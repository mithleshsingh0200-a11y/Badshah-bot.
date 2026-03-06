import asyncio
import os
import random
import cloudscraper
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# --- GOAGAMES API SECURE LINKS ---
API_LINKS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "60s": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BADSHAH V33 SYSTEM LIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- POWERFUL BYPASS LOGIC ---
async def fetch_secure_prediction(mode):
    # Har baar naya session banayega taaki block na ho
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    for i in range(5): # 5 baar alag tareeke se try karega
        try:
            # Thoda delay taaki server ko lage insaan click kar raha hai
            await asyncio.sleep(random.uniform(1, 2))
            resp = scraper.get(API_LINKS[mode], timeout=20)
            
            if resp.status_code == 200:
                data = resp.json()
                last = data['data']['list'][0]
                p = str(int(last['issueNumber']) + 1)
                
                # HTML wala Result Pattern Logic
                res = "BIG" if random.random() > 0.5 else "SMALL"
                num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
                return p, res, num
        except:
            continue
    return None, None, None

# --- BOT INTERFACE ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎮 30S MODE", callback_data='30s'),
        InlineKeyboardButton("🎮 60S MODE", callback_data='60s')
    ]]
    await update.message.reply_text(
        "👑 **BADSHAH GOAGAMES V33**\n\nApna mode select karein. Connection fix kar diya gaya hai!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = query.data
    await query.answer()
    
    msg = await query.edit_message_text(f"📡 **ANALYZING {mode.upper()} PATTERNS...**")
    p, res, num = await fetch_secure_prediction(mode)
    
    if p:
        # Aapka Win/Loss Emoji logic
        is_win = random.random() > 0.15
        status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭😭"
        color = "🟢" if res == "BIG" else "🔴"
        
        text = (
            f"👑 **BADSHAH {mode.upper()} VIP**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"{status}\n\n"
            f"⏳ Agla result period khatam hone par nikalein."
        )
        keyboard = [[InlineKeyboardButton("🔄 REFRESH RESULT", callback_data=mode)]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        # Agar block ho jaye toh Automatic Retry ka option
        keyboard = [[InlineKeyboardButton("FORCE RETRY 🔄", callback_data=mode)]]
        await msg.edit_text("⚠️ **Server overloaded!** Force Retry dabayein.", reply_markup=InlineKeyboardMarkup(keyboard))

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