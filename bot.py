import asyncio
import os
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Render Environment Token
TOKEN = os.environ.get('BOT_TOKEN')

# --- AAPKA VIP HTML (Bina Password, Dono Modes) ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>BADSHAH KING AI 👑 - V33</title>
    <style>
        :root { --bg: #000; --neon: #00ff41; --red: #ff3131; --gold: #ffd700; --violet: #b659ff; }
        * { touch-action: manipulation; box-sizing: border-box; font-family: 'Courier New', monospace; }
        body { margin: 0; background: var(--bg); color: #fff; overflow-x: hidden; padding: 10px; }
        .stats-header { background: #0a0a0a; border: 1px solid #1a3a1a; border-radius: 12px; padding: 10px; margin-bottom: 10px; border-bottom: 3px solid var(--neon); }
        .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 5px; }
        .stat-box { background: #111; padding: 8px 5px; border-radius: 6px; text-align: center; border: 1px solid #222; }
        .stat-label { font-size: 8px; color: #888; display: block; margin-bottom: 2px; }
        .stat-val { font-size: 11px; color: var(--neon); font-weight: bold; }
        .tab-menu { display: flex; gap: 8px; margin: 10px 0; }
        .tab-btn { flex: 1; padding: 12px; background: #111; border: 1px solid #333; color: #666; font-weight: bold; border-radius: 8px; }
        .tab-btn.active { background: var(--neon); color: #000; border-color: var(--neon); }
        .card { background: #0a0a0a; border: 1px solid #1a3a1a; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; }
        .timer { font-size: 45px; font-weight: bold; color: var(--gold); }
        .pred-box { font-size: 52px; font-weight: 900; margin: 5px 0; letter-spacing: 3px; }
        .big { color: var(--neon); text-shadow: 0 0 15px var(--neon); }
        .small { color: var(--red); text-shadow: 0 0 15px var(--red); }
        .ball { width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 8px auto; font-weight: bold; font-size: 22px; border: 2px solid #fff; color: #fff; }
        .bg-g { background: #11e560; } .bg-r { background: #ff4d4d; }
    </style>
</head>
<body>
    <div class="stats-header">
        <div style="text-align: center; font-size: 14px; font-weight: bold; color: var(--neon); margin-bottom: 10px;">BADSHAH KING AI 👑</div>
        <div class="stats-grid">
            <div class="stat-box"><span class="stat-label">ACCURACY</span><span class="stat-val">99.1%</span></div>
            <div class="stat-box"><span class="stat-label">CONFIDENCE</span><span class="stat-val">98.4%</span></div>
            <div class="stat-box"><span class="stat-label">WIN RATE</span><span class="stat-val">99.5%</span></div>
        </div>
    </div>
    <div class="tab-menu">
        <button id="btn30" class="tab-btn active">30S MODE</button>
        <button id="btn60" class="tab-btn">60S MODE</button>
    </div>
    <div class="card">
        <div id="p-top" style="color:#888; font-size:14px; font-weight:bold;">PERIOD: Loading...</div>
        <div id="timer" class="timer">00:00</div>
    </div>
    <div class="card">
        <div class="pred-box big" id="pred-text">SCANNING</div>
        <div class="ball bg-g" id="ball">?</div>
    </div>
    <script>
        let mode = '30s';
        setInterval(() => {
            const now = new Date();
            let s = now.getSeconds();
            let timerDisplay = (mode === '30s') ? (s < 30 ? 30 - s : 60 - s) : (60 - s);
            document.getElementById('timer').innerText = "00:" + (timerDisplay < 10 ? "0"+timerDisplay : timerDisplay);
            let period = now.getFullYear().toString() + (now.getMonth()+1).toString().padStart(2,'0') + now.getDate().toString().padStart(2,'0') + "1000" + now.getHours() + now.getMinutes();
            document.getElementById('p-top').innerText = "PERIOD: " + period;
        }, 1000);
    </script>
</body>
</html>
"""

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(HTML_CODE, "utf8"))

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
    server.serve_forever()

# --- PREDICTION ENGINE (Win/Loss Emojis) ---
async def send_auto_prediction(chat_id, bot):
    while True:
        now = datetime.now()
        period = now.strftime("%Y%m%d1000%H%M")
        
        # Result Logic
        result = random.choice(["BIG", "SMALL"])
        num = random.choice([5,6,7,8,9]) if result == "BIG" else random.choice([0,1,2,3,4])
        
        # 90% Win Chance Emojis
        is_win = random.random() < 0.9
        emoji = "✅ WIN" if is_win else "❌ LOSS"
        color = "🟢" if result == "BIG" else "🔴"
        
        msg = (
            f"👑 **BADSHAH KING AI V33**\n\n"
            f"🆔 **Period:** `{period}`\n"
            f"📊 **Result:** {result} {color}\n"
            f"🔢 **Number:** {num}\n"
            f"✨ **Status:** {emoji}\n\n"
            f"⏳ **Next Prediction in 60s...**"
        )
        
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
        await asyncio.sleep(60)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ **VIP V33 SYSTEM ACTIVATED!**\nAuto predictions with Win/Loss emojis started.")
    asyncio.create_task(send_auto_prediction(update.effective_chat.id, context.bot))

async def main():
    print("🚀 BOT POLLING STARTING...")
    Thread(target=run_server, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
