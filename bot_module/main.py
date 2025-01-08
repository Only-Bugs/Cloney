#!/Users/malfunctxn/Code/Cloney/myenv/bin/python3

"""
Main module for the Torrent-to-GDrive Bot.

This module initializes the Telegram bot and listens for commands.
"""
import sys
import os
import time
import logging
from telegram.ext import Application, CommandHandler
from bot_module.torrent_manager import TorrentManager
from bot_module.handlers.start_handler import start
from bot_module.handlers.status_handler import status
from bot_module.handlers.purge_handler import purge
from bot_module.handlers.add_torrent_handler import add_torrent
from bot_module.handlers.list_torrents_handler import list_torrents
from bot_module.handlers.torrent_status_handler import torrent_status

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import configuration
from config.config import TELEGRAM_BOT_TOKEN

# Track bot start time
BOT_START_TIME = time.time()
# Create a logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# File handlers for logs
general_log_file = "logs/bot_logs.log"
error_log_file = "logs/error_logs.log"

# Define log handlers
file_handler_general = logging.FileHandler(general_log_file)
file_handler_general.setLevel(logging.INFO)

file_handler_error = logging.FileHandler(error_log_file)
file_handler_error.setLevel(logging.ERROR)
file_handler_error.setLevel(logging.WARNING)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Define a common log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler_general.setFormatter(formatter)
file_handler_error.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# Set up the root logger
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler_general, file_handler_error, console_handler])

# Create a logger instance for the bot
logger = logging.getLogger(__name__)

def main():
    """
    Initializes the Telegram bot and sets up command handlers.
    """
    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Initialize aria2-based TorrentManager and store it in bot_data
    try:
        torrent_manager = TorrentManager(
            host="http://localhost",
            port=6800,
            secret="APZbUnwVUUVtYiTnZ7KNmMfdtjVEw4M540RuHs7Lm5E",  # Replace with your RPC secret
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

    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()