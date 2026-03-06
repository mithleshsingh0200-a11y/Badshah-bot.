# Yeh part dono modes ko manage kar raha hai
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Dono modes ke buttons yahan hain
    keyboard = [[InlineKeyboardButton("🚀 30S MODE", callback_data='30s'), 
                  InlineKeyboardButton("🚀 60S MODE", callback_data='60s')]]
    await update.message.reply_text("👑 **BADSHAH LIVE SYNC**\nSelect Mode:", reply_markup=InlineKeyboardMarkup(keyboard))
