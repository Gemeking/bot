from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import asyncio

# Telegram Bot Token
TOKEN = "8299233960:AAEn9hKdSr9S1eP0bry39tqAxywKlhOkwYA"
# Web App URL
WEBAPP_URL = "https://gemeking.github.io/cryptotracker/"
# Exchange Rate API URL
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/ETB?access_key=9b2b2dfba35e59129f2de9c4a5651e74&symbols=USD,EUR,GBP"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetch exchange rates
    try:
        response = requests.get(EXCHANGE_API_URL)
        data = response.json()
        if data.get("success", False):
            rates = data["rates"]
            rates_text = (
                f"Exchange Rates for 1 ETB (as of {data['date']}):\n"
                f"USD: {rates['USD']}\n"
                f"EUR: {rates['EUR']}\n"
                f"GBP: {rates['GBP']}"
            )
        else:
            rates_text = f"Error fetching rates: {data.get('error', {}).get('info', 'Unknown error')}"
    except Exception as e:
        rates_text = f"Failed to fetch exchange rates: {str(e)}"

    # Create web app button
    keyboard = [
        [InlineKeyboardButton(
            "Open Crypto Tracker 📊",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send welcome message with rates and web app button
    await update.message.reply_text(
        f"Welcome to Crypto Tracker!\n\n{rates_text}\n\nClick the button to open the tracker.",
        reply_markup=reply_markup
    )

async def main():
    # Initialize the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handler
    application.add_handler(CommandHandler("start", start))

    print("Bot is running...")
    try:
        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        # Keep running until interrupted
        await asyncio.Event().wait()  # Wait indefinitely until Ctrl+C
    except Exception as e:
        print(f"Error during bot execution: {str(e)}")
    finally:
        # Ensure proper shutdown
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("Bot has stopped.")

if __name__ == "__main__":
    # Create and run a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Received exit signal, shutting down...")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()