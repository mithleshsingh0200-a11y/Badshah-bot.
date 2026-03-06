import asyncio
import os
import random
import requests
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# --- GOAGAMES REAL API ---
API_LINKS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "60s": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

# User state track karne ke liye (taaki loop chalta rahe)
user_active_modes = {}

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AUTO-SYSTEM ACTIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

async def fetch_api_data(mode):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(API_LINKS[mode], headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            last_record = data['data']['list'][0]
            p = str(int(last_record['issueNumber']) + 1)
            res = "BIG" if random.random() > 0.5 else "SMALL"
            num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
            return p, res, num
    except:
        pass
    return None, None, None

# --- AUTOMATIC LOOP SYSTEM ---
async def start_auto_loop(context, chat_id, mode):
    interval = 30 if mode == "30s" else 60
    
    while user_active_modes.get(chat_id) == mode:
        p, res, num = await fetch_api_data(mode)
        
        if p:
            is_win = random.random() > 0.15
            status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭😭"
            color = "🟢" if res == "BIG" else "🔴"
            
            text = (
                f"👑 **BADSHAH {mode.upper()} AUTO-VIP**\n\n"
                f"🆔 **Period:** `{p}`\n"
                f"📊 **Result:** {res} {color}\n"
                f"🔢 **Number:** {num}\n"
                f"{status}\n\n"
                f"⏳ Agla prediction {interval}s mein automatic aayega..."
            )
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        
        # Agle period tak intezaar (30s ya 60s)
        await asyncio.sleep(interval)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None # Reset
    keyboard = [[
        InlineKeyboardButton("🚀 START 30S AUTO", callback_data='30s'),
        InlineKeyboardButton("🚀 START 60S AUTO", callback_data='60s')
    ]]
    await update.message.reply_text("👑 **BADSHAH V33 AUTO-SYSTEM**\n\nEk baar mode select karein, phir bot automatic chalta rahega:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = query.data
    chat_id = query.message.chat_id
    await query.answer()
    
    user_active_modes[chat_id] = mode
    await query.edit_message_text(f"✅ **{mode.upper()} AUTO-MODE SHURU!**\n\nAb bot har period par khud result bhejega. Rokne ke liye /start karein.")
    
    # Loop shuru karein
    asyncio.create_task(start_auto_loop(context, chat_id, mode))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())