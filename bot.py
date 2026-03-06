import random
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- APKA NAYA TOKEN ---
TOKEN = '8044105919:AAERJW90-4rMpQAfdjuF-kTVCFu57Tjaxqw'

# Render ke liye Health Check Server
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

# Prediction Logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("91CLUB 1 MIN", callback_data='91CLUB_1MIN')],
        [InlineKeyboardButton("WINGO 3 MIN", callback_data='WINGO_3MIN')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 **BADSHAH PREDICTION BOT**\nSelect your game:", reply_markup=reply_markup, parse_mode='Markdown')

async def send_prediction(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    results = ["BIG 🔴", "SMALL 🟢", "RED ❤️", "GREEN 💚"]
    res = random.choice(results)
    await context.bot.send_message(chat_id=job.chat_id, text=f"🚀 **NEXT PERIOD PREDICTION**\n\nResult: `{res}`\nAccuracy: 98%", parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"✅ **{query.data} SELECTED**\n🚀 Har 30 second mein prediction shuru ho rahi hai...")
    
    # Purani jobs hatao aur naya timer shuru karo
    chat_id = query.message.chat_id
    for current_job in context.job_queue.get_jobs_by_name(str(chat_id)):
        current_job.schedule_removal()
    
    context.job_queue.run_repeating(send_prediction, interval=30, first=5, chat_id=chat_id, name=str(chat_id))

if __name__ == '__main__':
    # 1. Server start (Render ke liye zaroori)
    Thread(target=run_server, daemon=True).start()
    
    # 2. Bot start sequence
    print("🚀 BOT POLLING STARTING...") # Pehle ye print hoga
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    # 3. Connection (drop_pending_updates=True conflict se bachata hai)
    app.run_polling(drop_pending_updates=True)
