import random
import asyncio
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- CONFIG (Aapka Token) ---
TOKEN = '8044105919:AAEq2H7ZVtIxQ3nRN_Gro5xvGzsWTXciRtc'

# Render Health Check (Isse bot hamesha 'Live' rahega)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Active")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

class BadshahEngine:
    def __init__(self):
        self.last_period = None
        self.mode = "WinGo_30S"
        self.current_lvl = 1
        self.prev_pred = None

    def get_color(self, n):
        n = int(n)
        if n == 0: return "🔴🟣 (Red-Violet)"
        if n == 5: return "🟢🟣 (Green-Violet)"
        return "🔴 (Red)" if n % 2 == 0 else "🟢 (Green)"

    async def fetch_and_predict(self, context, chat_id):
        try:
            # Latest API Link for 9987up/Lottery
            url = f"https://api.9987up.com/api/web/game/v1/wingo/last-result?gameId={'1' if '30S' in self.mode else '2'}"
            resp = requests.get(url, timeout=10).json()['data']
            curr_period = resp['issueNumber']
            
            # Check Result of previous turn
            if self.last_period and curr_period != self.last_period:
                actual_num = int(resp['number'])
                actual_res = "BIG" if actual_num >= 5 else "SMALL"
                if self.prev_pred == actual_res:
                    self.current_lvl = 1
                    await context.bot.send_message(chat_id, "💰 **WINNING!!** ✅🤑")
                else:
                    self.current_lvl = 2
                    await context.bot.send_message(chat_id, "🔻 **LOSS** ❌⚠️\n🔄 Recovery Level 2 Start!")

            # Prediction Logic
            self.last_period = curr_period
            next_p = str(int(curr_period) + 1)
            prediction = "BIG" if random.random() > 0.5 else "SMALL"
            self.prev_pred = prediction
            
            jackpot = random.choice(range(5, 10) if prediction == "BIG" else range(0, 5))
            color = self.get_color(jackpot)

            msg = (f"👑 *BADSHAH KING AI V33*\n"
                   f"━━━━━━━━━━━━━━━━━━\n"
                   f"🕒 *MODE:* {'30S' if '30S' in self.mode else '60S'}\n"
                   f"🆔 *NEXT PERIOD:* `{next_p}`\n"
                   f"📏 *SIZE:* `{prediction}`\n"
                   f"🎰 *JACKPOT:* `{jackpot}`\n"
                   f"🎨 *COLOR:* {color}\n"
                   f"⚠️ *LEVEL:* {self.current_lvl}\n"
                   f"━━━━━━━━━━━━━━━━━━")
            await context.bot.send_message(chat_id, msg, parse_mode='Markdown')
        except Exception as e:
            print(f"API Error: {e}")

engine = BadshahEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 30S MODE", callback_data='WinGo_30S')],
                [InlineKeyboardButton("🎮 60S MODE", callback_data='WinGo_1M')]]
    await update.message.reply_text("👑 *BADSHAH AI V33*\nChoose Game Mode:", 
                                  parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    engine.mode = query.data
    interval = 30 if "30S" in query.data else 60
    await query.edit_message_text(f"✅ *{engine.mode} SELECTED*\n🚀 Prediction chalu...")
    for job in context.job_queue.get_jobs_by_name(str(query.message.chat_id)): job.schedule_removal()
    context.job_queue.run_repeating(engine.fetch_and_predict, interval=interval, first=1, chat_id=query.message.chat_id, name=str(query.message.chat_id))

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()
