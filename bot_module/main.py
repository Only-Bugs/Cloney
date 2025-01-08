"""
Main module for the Torrent-to-GDrive Bot.

This module initializes the Telegram bot and listens for commands.
"""
import sys
import os
import time
import logging

from telegram.ext import Application, CommandHandler
from config.config import QB_HOST, QB_USERNAME, QB_PASSWORD
from bot_module.torrent_manager import TorrentManager
from bot_module.handlers.start_handler import start
from bot_module.handlers.status_handler import status
from bot_module.handlers.purge_handler import purge

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import configuration
from config.config import TELEGRAM_BOT_TOKEN

# Track bot start time
BOT_START_TIME = time.time()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """
    Initializes the Telegram bot and sets up command handlers.
    """
    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Initialize TorrentManager and store it in bot_data
    torrent_manager = TorrentManager(
        host=QB_HOST,
        username=QB_USERNAME,
        password=QB_PASSWORD,
    )
    application.bot_data["torrent_manager"] = torrent_manager
    application.bot_data["start_time"] = BOT_START_TIME

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("purge", purge))

    logger.info("TorrentManager initialized successfully.")
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
