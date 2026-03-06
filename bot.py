import random
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Render ki Environment settings se token uthayega
TOKEN = os.environ.get('BOT_TOKEN')

# --- AAPKA HTML HEALTH CHECK SERVER ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # HTML Response jo Render ko 'Live' dikhayega
        html = "<html><body><h1>Bot Status: Active</h1></body></html>"
        self.wfile.write(bytes(html, "utf8"))
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# Bot Logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("91CLUB 1 MIN", callback_data='91CLUB_1MIN')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 **BADSHAH BOT READY**", reply_markup=reply_markup)

async def main():
    # Rocket message logs mein sabse pehle
    print("🚀 BOT POLLING STARTING...")
    
    # HTML Server start
    Thread(target=run_server, daemon=True).start()

    # Naya tarika jo 'RuntimeError' ko theek karega
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    async with app:
        await app.initialize()
        await app.start()
        print("✅ Bot is fully online!")
        await app.updater.start_polling(drop_pending_updates=True)
        # Bot ko zinda rakhne ke liye infinite loop
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
