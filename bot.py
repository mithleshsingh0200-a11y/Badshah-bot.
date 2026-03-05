import random
import asyncio
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# CONFIG (Aapka Naya Token)
TOKEN = '8044105919:AAHPya5KATSdB-NM7OFUvTidYGY3fdtJd70'

class BadshahEngine:
    def __init__(self):
        self.last_period = None
        self.current_lvl = 1
        self.my_pred = None
        self.mode = "WinGo_30S"

    def get_prediction(self):
        patterns = ["DRAGON 🐉", "ZIG-ZAG 📈", "DOUBLE MIRROR 🪞", "CHIP MARKET 🤖"]
        pat = random.choice(patterns)
        res = random.choice(["BIG", "SMALL"])
        if self.current_lvl == 2:
            res = "SMALL" if res == "BIG" else "BIG"
        self.my_pred = res
        return pat, res

engine = BadshahEngine()

async def auto_check(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    try:
        url = f"https://draw.ar-lottery01.com/WinGo/{engine.mode}/GetHistoryIssuePage.json"
        response = requests.get(url).json()
        latest_data = response['data']['list'][0]
        curr_period = latest_data['issueNumber']
        actual_num = int(latest_data['number'])
        actual_res = "BIG" if actual_num >= 5 else "SMALL"

        if engine.last_period and curr_period != engine.last_period:
            if engine.my_pred == actual_res:
                engine.current_lvl = 1
                await context.bot.send_message(chat_id, "💰 **WINNING!!** 💰\n✅ **WINNING SECURED!** 🤑")
            else:
                engine.current_lvl = 2
                await context.bot.send_message(chat_id, "🔻 **LOSS DETECTED** 🔻\n⚠️ **LEVEL 2 RECOVERY START!** 📉")

        next_p = str(int(curr_period) + 1)
        pat, pred = engine.get_prediction()
        engine.last_period = next_p
        
        mode_label = "30S" if "30S" in engine.mode else "1M"
        msg = f"👑 *BADSHAH KING AI V33*\n━━━━━━━━━━━━━━━━━━\n🕒 *MODE:* {mode_label}\n🆔 *NEXT PERIOD:* `{next_p}`\n📊 *PATTERN:* {pat}\n📏 *PREDICTION:* `{pred}`\n⚠️ *LEVEL:* {engine.current_lvl}\n━━━━━━━━━━━━━━━━━━"
        await context.bot.send_message(chat_id, msg, parse_mode='Markdown')
    except Exception as e:
        print(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 'callback_data' use karna hai, callback_query_data nahi
    keyboard = [
        [InlineKeyboardButton("🎮 30S MODE", callback_data='mode_30s')],
        [InlineKeyboardButton("🎮 1M MODE", callback_data='mode_1m')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👑 *WELCOME TO BADSHAH KING AI*\n\nNiche diye gaye buttons se apna game mode chunein:", 
                                  parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    engine.mode = "WinGo_30S" if query.data == 'mode_30s' else "WinGo_1M"
    interval = 35 if query.data == 'mode_30s' else 65
    await query.edit_message_text(f"✅ **{engine.mode.replace('_', ' ')} SELECTED**\n🚀 Automatic prediction shuru ho rahi hai...")
    for job in context.job_queue.get_jobs_by_name(str(query.message.chat_id)):
        job.schedule_removal()
    context.job_queue.run_repeating(auto_check, interval=interval, first=1, chat_id=query.message.chat_id, name=str(query.message.chat_id))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
