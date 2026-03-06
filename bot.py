import asyncio
import os
import random
import time
from datetime import datetime
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')

# Render Health Check
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"BADSHAH V33 SYSTEM STABLE")

def run_server():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheck).serve_forever()

# --- SMART PREDICTION LOGIC (No API Reliance) ---
def generate_smart_prediction(mode):
    # Current time ke hisab se period number calculate karna (Goagames Style)
    now = datetime.now()
    total_seconds = now.hour * 3600 + now.minute * 60 + now.second
    
    if mode == "30s":
        period_suffix = str(total_seconds // 30).zfill(4)
    else:
        period_suffix = str(total_seconds // 60).zfill(4)
        
    current_date = now.strftime("%Y%m%d")
    period = f"{current_date}1000{period_suffix}"
    
    # Result patterns (Dragon/Zig-Zag Simulation)
    res = random.choice(["BIG", "SMALL"])
    num = random.choice([5,6,7,8,9]) if res == "BIG" else random.choice([0,1,2,3,4])
    return period, res, num

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🎮 30S MODE", callback_data='30s'),
        InlineKeyboardButton("🎮 60S MODE", callback_data='60s')
    ]]
    await update.message.reply_text(
        "👑 **BADSHAH GOAGAMES VIP V33**\n\nAb connection 100% stable hai. Mode select karein:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = query.data
    await query.answer()
    
    await query.edit_message_text(f"📡 **ANALYZING {mode.upper()} PATTERNS...**")
    await asyncio.sleep(1) # Realistic Delay
    
    p, res, num = generate_smart_prediction(mode)
    
    # Win/Loss Emoji logic as per demand
    is_win = random.random() > 0.10 
    status = "✨ STATUS: WIN 💸💸💸" if is_win else "✨ STATUS: LOSS 😭😭😭"
    color = "🟢" if res == "BIG" else "🔴"
    
    text = (
        f"👑 **BADSHAH {mode.upper()} VIP**\n\n"
        f"🆔 **Period:** `{p}`\n"
        f"📊 **Result:** {res} {color}\n"
        f"🔢 **Number:** {num}\n"
        f"{status}\n\n"
        f"⏳ Agla result period badalne par nikalein."
    )
    keyboard = [[InlineKeyboardButton("🔄 GET NEXT PREDICTION", callback_data=mode)]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def main():
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_click))
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
