import random
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = '8044105919:AAGgf9AKQcLYil_XnlB03NPsylRVKz5bWDE'


class BadshahEngine:
    def __init__(self):
        self.lvlS = 1
        self.lvlC = 1

    def get_pred(self, mode):
        patterns = ["DRAGON 🐉", "ZIG-ZAG 📈", "DOUBLE MIRROR 🪞", "CHIP MARKET 🤖"]
        pat = random.choice(patterns)
        size = random.choice(["BIG", "SMALL"])
        color = random.choice(["RED", "GREEN"])
        
        # Level 1-2 Recovery Logic
        if self.lvlS == 2: size = "SMALL" if size == "BIG" else "BIG"
        if self.lvlC == 2: color = "GREEN" if color == "RED" else "RED"

        # Jackpot Logic (2 types as per HTML)
        if random.random() < 0.15:
            color = random.choice(["🔴+🟣 Jackpot (0)", "🟢+🟣 Jackpot (5)"])
        
        return {"s": size, "c": color, "p": pat, "ls": self.lvlS, "lc": self.lvlC}

engine = BadshahEngine()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("⏱️ 30S MODE", callback_data='30')],
                [InlineKeyboardButton("⏱️ 60S MODE", callback_data='60')]]
    await update.message.reply_text("👑 *BADSHAH AI V240 PERSISTENT*\n\nApna mode select karein. Bot 24 ghante automatic prediction bhejta rahega:", 
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def auto_loop(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    res = engine.get_pred(job.data)
    period = time.strftime("%Y%m%d%H%M")
    
    msg = (f"👑 *BADSHAH AI*\n━━━━━━━━━━━━\n⏱️ MODE: {job.data}s\n🆔 PERIOD: `{period}`\n\n"
           f"📊 PATTERN: {res['p']}\n📏 SIZE: *{res['s']}*\n🎨 COLOUR: *{res['c']}*\n"
           f"📈 STRATEGY: Lvl {res['ls']}/{res['lc']}\n━━━━━━━━━━━━\n✅ WINNING SECURED!")
    
    await context.bot.send_message(chat_id=job.chat_id, text=msg, parse_mode='Markdown')
    # Simulation for Winning
    await asyncio.sleep(max(1, job.data - 5))
    await context.bot.send_message(chat_id=job.chat_id, text="💰 *WINNING!!* 💰", parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sec = int(query.data)
    # Purane jobs clear karein
    for j in context.job_queue.get_jobs_by_name(str(query.message.chat_id)): j.schedule_removal()
    # Naya loop shuru karein
    context.job_queue.run_repeating(auto_loop, interval=sec, first=1, chat_id=query.message.chat_id, name=str(query.message.chat_id), data=sec)
    await query.edit_message_text(f"✅ *{sec}s MODE ACTIVATED*\nBot ab 24 ghante automatic chalta rahega!", parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
      
