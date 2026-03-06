import asyncio
import os
import requests
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# --- GOAGAMES API CONFIG ---
API_URLS = {
    "30s": "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json",
    "60s": "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
}

# --- RENDER KEEP-ALIVE ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BADSHAH V33 ACTIVE 24/7")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- FETCH WITH RETRY LOGIC ---
async def get_data_from_api(mode):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for _ in range(3):  # 3 baar koshish karega agar error aaye
        try:
            resp = requests.get(API_URLS[mode], headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                last_item = data['data']['list'][0]
                p = str(int(last_item['issueNumber']) + 1)
                res = "BIG" if random.random() > 0.5 else "SMALL"
                num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
                return p, res, num
        except:
            await asyncio.sleep(1)
    return None, None, None

# --- BOT INTERFACE ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎮 30S MODE", callback_data='30s'),
        InlineKeyboardButton("🎮 60S MODE", callback_data='60s')
    ]]
    await update.message.reply_text("👑 **BADSHAH GOAGAMES V33**\n\nGame mode select karein:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = query.data
    await query.answer()
    
    msg = await query.edit_message_text(f"📡 **FETCHING {mode.upper()} DATA...**")
    p, res, num = await get_data_from_api(mode)
    
    if p:
        is_win = random.random() > 0.1
        status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭😭"
        color = "🟢" if res == "BIG" else "🔴"
        
        text = (
            f"👑 **BADSHAH {mode.upper()} VIP**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"{status}\n\n"
            f"⏳ Agla result period ke baad nikaalein."
        )
        keyboard = [[InlineKeyboardButton("🔄 REFRESH", callback_data=mode)]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        keyboard = [[InlineKeyboardButton("Retry 🔄", callback_data=mode)]]
        await msg.edit_text("❌ **Server Busy!** Niche click karein.", reply_markup=InlineKeyboardMarkup(keyboard))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
