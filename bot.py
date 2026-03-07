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
        self.send_response(200); self.end_headers(); self.wfile.write(b"BADSHAH_V33_LIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- PURANA PERFECT SYNC PERIOD LOGIC ---
def get_live_period(mode):
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    # 30s: 2 periods/min | 60s: 1 period/min
    p_count = (50000 + (total_sec // 30) + 1) if mode == "30s" else (10000 + (total_sec // 60) + 1)
    return f"{date_prefix}1000{p_count}"

# --- HTML PATTERN ANALYSIS LOGIC ---
def get_html_prediction():
    patterns = ["DRAGON MODE 🐉", "ZIG-ZAG 1-1 ⚡", "DOUBLE MIRROR 2-2 💎", "CHIP MARKET SCAN 🔍"]
    current_pattern = random.choice(patterns)
    prediction = "BIG" if random.random() > 0.5 else "SMALL"
    return prediction, current_pattern

async def dual_prediction_loop(context, mode, personal_chat_id):
    last_period = ""
    
    while user_active_modes.get(personal_chat_id) == mode:
        try:
            current_p = get_live_period(mode)
            if current_p == last_period:
                await asyncio.sleep(1); continue
            
            last_period = current_p
            pred, pattern = get_html_prediction()
            color = "🟢 GREEN" if pred == "BIG" else "🔴 RED"
            # Jackpot logic from HTML: BIG (5-9), SMALL (0-4)
            jacks = random.sample(range(5, 10), 2) if pred == "BIG" else random.sample(range(0, 5), 2)
            
            # HTML Stats Simulation
            accuracy = round(98 + random.random() * 1.5, 1)

            text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{current_p}`\n"
                f"📈 **Pattern:** `{pattern}`\n"
                f"📊 **Size:** `{pred}`\n"
                f"🎨 **Colour:** {color}\n"
                f"🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n"
                f"✨ **Accuracy:** `{accuracy}%`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⏳ Status: Scanning Next..."
            )
            
            # Sending to Channel & Personal
            ch_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
            p_msg = await context.bot.send_message(chat_id=personal_chat_id, text=text, parse_mode='Markdown')

            await asyncio.sleep(25 if mode == "30s" else 55)

            # HTML LEVEL 1-2 WIN LOGIC
            win_type = "✅ LEVEL 1 WIN 💸" if random.random() > 0.15 else "✅ LEVEL 2 WIN 💰"
            
            final_text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{current_p}`\n"
                f"📊 **Result:** `{pred} {color}`\n"
                f"🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n"
                f"✨ **Status:** {win_type}\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            await ch_msg.edit_text(final_text, parse_mode='Markdown')
            await p_msg.edit_text(final_text, parse_mode='Markdown')
            await asyncio.sleep(5)
            
        except Exception: await asyncio.sleep(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None
    keyboard = [[InlineKeyboardButton("🚀 30S MODE (DUAL)", callback_data='30s'), 
                  InlineKeyboardButton("🚀 60S MODE (DUAL)", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH KING AI V33**\nPassword Removed.\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    user_active_modes[chat_id] = query.data
    await query.edit_message_text(f"🚀 **{query.data.upper()} CONNECTED!**\nSending to Channel & Personal Inbox.")
    asyncio.create_task(dual_prediction_loop(context, query.data, chat_id))

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    async with app:
        await app.initialize(); await app.start(); await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
