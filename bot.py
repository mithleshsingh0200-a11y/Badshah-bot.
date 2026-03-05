import random
import asyncio
import requests
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# --- AAPKA TOKEN YAHAN HAI ---
TOKEN = '8044105919:AAHPya5KATSdB-NM7OFUvTidYGY3fdtJd70'

# Render Port Fix (Taaki bot band na ho)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Badshah AI Live")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

class BadshahEngine:
    def __init__(self):
        self.last_period = None
        self.mode = "WinGo_30S"
        self.current_lvl = 1
        self.prev_pred = None

    def get_color_emoji(self, n):
        n = int(n)
        if n == 0: return "🔴🟣 (Red-Violet)"
        if n == 5: return "🟢🟣 (Green-Violet)"
        return "🔴 (Red)" if n % 2 == 0 else "🟢 (Green)"

    def analyze_patterns(self, api_list):
        trend = [("BIG" if int(x['number']) >= 5 else "SMALL") for x in api_list[:5]]
        if trend[0] == trend[1] == trend[2]:
            pat, res = "DRAGON MODE 🐉", trend[0]
        elif trend[0] != trend[1] and trend[1] != trend[2]:
            pat, res = "ZIG-ZAG 1-1 📈", ("SMALL" if trend[0] == "BIG" else "BIG")
        else:
            pat, res = "CHIP MARKET SCAN 🤖", ("BIG" if int(api_list[0]['number']) % 2 == 0 else "SMALL")
        
        if self.current_lvl == 2:
            res = "SMALL" if res == "BIG" else "BIG"
        return pat, res

    async def fetch_and_predict(self, context, chat_id):
        try:
            url = f"https://draw.ar-lottery01.com/WinGo/{self.mode}/GetHistoryIssuePage.json"
            data = requests.get(url, timeout=10).json()['data']['list']
            curr_row = data[0]
            curr_period = curr_row['issueNumber']
            
            if self.last_period and curr_period != self.last_period:
                actual_num = int(curr_row['number'])
                actual_res = "BIG" if actual_num >= 5 else "SMALL"
                if self.prev_pred == actual_res:
                    self.current_lvl = 1
                    await context.bot.send_message(chat_id, "💰 **WINNING!!** ✅🤑")
                else:
                    self.current_lvl = 2
                    await context.bot.send_message(chat_id, "🔻 **LOSS** ❌⚠️\n🔄 Recovery Level 2 Start!")

            self.last_period = curr_period
            next_p = str(int(curr_period) + 1)
            pattern, prediction = self.analyze_patterns(data)
            self.prev_pred = prediction
            
            jackpot_num = random.choice(range(5, 10) if prediction == "BIG" else range(0, 5))
            color = self.get_color_emoji(jackpot_num)

            msg = (f"👑 *BADSHAH KING AI V33*\n"
                   f"━━━━━━━━━━━━━━━━━━\n"
                   f"🕒 *MODE:* {'30S' if '30S' in self.mode else '60S'}\n"
                   f"🆔 *NEXT PERIOD:* `{next_p}`\n"
                   f"📊 *PATTERN:* {pattern}\n"
                   f"📏 *SIZE:* `{prediction}`\n"
                   f"🎰 *JACKPOT:* `{jackpot_num}`\n"
                   f"🎨 *COLOR:* {color}\n"
                   f"⚠️ *LEVEL:* {self.current_lvl}\n"
                   f"━━━━━━━━━━━━━━━━━━")
            await context.bot.send_message(chat_id, msg, parse_mode='Markdown')
        except: pass

engine = BadshahEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 30S MODE", callback_data='WinGo_30S')],
                [InlineKeyboardButton("🎮 60S MODE", callback_data='WinGo_1M')]]
    await update.message.reply_text("👑 *WELCOME TO BADSHAH KING AI*\nMode chunein:", 
                                  parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
