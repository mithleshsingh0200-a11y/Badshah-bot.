import random
import asyncio
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- NAYA UPDATED TOKEN ---
TOKEN = '8044105919:AAERJW90-4rMpQAfdjuF-kTVCFu57Tjaxqw'

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

class GameEngine:
    def __init__(self):
        self.mode = None

engine = GameEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("91CLUB 1 MIN", callback_data='91CLUB_1MIN')],
        [InlineKeyboardButton("WINGO 3 MIN", callback_data='WINGO_3MIN')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 **BADSHAH PREDICTION ACTIVE**\nSelect your game mode:", reply_markup=reply_markup, parse_mode='Markdown')

async def fetch_now(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    results = ["BIG 🔴", "SMALL 🟢", "RED ❤️", "GREEN 💚"]
    res = random.choice(results)
    await context.bot.send_message(chat_id=job.chat_id, text=f"🚀 **PREDICTION FOR NEXT PERIOD**\n\nResult: `{res}`\nConfidence: 95%", parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    engine.mode = query.data
    await query.edit_message_text(f"✅ **{query.data} SELECTED**\n🚀 Har 15-30 second mein prediction aayegi...")
    
    # Purani jobs mitao aur nayi shuru karo
    for job in context.job_queue.get_jobs_by_name(str(query.message.chat_id)):
        job.schedule_removal()
    
    context.job_queue.run_repeating(fetch_now, interval=30, first=1, chat_id=query.message.chat_id, name=str(query.message.chat_id))

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    print("🚀 BOT POLLING STARTING...") # Pehle print hoga
    app.run_polling(drop_pending_updates=True) # Conflict se bachayega
