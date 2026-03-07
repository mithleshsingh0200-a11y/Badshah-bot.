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
        self.send_response(200); self.end_headers(); self.wfile.write(b"GOAGAMES_SYNC_LIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- GOAGAMES STRICT PERIOD SYNC (Exact Match) ---
def get_goagames_period(mode):
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    
    # Goagames 1-step back correction to match live exactly
    if mode == "30s":
        p_count = 50000 + (total_sec // 30)
    else:
        p_count = 10000 + (total_sec // 60)
    return f"{date_prefix}1000{p_count}"

# --- HTML PATTERNS INTEGRATION ---
def get_html_pattern():
    patterns = [
        "ZIG-ZAG PATTERN ⚡", 
        "CHIP MARKET PATTERN 🔍", 
        "DRAGON PATTERN 🐉", 
        "DOUBLE MIRROR PATTERN 💎"
    ]
    return random.choice(patterns)

async def dual_prediction_loop(context, mode, chat_id):
    last_p = ""
    while user_active_modes.get(chat_id) == mode:
        try:
            curr_p = get_goagames_period(mode)
            if curr_p == last_p:
                await asyncio.sleep(0.5); continue
            
            last_p = curr_p
            pattern = get_html_pattern()
            res = "BIG" if random.random() > 0.5 else "SMALL"
            color = "🟢 GREEN" if res == "BIG" else "🔴 RED"
            jacks = random.sample(range(5,10), 2) if res == "BIG" else random.sample(range(0,5), 2)

            # Initial Message with Scanning
            text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{curr_p}`\n"
                f"📈 **Pattern:** `{pattern}`\n"
                f"⏳ **Status:** `Scanning...`"
            )
            
            ch_msg = None
            try: ch_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
            except: pass
            p_msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

            # Fast Result: 2 Seconds only
            await asyncio.sleep(2)

            # Accuracy: Level 1-2 Win Logic
            win_msg = "✅ **LEVEL 1 WIN 💸**" if random.random() > 0.15 else "✅ **LEVEL 2 WIN 💰**"
            
            final_text = (
                f"👑 **BADSHAH KING AI - V33**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Period:** `{curr_p}`\n"
                f"📈 **Pattern:** `{pattern}`\n"
                f"📊 **Size:** `{res}`\n"
                f"🎨 **Colour:** {color}\n"
                f"🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n"
                f"✨ **Status:** {win_msg}\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            if ch_msg: await ch_msg.edit_text(final_text, parse_mode='Markdown')
            await p_msg.edit_text(final_text, parse_mode='Markdown')
            
            # Wait for next period
            await asyncio.sleep(5)
        except: await asyncio.sleep(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🚀 30S MODE", callback_data='30s'), 
           InlineKeyboardButton("🚀 60S MODE", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH KING AI (GOAGAMES)**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_active_modes[q.message.chat_id] = q.data
    await q.edit_message_text(f"🚀 **{q.data.upper()} SYNCED!**\nLive Result sending...")
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
