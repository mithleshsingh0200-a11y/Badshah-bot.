import random
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- APKA NAYA TOKEN ---
TOKEN = os.environ.get('BOT_TOKEN')

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("91CLUB 1 MIN", callback_data='91CLUB_1MIN')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 **BADSHAH BOT ACTIVE**", reply_markup=reply_markup)

if __name__ == '__main__':
    # Rocket message sabse pehle taaki logs mein turant dikhe
    print("🚀 BOT POLLING STARTING...") 
    
    Thread(target=run_server, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    # drop_pending_updates=True conflict error ko khatam karta hai
    app.run_polling(drop_pending_updates=True)
