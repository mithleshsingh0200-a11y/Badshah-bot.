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
        self.send_response(200); self.end_headers(); self.wfile.write(b"STRICT_SYNC_ACTIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

def get_live_period(mode):
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    total_sec = (now.hour * 3600) + (now.minute * 60) + now.second
    # 30s aur 60s EXACT LIVE SYNC
    p_count = (50000 + (total_sec // 30) + 1) if mode == "30s" else (10000 + (total_sec // 60) + 1)
    return f"{date_prefix}1000{p_count}"

async def dual_prediction_loop(context, mode, personal_chat_id):
    interval = 30 if mode == "30s" else 60
    last_period = ""
    
    while user_active_modes.get(personal_chat_id) == mode:
        try:
            current_p = get_live_period(mode)
            
            # Agar period change nahi hua, toh naya message nahi bhejega (No Spam)
            if current_p == last_period:
                await asyncio.sleep(1)
                continue
            
            last_period = current_p
            res = "BIG" if random.random() > 0.5 else "SMALL"
            color = "🟢 GREEN" if res == "BIG" else "🔴 RED"
            jacks = random.sample([5,6,7,8,9], 2) if res == "BIG" else random.sample([0,1,2,3,4], 2)

            text = f"👑 **BADSHAH VIP V33**\n\n🆔 **Period:** `{current_p}`\n📊 **Size:** {res}\n🎨 **Colour:** {color}\n🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n⏳ **Status:** Live..."
            
            # Ek saath dono jagah bhejega
            ch_msg = await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='Markdown')
            p_msg = await context.bot.send_message(chat_id=personal_chat_id, text=text, parse_mode='Markdown')

            # Wait for result time
            await asyncio.sleep(interval - 5)

            # Level 1-2 Win Logic
            win_msg = "✅ **LEVEL 1 WIN 💸**" if random.random() > 0.1 else "✅ **LEVEL 2 WIN 💰**"
            final_text = f"👑 **BADSHAH VIP V33**\n\n🆔 **Period:** `{current_p}`\n📊 **Result:** {res} {color}\n🎯 **Jackpot:** `{jacks[0]}, {jacks[1]}`\n✨ **Status:** {win_msg}"
            
            await ch_msg.edit_text(final_text, parse_mode='Markdown')
            await p_msg.edit_text(final_text, parse_mode='Markdown')
            
            await asyncio.sleep(5) # Small gap before next period
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None
    keyboard = [[InlineKeyboardButton("🚀 30S (DUAL)", callback_data='30s'), 
                  InlineKeyboardButton("🚀 60S (DUAL)", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH DUAL MODE**\nChannel: @Priyan1255\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    # Purana loop rokne ke liye
    user_active_modes[chat_id] = query.data
    await query.edit_message_text(f"🚀 **{query.data.upper()} CONNECTED!**\nStrict Sync Active.")
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
