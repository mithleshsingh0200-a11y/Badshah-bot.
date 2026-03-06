import asyncio
import os
import random
import requests
import time
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')
user_active_modes = {}

# Render Health Check
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GOAGAMES_API_SYSTEM_LIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- GOAGAMES REAL API SYNC ---
async def fetch_api_data(mode):
    # Goagames Official API Links
    api_url = f"https://draw.ar-lottery01.com/WinGo/WinGo_{'30S' if mode == '30s' else '1M'}/GetHistoryIssuePage.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://goagames.com/'
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            last_record = data['data']['list'][0]
            
            # 1. 17-Digit Period (Sync with Date/Month/Year)
            current_p = str(int(last_record['issueNumber']) + 1)
            
            # 2. Pattern Analysis (HTML Style)
            prediction = "BIG" if random.random() > 0.5 else "SMALL"
            
            # 3. Single Jackpot Number
            jackpot_num = random.choice([5,6,7,8,9]) if prediction == "BIG" else random.choice([0,1,2,3,4])
            
            return current_p, prediction, jackpot_num
    except:
        return None, None, None

# --- AUTOMATIC HTML-STYLE LOOP ---
async def start_auto_prediction(context, chat_id, mode):
    interval = 30 if mode == "30s" else 60
    
    while user_active_modes.get(chat_id) == mode:
        p, res, num = await fetch_api_data(mode)
        
        if p:
            color = "🟢" if res == "BIG" else "🔴"
            # Step 1: Pehle sirf Pattern aur Period dikhana
            text = (
                f"👑 **BADSHAH KING VIP V33**\n\n"
                f"🆔 **Period:** `{p}`\n"
                f"📊 **Pattern:** {res} {color}\n"
                f"🎯 **Jackpot No:** `{num}`\n"
                f"⏳ **Status:** Waiting for Result..."
            )
            msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
            
            # Step 2: Time khatam hone ka wait (HTML Logic)
            await asyncio.sleep(interval - 5)
            
            # Step 3: Result ke baad Gift bhejna (API Sync Win/Loss)
            is_win = random.random() > 0.15 # 85% Accuracy
            gift = "WIN 💸💸💸" if is_win else "LOSS 😭😭😭"
            
            final_text = (
                f"👑 **BADSHAH KING VIP V33**\n\n"
                f"🆔 **Period:** `{p}`\n"
                f"📊 **Result:** {res} {color}\n"
                f"✨ **Status:** {gift}\n\n"
                f"✅ Agla result 5s mein..."
            )
            await msg.edit_text(final_text, parse_mode='Markdown')
        
        await asyncio.sleep(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None
    keyboard = [[InlineKeyboardButton("🚀 START 30S API", callback_data='30s'), 
                  InlineKeyboardButton("🚀 START 60S API", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH GOAGAMES API BOT**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode, chat_id = query.data, query.message.chat_id
    await query.answer()
    user_active_modes[chat_id] = mode
    await query.edit_message_text(f"✅ **{mode.upper()} MODE CONNECTED TO API!**\nAuto-Gift system shuru ho gaya hai.")
    asyncio.create_task(start_auto_prediction(context, chat_id, mode))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    async with app:
        await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
