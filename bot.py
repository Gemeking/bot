import os
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ----------------------
# Environment Variables
# ----------------------
TOKEN = "8299233960:AAEn9hKdSr9S1eP0bry39tqAxywKlhOkwYA"
  # Telegram Bot Token from Railway Environment
WEBAPP_URL = "https://gemeking.github.io/cryptotracker/"
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/ETB?access_key=9b2b2dfba35e59129f2de9c4a5651e74&symbols=USD,EUR,GBP"

# ----------------------
# /start Command Handler
# ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch exchange rates
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=10)
        data = response.json()
        rates = data.get("rates", {})
        if rates:
            # Convert to format: 1 USD = XXX ETB
            usd_to_etb = round(1 / rates.get("USD", 0.0), 2)
            eur_to_etb = round(1 / rates.get("EUR", 0.0), 2)
            gbp_to_etb = round(1 / rates.get("GBP", 0.0), 2)

            rates_text = (
                f"💱 Exchange Rates (ETB):\n"
                f"1 USD = {usd_to_etb} ETB\n"
                f"1 EUR = {eur_to_etb} ETB\n"
                f"1 GBP = {gbp_to_etb} ETB\n"
                f"📅 Date: {data.get('date')}"
            )
        else:
            rates_text = "⚠️ Failed to fetch exchange rates."
    except Exception as e:
        rates_text = f"⚠️ Error fetching rates: {str(e)}"

    # Create Web App button
    keyboard = [
        [InlineKeyboardButton("Open Crypto Tracker 📊", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message
    await update.message.reply_text(
        f"Welcome to Crypto Tracker Bot!\n\n{rates_text}\n\nClick the button below to open the tracker.",
        reply_markup=reply_markup
    )

# ----------------------
# Main Bot Runner
# ----------------------
async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("Bot is running...")

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    # Keep running until manually stopped
    await asyncio.Event().wait()

    # Shutdown properly
    await application.updater.stop()
    await application.stop()
    await application.shutdown()
    print("Bot stopped.")

# ----------------------
# Run the Bot
# ----------------------
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot interrupted. Shutting down...")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

