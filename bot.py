import random
import asyncio
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# CONFIG
TOKEN = '8044105919:AAG889Nvestlcj_3m5MwDaYYc5oplzAHT28'

class BadshahEngine:
    def __init__(self):
        self.last_period = None
        self.current_lvl = 1
        self.my_pred = None
        self.mode = "WinGo_30S" # Default

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
                # Win Sticker ID yahan dalein
                # await context.bot.send_sticker(chat_id, "STICKER_ID") 
            else:
                engine.current_lvl = 2
                await context.bot.send_message(chat_id, "🔻 **LOSS DETECTED** 🔻\n⚠️ **LEVEL 2 RECOVERY START!** 📉")
                # Loss Sticker ID yahan dalein
                # await context.bot.send_sticker(chat_id, "STICKER_ID")

        next_p = str(int(curr_period) + 1)
        pat, pred = engine.get_prediction()
        engine.last_period = next_p
        
        mode_label = "30S" if engine.mode == "WinGo_30S" else "1M"
        msg = (
            f"👑 *BADSHAH KING AI V33*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 *MODE:* {mode_label}\n"
            f"🆔 *NEXT PERIOD:* `{next_p}`\n"
            f"📊 *PATTERN:* {pat}\n"
            f"📏 *PREDICTION:* `{pred}`\n"
            f"⚠️ *LEVEL:* {engine.current_lvl}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        await context.bot.send_message(chat_id, msg, parse_mode='Markdown')

    except Exception as e:
        print(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 30S MODE", callback_query_data='mode_30s')],
        [InlineKeyboardButton("🎮 1M MODE", callback_query_data='mode_1m')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👑 *WELCOME TO BADSHAH KING AI*\n\nNiche diye gaye buttons se apna game mode chunein:", 
                                  parse_mode='Markdown', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'mode_30s':
        engine.mode = "WinGo_30S"
        interval = 35
    else:
        engine.mode = "WinGo_1M"
        interval = 65

    await query.edit_message_text(f"✅ **{engine.mode.replace('_', ' ')} SELECTED**\n🚀 Automatic prediction shuru ho rahi hai...")
    
    # Purane jobs clear karke naya shuru karna
    current_jobs = context.job_queue.get_jobs_by_name(str(query.message.chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    context.job_queue.run_repeating(auto_check, interval=interval, first=1, 
                                  chat_id=query.message.chat_id, name=str(query.message.chat_id))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
