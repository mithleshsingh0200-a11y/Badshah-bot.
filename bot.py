import asyncio
import os
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Render ki settings se token lega
TOKEN = os.environ.get('BOT_TOKEN')

# --- HEALTH CHECK SERVER (Render ko Live rakhne ke liye) ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><body><h1>Badshah Bot is Online!</h1></body></html>", "utf8"))
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# --- PREDICTION LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎯 91CLUB 1 MIN", callback_data='predict')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 **WELCOME TO BADSHAH PREDICTOR**\n\nClick below for 1-minute prediction.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'predict':
        msg = await query.edit_message_text("⏳ **ANALYZING NEXT PERIOD...**")
        await asyncio.sleep(2) # Thoda wait dikhane ke liye
        
        result = random.choice(["BIG 🟢", "SMALL 🔴"])
        number = random.choice([0,1,2,3,4,5,6,7,8,9])
        
        prediction_text = (
            f"✅ **PREDICTION READY**\n\n"
            f"📊 **Result:** {result}\n"
            f"🔢 **Number:** {number}\n"
            f"⏳ **Next Prediction in:** 30 seconds"
        )
        await msg.edit_text(prediction_text)
        
        # 30-second ka timer
        await asyncio.sleep(30)
        
        keyboard = [[InlineKeyboardButton("🎯 GET NEXT PREDICTION", callback_data='predict')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("✅ **TIMER OVER!** You can get new prediction now.", reply_markup=reply_markup)

async def main():
    print("🚀 BOT POLLING STARTING...") #
    Thread(target=run_server, daemon=True).start() #
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    async with app:
        await app.initialize()
        await app.start()
        # Conflict error ko khatam karne ke liye
        await app.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main()) #
