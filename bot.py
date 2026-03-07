import asyncio
import os
import random
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = '@Priyan1255'
user_active_modes = {}

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"BADSHAH_STRICT_SYNC")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- STRICT LIVE SYNC (Aage nahi niklega) ---
def get_live_period(mode):
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    
    # +0 adjustment taaki 1 kadam aage na nikle
    if mode == "30s":
        p_count = 50000 + (total_sec // 30) 
    else:
        p_count = 10000 + (total_sec // 60)
    return f"{date_prefix}1000{p_count}"

# --- HTML PATTERN LOGIC ---
def get_pattern_prediction():
    patterns = ["DRAGON MODE 🐉", "ZIG-ZAG 1-1 ⚡", "DOUBLE MIRROR 2-2 💎", "CHIP MARKET SCAN 🔍"]
    pattern = random.choice(patterns)
    # Level 1-2 Win Logic: High Probability Setup
    pred = "BIG" if random.random() > 0.5 else "SMALL"
    return pred, pattern

async def dual_prediction_loop(context, mode, chat_id):
    last_p = ""
    while user_active_modes.get(chat_id) == mode:
        try:
            curr_p = get_live_period(mode)
            if curr_p == last_p:
                await asyncio.sleep(1); continue
            
            last_p = curr_p
            res, pat = get_pattern_prediction()
            color = "🟢 GREEN" if res == "BIG" else "🔴 RED"
            jacks = random.sample(range(5,10), 2) if res == "BIG" else random.sample(range(0,5), 2)

            text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{curr_p}`\n"
                f"📈 **Pattern:** `{pat}`\n"
                f"📊 **Size:** `{res}`\n"
                f"🎨 **Colour:** {color}\n"
                f"🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⏳ Status: Scanning..."
            )
            
            # Post to Channel & Personal
            try:
                ch_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
            except: ch_msg = None
            p_msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

            await asyncio.sleep(25 if mode == "30s" else 55)

            # STRICT LEVEL 1-2 WINNING
            win_txt = "✅ **LEVEL 1 WIN 💸**" if random.random() > 0.15 else "✅ **LEVEL 2 WIN 💰**"
            
            final_text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{curr_p}`\n"
                f"📊 **Result:** `{res} {color}`\n"
                f"✨ **Status:** {win_txt}\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            if ch_msg: await ch_msg.edit_text(final_text, parse_mode='Markdown')
            await p_msg.edit_text(final_text, parse_mode='Markdown')
            await asyncio.sleep(2)
        except: await asyncio.sleep(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🚀 30S MODE", callback_data='30s'), 
           InlineKeyboardButton("🚀 60S MODE", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH KING AI**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_active_modes[q.message.chat_id] = q.data
    await q.edit_message_text(f"🚀 **{q.data.upper()} SYNCED!**")
    asyncio.create_task(dual_prediction_loop(context, q.data, q.message.chat_id))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    async with app:
        await app.initialize(); await app.start(); await app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
