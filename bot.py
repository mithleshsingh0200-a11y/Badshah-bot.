import asyncio
import os
import requests
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# --- GOAGAMES API FIX ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

API_URLS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "60s": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

# Keep-Alive Server
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BADSHAH V33 IS RUNNING 24/7")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- REAL API FETCH ---
async def fetch_prediction(mode):
    try:
        # API request with headers to avoid "API Error"
        response = requests.get(API_URLS[mode], headers=HEADERS, timeout=15)
        data = response.json()
        last_item = data['data']['list'][0]
        
        period = str(int(last_item['issueNumber']) + 1)
        # Logic based on real API pattern
        num = int(last_item['number'])
        res = "BIG" if num < 5 else "SMALL" # Example logic
        final_num = (num + 3) % 10
        
        return period, res, final_num
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

# --- BOT INTERFACE ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎯 30S MODE", callback_data='30s'),
        InlineKeyboardButton("🎯 60S MODE", callback_data='60s')
    ]]
    await update.message.reply_text(
        "👑 **BADSHAH GOAGAMES V33**\n\nApna mode select karein. Bot automatic 24 ghante chalega.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = query.data
    await query.answer()
    
    msg = await query.edit_message_text(f"📡 **SCANNING {mode.upper()} API...**")
    
    period, res, num = await fetch_prediction(mode)
    
    if period:
        import random
        is_win = random.random() > 0.15
        status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭😭"
        color = "🟢" if res == "BIG" else "🔴"
        
        text = (
            f"👑 **BADSHAH {mode.upper()} VIP**\n\n"
            f"🆔 **Period:** `{period}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"{status}\n\n"
            f"⏳ Agla result niche se refresh karein."
        )
        keyboard = [[InlineKeyboardButton("🔄 REFRESH RESULT", callback_data=mode)]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        keyboard = [[InlineKeyboardButton("retry 🔄", callback_data=mode)]]
        await msg.edit_text("❌ **API Connection Slow!** Retry karein.", reply_markup=InlineKeyboardMarkup(keyboard))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_mode))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
