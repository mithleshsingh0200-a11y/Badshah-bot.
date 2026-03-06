import asyncio
import os
import requests
import random
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# --- GOAGAMES API LINKS ---
API_LINKS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "60s": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

# Render ko 24 ghante jagaye rakhne ke liye
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BADSHAH V33 SYSTEM LIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- API FETCH WITH ERROR FIX ---
async def get_goa_data(mode):
    # Bot ko insaan ki tarah dikhane ke liye headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://goagames.com/'
    }
    try:
        response = requests.get(API_LINKS[mode], headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            last_record = data['data']['list'][0]
            # Agla Period Calculation
            p = str(int(last_record['issueNumber']) + 1)
            # Result Logic (Win/Loss Simulation)
            res = "BIG" if random.random() > 0.5 else "SMALL"
            num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
            return p, res, num
    except Exception as e:
        print(f"Error: {e}")
    return None, None, None

# --- BOT INTERFACE & SWITCHING ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎯 30S MODE", callback_data='30s'),
        InlineKeyboardButton("🎯 60S MODE", callback_data='60s')
    ]]
    await update.message.reply_text(
        "👑 **BADSHAH GOAGAMES V33**\n\nApna game mode select karein. Bot automatic 24 ghante chalega.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = query.data
    await query.answer()
    
    msg = await query.edit_message_text(f"📡 **SCANNING {mode.upper()} PATTERNS...**")
    
    # API se data fetch karna
    p, res, num = await get_goa_data(mode)
    
    if p:
        # Win/Loss Emojis as per your demand
        is_win = random.random() > 0.15
        if is_win:
            status_text = "✨ STATUS: WIN 💸💸💸"
            footer = "✅ ANALYSIS CONFIRMED"
        else:
            status_text = "✨ STATUS: LOSS 😭😭😭"
            footer = "❌ ANALYSIS FAILED"
            
        color = "🟢" if res == "BIG" else "🔴"
        
        text = (
            f"👑 **BADSHAH {mode.upper()} VIP**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"{status_text}\n\n"
            f"🏆 **{footer}**\n"
            f"⏳ Agla result period ke baad refresh karein."
        )
        keyboard = [[InlineKeyboardButton("🔄 REFRESH RESULT", callback_data=mode)]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        # Retry Button agar API busy ho
        keyboard = [[InlineKeyboardButton("RETRY 🔄", callback_data=mode)]]
        await msg.edit_text("⚠️ **Server Busy!** Please retry karein.", reply_markup=InlineKeyboardMarkup(keyboard))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_choice))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
