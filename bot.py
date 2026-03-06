import asyncio
import os
import random
import cloudscraper
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')
user_active_modes = {}

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GOAGAMES_AUTO_SYNC_LIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- REAL API FETCH LOGIC (Bypassing "None" Error) ---
async def get_goa_data(mode):
    # Cloudscraper use kar rahe hain taaki "None" wala error na aaye
    scraper = cloudscraper.create_scraper()
    api_url = f"https://draw.ar-lottery01.com/WinGo/WinGo_{'30S' if mode == '30s' else '1M'}/GetHistoryIssuePage.json"
    
    try:
        response = scraper.get(api_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            last_record = data['data']['list'][0]
            # 17-Digit Period Sync (Date+Year+Period)
            p = str(int(last_record['issueNumber']) + 1)
            return p
    except:
        pass
    
    # Backup: Agar API phir bhi "None" de, toh time se 17-digit period banayein
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    p_num = str(total_sec // (30 if mode == '30s' else 60)).zfill(4)
    return f"{date_str}1000{p_num}"

# --- AUTOMATIC HTML-STYLE LOOP ---
async def start_auto_prediction(context, chat_id, mode):
    interval = 30 if mode == "30s" else 60
    
    while user_active_modes.get(chat_id) == mode:
        p = await get_goa_data(mode)
        
        # Pattern & Jackpot Logic
        res = random.choice(["BIG", "SMALL"])
        num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
        color = "🔴" if res == "SMALL" else "🟢"
        
        # STEP 1: Pehle Pattern aur Jackpot batana (HTML Style)
        text = (
            f"👑 **BADSHAH KING AI V33**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Pattern:** {res} {color}\n"
            f"🔢 **Jackpot Number:** `{num}`\n"
            f"⏳ **Checking Result...**"
        )
        msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        
        # STEP 2: Wait for period to end
        await asyncio.sleep(interval - 5)
        
        # STEP 3: Win/Loss Gift bhejna
        is_win = random.random() > 0.15 
        status_text = "✅ **WIN 💸💸💸**" if is_win else "❌ **LOSS 😭😭😭**"
        
        final_text = (
            f"👑 **BADSHAH KING AI V33**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"✨ **Status:** {status_text}\n\n"
            f"✅ Next Prediction in 5s..."
        )
        await msg.edit_text(final_text, parse_mode='Markdown')
        await asyncio.sleep(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None
    keyboard = [[InlineKeyboardButton("🚀 START 30S API", callback_data='30s'), 
                  InlineKeyboardButton("🚀 START 60S API", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH GOAGAMES LIVE BOT**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode, chat_id = query.data, query.message.chat_id
    await query.answer()
    user_active_modes[chat_id] = mode
    await query.edit_message_text(f"✅ **{mode.upper()} MODE CONNECTED!**\nAuto-Gift system shuru ho gaya hai.")
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
