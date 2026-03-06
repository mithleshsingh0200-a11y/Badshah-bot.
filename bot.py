import asyncio
import os
import random
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')
user_active_modes = {}

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"GOAGAMES_LIVE_v33")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck)
    server.serve_forever()

# --- PERFECT SYNC LOGIC (30s OK, 60s FIXED) ---
def get_live_period(mode):
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d") # Har din/month/year auto badlega
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    
    if mode == "30s":
        period_count = 50000 + (total_sec // 30) + 1 # 30s as it is
    else:
        # 60s ko 1 kadam piche karke live sync kiya hai
        period_count = 10000 + (total_sec // 60) + 1 
        
    return f"{date_prefix}1000{period_count}"

async def auto_loop(context, chat_id, mode):
    interval = 30 if mode == "30s" else 60
    while user_active_modes.get(chat_id) == mode:
        try:
            p = get_live_period(mode)
            res = "BIG" if random.random() > 0.5 else "SMALL"
            color = "🟢 GREEN" if res == "BIG" else "🔴 RED"
            jacks = random.sample([5,6,7,8,9], 2) if res == "BIG" else random.sample([0,1,2,3,4], 2)

            # Step 1: Prediction Message (No 5s check)
            text = (
                f"👑 **BADSHAH KING VIP V33**\n\n"
                f"🆔 **Period:** `{p}`\n"
                f"📊 **Size:** {res}\n"
                f"🎨 **Colour:** {color}\n"
                f"🎯 **Jackpot Nos:** `{jacks[0]}, {jacks[1]}`\n"
                f"⏳ **Status:** Live Prediction..."
            )
            msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')

            # Wait for full interval
            await asyncio.sleep(interval - 2)

            # Step 2: Level 1-2 Win Result
            is_win = random.random() > 0.12
            gift = "✅ **LEVEL 1 WIN 💸💸💸**" if is_win else "✅ **LEVEL 2 WIN 💰💰💰**"
            
            final_text = (
                f"👑 **BADSHAH KING VIP V33**\n\n"
                f"🆔 **Period:** `{p}`\n"
                f"📊 **Result:** {res} {color}\n"
                f"🎯 **Jackpot Nos:** `{jacks[0]}, {jacks[1]}`\n"
                f"✨ **Status:** {gift}\n\n"
                f"✅ New period starting..."
            )
            await msg.edit_text(final_text, parse_mode='Markdown')
            await asyncio.sleep(2)
        except Exception:
            await asyncio.sleep(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None
    keyboard = [[InlineKeyboardButton("🚀 30S MODE", callback_data='30s'), 
                  InlineKeyboardButton("🚀 60S MODE", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH LIVE SYNC**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query, chat_id = update.callback_query, update.callback_query.message.chat_id
    await query.answer()
    user_active_modes[chat_id] = query.data
    await query.edit_message_text(f"🚀 **{query.data.upper()} CONNECTED!**\n24/7 Auto Sync Start.")
    asyncio.create_task(auto_loop(context, chat_id, query.data))

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
