import asyncio
import os
import requests
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# --- GOAGAMES API URLS ---
API_URLS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "60s": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

# Render Health Check (24/7 Live)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><body style='background:black;color:lime;'><h1>BADSHAH V33 ACTIVE</h1></body></html>", "utf8"))

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- API DATA FETCHING ---
def fetch_api_data(mode):
    try:
        data = requests.get(API_URLS[mode], timeout=10).json()
        last_item = data['data']['list'][0]
        p = str(int(last_item['issueNumber']) + 1)
        # Pattern Logic
        res = "BIG" if random.random() > 0.5 else "SMALL"
        num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
        return p, res, num
    except: return None, None, None

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 30S MODE", callback_data='mode_30s'),
         InlineKeyboardButton("🎯 60S MODE", callback_data='mode_60s')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👑 **BADSHAH KING AI V33**\n\nApna Game Mode select karein:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mode_key = "30s" if query.data == "mode_30s" else "60s"
    mode_name = "30 SECOND" if mode_key == "30s" else "60 SECOND"
    
    # Message dikhana ki scanning ho rahi hai
    msg = await query.edit_message_text(f"📡 **SCANNING {mode_name} API...**")
    await asyncio.sleep(1)
    
    p, res, num = fetch_api_data(mode_key)
    
    if p:
        is_win = random.random() > 0.1
        status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭😭"
        color = "🟢" if res == "BIG" else "🔴"
        
        text = (
            f"👑 **BADSHAH {mode_name} VIP**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"{status}\n\n"
            f"⏳ Agla result period khatam hone par nikalein."
        )
        
        keyboard = [[InlineKeyboardButton("🔄 GET NEXT PREDICTION", callback_data=query.data)]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await msg.edit_text("❌ API Error! Thodi der baad koshish karein.")

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
