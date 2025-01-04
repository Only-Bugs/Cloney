"""
Main module for the Torrent-to-GDrive Bot.

This module initializes the Telegram bot and listens for commands.
"""
import sys
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from config.config import TELEGRAM_BOT_TOKEN



# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    Sends a welcome message to the user.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    await update.message.reply_text("Welcome to the Torrent-to-GDrive Bot! 🚀\nSend a torrent link to get started.")

def main():
    """
    Initializes the Telegram bot and sets up command handlers.
    """
    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))

    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
