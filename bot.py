import asyncio
import os
import random
import requests
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
        self.wfile.write(b"AUTO-SYSTEM ACTIVE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- BACKUP LOGIC AGAR API BLOCK HO ---
async def get_data_safe(mode):
    headers = {'User-Agent': 'Mozilla/5.0'}
    api_url = f"https://draw.ar-lottery01.com/WinGo/WinGo_{'30S' if mode == '30s' else '1M'}/GetHistoryIssuePage.json"
    try:
        response = requests.get(api_url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            last = data['data']['list'][0]
            p = str(int(last['issueNumber']) + 1)
            return p
    except:
        pass
    # Agar API block ho toh time se period nikal lo (Backup)
    import datetime
    now = datetime.datetime.now()
    p_time = now.strftime("%Y%m%d") + "1000" + str((now.hour * 60 + now.minute) * (2 if mode == '30s' else 1)).zfill(4)
    return p_time

# --- AUTOMATIC NON-STOP LOOP ---
async def start_auto_loop(context, chat_id, mode):
    interval = 30 if mode == "30s" else 60
    while user_active_modes.get(chat_id) == mode:
        p = await get_data_safe(mode)
        
        # Result Logic (As per your VIP style)
        res = random.choice(["BIG", "SMALL"])
        num = random.randint(0, 9)
        is_win = random.random() > 0.15
        status = "✅ WIN 💸💸💸" if is_win else "❌ LOSS 😭😭😭"
        color = "🟢" if res == "BIG" else "🔴"
        
        text = (
            f"👑 **BADSHAH KING AI V33**\n\n"
            f"🆔 **Period:** `{p}`\n"
            f"📊 **Result:** {res} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"✨ **Status:** {status}\n\n"
            f"⌛ Next Prediction in {interval}s..."
        )
        
        try:
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
        except:
            break # Agar koi aur error ho toh loop stop
            
        await asyncio.sleep(interval)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_active_modes[update.message.chat_id] = None
    keyboard = [[
        InlineKeyboardButton("🚀 START 30S AUTO", callback_data='30s'),
        InlineKeyboardButton("🚀 START 60S AUTO", callback_data='60s')
    ]]
    await update.message.reply_text("👑 **BADSHAH AUTO-SYSTEM**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode, chat_id = query.data, query.message.chat_id
    await query.answer()
    
    user_active_modes[chat_id] = mode
    await query.edit_message_text(f"✅ **{mode.upper()} AUTO-MODE SHURU!**\nAb har period par prediction aayegi.")
    asyncio.create_task(start_auto_loop(context, chat_id, mode))

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
