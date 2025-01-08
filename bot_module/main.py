"""
Main module for the Torrent-to-GDrive Bot.

This module initializes the Telegram bot and listens for commands.
"""
import sys
import os
import time
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot_module.torrent_manager import TorrentManager
from bot_module.handlers.start_handler import start
from bot_module.handlers.status_handler import status
from bot_module.handlers.purge_handler import purge
from bot_module.handlers.add_torrent_handler import add_torrent
from bot_module.handlers.list_torrents_handler import list_torrents
from bot_module.handlers.torrent_status_handler import torrent_status
from bot_module.handlers.movie_search_handler import movie_search

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import configuration
from config.config import TELEGRAM_BOT_TOKEN, QB_HOST, QB_USERNAME, QB_PASSWORD

# Track bot start time
BOT_START_TIME = time.time()
LOG_FILE = "bot_logs.log"


# Set up logging
# Configure logging handlers
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)  # Log everything to the file

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in the terminal

# Configure logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Set up the root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# Create a logger instance
logger = logging.getLogger(__name__)


def main():
    """
    Initializes the Telegram bot and sets up command handlers.
    """
    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Initialize TorrentManager and store it in bot_data
    try:
        torrent_manager = TorrentManager(
            host=QB_HOST,
            username=QB_USERNAME,
            password=QB_PASSWORD,
        )
        application.bot_data["torrent_manager"] = torrent_manager
        logger.info("TorrentManager initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize TorrentManager: {str(e)}")
        return

    # Add the bot's start time to bot_data
    application.bot_data["start_time"] = BOT_START_TIME

    # Add command handlers
    application.add_handler(CommandHandler("start", start))  # /start command
    application.add_handler(CommandHandler("status", status))  # /status command
    application.add_handler(CommandHandler("purge", purge))  # /purge command
    application.add_handler(CommandHandler("add_torrent", add_torrent))  # /add_torrent command
    application.add_handler(CommandHandler("list_torrents", list_torrents))  # /list_torrents command
    application.add_handler(CommandHandler("torrent_status", torrent_status))  # /torrent_status command
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, movie_search))


    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
