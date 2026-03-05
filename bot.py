import random
import asyncio
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# CONFIG
TOKEN = '8044105919:AAHPya5KATSdB-NM7OFUvTidYGY3fdtJd70'

# Render Health Check (Taaki bot band na ho)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Live")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

class BadshahEngine:
    def __init__(self):
        self.last_period = None
        self.mode = "1" # 1 for 30s, 2 for 1m

    def get_data(self):
        try:
            # Naya Working API Link
            url = f"https://api.9987up.com/api/web/game/v1/wingo/last-result?gameId={self.mode}"
            data = requests.get(url).json()['data']
            return data['issueNumber'], int(data['number'])
        except: return None, None

engine = BadshahEngine()

async def auto_check(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    period, num = engine.get_data()
    
    if period and period != engine.last_period:
        engine.last_period = period
        next_p = str(int(period) + 1)
        res = "BIG 🔴" if random.random() > 0.5 else "SMALL 🟢"
        
        msg = f"👑 *BADSHAH PREDICTION*\n━━━━━━━━━━━━━━\n🆔 *NEXT:* `{next_p}`\n📊 *RESULT:* `{res}`\n━━━━━━━━━━━━━━"
        await context.bot.send_message(chat_id, msg, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎮 30S MODE", callback_data='1')]]
    await update.message.reply_text("✅ *BADSHAH AI ACTIVE*\nMode chunein:", 
                                  parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    engine.mode = query.data
    await query.edit_message_text("🚀 *PREDICTION STARTING...*\nAgli prediction 30s mein aayegi.")
    context.job_queue.run_repeating(auto_check, interval=30, first=1, chat_id=query.message.chat_id)

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()
