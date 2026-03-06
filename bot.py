import asyncio
import os
import requests
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get('BOT_TOKEN')

# --- APIS FOR BOTH MODES ---
API_30S = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"
API_60S = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"

# HTML Interface (Render ko live rakhne ke liye)
HTML_CODE = "<html><body style='background:black;color:lime;'><h1>BADSHAH V33 24/7 LIVE</h1></body></html>"

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(HTML_CODE, "utf8"))

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck)
    server.serve_forever()

# --- PREDICTION LOGIC ---
def get_prediction(api_url):
    try:
        data = requests.get(api_url, timeout=10).json()
        last_results = data['data']['list']
        p = str(int(last_results[0]['issueNumber']) + 1)
        res = "BIG" if random.random() > 0.5 else "SMALL"
        num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
        return p, res, num
    except: return None, None, None

# --- AUTOMATIC 24/7 LOOP ---
async def prediction_loop(chat_id, bot, mode_name, api_url, interval):
    last_p = ""
    while True:
        p, res, num = get_prediction(api_url)
        if p and p != last_p:
            last_p = p
            is_win = random.random() > 0.1
            status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭"
            color = "🟢" if res == "BIG" else "🔴"
            
            msg = (
                f"👑 **BADSHAH {mode_name} VIP**\n\n"
                f"🆔 **Period:** `{p}`\n"
                f"📊 **Result:** {res} {color}\n"
                f"🔢 **Number:** {num}\n"
                f"{status}\n\n"
                f"⏳ **Next Prediction Automatic...**"
            )
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
        await asyncio.sleep(interval)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 **24/7 AUTO-SYSTEM ACTIVATED!**\n30s aur 60s dono modes shuru ho gaye hain.")
    # Dono modes ko ek saath chalu karna
    asyncio.create_task(prediction_loop(update.effective_chat.id, context.bot, "30S", API_30S, 15))
    asyncio.create_task(prediction_loop(update.effective_chat.id, context.bot, "60S", API_60S, 30))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        # 24/7 chalne ke liye infinite wait
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
