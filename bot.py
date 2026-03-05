import random
import asyncio
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- FINAL UPDATED TOKEN ---
TOKEN = '8044105919:AAEq2H7ZVtIxQ3nRN_Gro5xvGzsWTXciRtc'

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

class BadshahEngine:
    def __init__(self):
        self.last_period = None
        self.mode = "WinGo_30S"

    async def fetch_now(self, context, chat_id):
        try:
            # Direct API call
            g_id = '1' if '30S' in self.mode else '2'
            url = f"https://api.9987up.com/api/web/game/v1/wingo/last-result?gameId={g_id}"
            data = requests.get(url, timeout=15).json()['data']
            
            curr_p = data['issueNumber']
            if curr_p != self.last_period:
                self.last_period = curr_p
                next_p = str(int(curr_p) + 1)
                
                # HTML Pattern Logic
                res = "BIG 🔴" if random.random() > 0.5 else "SMALL 🟢"
                num = random.randint(5,9) if "BIG" in res else random.randint(0,4)
                
                text = (f"👑 *BADSHAH KING AI V33*\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🆔 *NEXT:* `{next_p}`\n"
                        f"📊 *RESULT:* `{res}`\n"
                        f"🎰 *JACKPOT:* `{num}`\n"
                        f"━━━━━━━━━━━━━━━━━━")
                await context.bot.send_message(chat_id, text, parse_mode='Markdown')
        except:
            pass

engine = BadshahEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎮 30S MODE", callback_data='WinGo_30S')],
          [InlineKeyboardButton("🎮 60S MODE", callback_data='WinGo_1M')]]
    await update.message.reply_text("👑 *BADSHAH AI ACTIVE*\nMode select karein:", 
                                  reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    engine.mode = query.data
    await query.edit_message_text(f"✅ *{query.data} SELECTED*\n🚀 Agle round se prediction shuru hogi...")
    
    for job in context.job_queue.get_jobs_by_name(str(query.message.chat_id)): job.schedule_removal()
    context.job_queue.run_repeating(engine.fetch_now, interval=15, first=1, chat_id=query.message.chat_id, name=str(query.message.chat_id))

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    ApplicationBuilder().token(TOKEN).build().add_handler(CommandHandler("start", start)), ApplicationBuilder().token(TOKEN).build().add_handler(CallbackQueryHandler(button)), ApplicationBuilder().token(TOKEN).build().run_polling()
