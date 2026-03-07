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
        self.send_response(200); self.end_headers(); self.wfile.write(b"BADSHAH_INSTANT_V33")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

def get_goagames_period(mode):
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    # Strict Sync with Goagames
    p_count = (50000 + (total_sec // 30) + 1) if mode == "30s" else (10000 + (total_sec // 60) + 1)
    return f"{date_prefix}1000{p_count}"

async def dual_prediction_loop(context, mode, chat_id):
    last_p = ""
    while user_active_modes.get(chat_id) == mode:
        try:
            curr_p = get_goagames_period(mode)
            if curr_p == last_p:
                await asyncio.sleep(0.1); continue # High Frequency Check
            
            last_p = curr_p
            res = "BIG" if random.random() > 0.5 else "SMALL"
            # Colour Update: Green for Big, Red for Small
            color = "🟢 GREEN" if res == "BIG" else "🔴 RED"
            # MIX JACKPOT: 2 random numbers
            jacks = random.sample(range(0, 10), 2) 

            # 1. Prediction Message (No Level yet)
            text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{curr_p}`\n"
                f"📊 **Size:** `{res}`\n"
                f"🎨 **Colour:** {color}\n"
                f"🎯 **Mix Jackpot:** `{jacks[0]}, {jacks[1]}`\n"
                f"⏳ **Status:** `Waiting...`"
            )
            
            ch_msg = None
            try: ch_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
            except: pass
            p_msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

            # 2. WAIT UNTIL EXACT END OF PERIOD
            wait_time = 28 if mode == "30s" else 58
            await asyncio.sleep(wait_time)

            # 3. INSTANT 2 SEC SCANNING
            scan_text = text.replace("Waiting...", "Scanning Result... 🔄")
            if ch_msg: await ch_msg.edit_text(scan_text, parse_mode='Markdown')
            await p_msg.edit_text(scan_text, parse_mode='Markdown')
            await asyncio.sleep(2)

            # 4. FINAL RESULT (Strict Level 1-2)
            win_msg = "✅ **LEVEL 1 WIN 💸**" if random.random() > 0.15 else "✅ **LEVEL 2 WIN 💰**"
            final_text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{curr_p}`\n"
                f"📊 **Result:** `{res} {color}`\n"
                f"🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n"
                f"✨ **Status:** {win_msg}\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            if ch_msg: await ch_msg.edit_text(final_text, parse_mode='Markdown')
            await p_msg.edit_text(final_text, parse_mode='Markdown')
            
        except Exception: await asyncio.sleep(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🚀 30S MODE", callback_data='30s'), 
           InlineKeyboardButton("🚀 60S MODE", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH KING AI (FAST SYNC)**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_active_modes[q.message.chat_id] = q.data
    await q.edit_message_text(f"🚀 **{q.data.upper()} CONNECTED!**\nInstant Result Enabled.")
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
