import random
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Render ki Environment settings se token uthayega
TOKEN = os.environ.get('BOT_TOKEN')

# --- AAPKA HTML HEALTH CHECK SERVER ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        # Ye Render ko '200 OK' bhejta hai taaki wo 'Live' dikhaye
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = "<html><body><h1>Bot is Running!</h1></body></html>"
        self.wfile.write(bytes(html, "utf8"))

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    # Render ke PORT par server chalata hai
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    print(f"✅ HTML Server started on port {port}")
    server.serve_forever()
# --------------------------------------

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("91CLUB 1 MIN", callback_data='91CLUB_1MIN')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 **BADSHAH BOT READY**\nClick start for prediction.", reply_markup=reply_markup)

if __name__ == '__main__':
    # Rocket message logs mein sabse pehle aayega
    print("🚀 BOT POLLING STARTING...") 
    
    # HTML Server ko background mein chalata hai
    Thread(target=run_server, daemon=True).start()
    
    # Bot Initialization
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN not found in Environment Variables!")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        
        # Conflict aur Loop errors ko khatam karta hai
        app.run_polling(drop_pending_updates=True)
