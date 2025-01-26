#!/Users/malfunctxn/Code/Cloney/myenv/bin/python3
"""
Main module for the Torrent-to-GDrive Bot.

✅ Initializes the Telegram bot.
✅ Sets up logging for bot activity and errors.
✅ Registers all command handlers.
✅ Manages the connection to the aria2 torrent client.
"""

# 🛠️ Standard Libraries
import sys
import os
import time
import json  # Used to persist bot state
import logging

# 🌍 Third-Party Libraries
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# 📦 Project Modules
from bot_module.torrent_manager import TorrentManager
from bot_module.handlers import (
    start_handler, status_handler, purge_handler,
    add_torrent_handler, list_torrents_handler, torrent_status_handler, movie_search_handler
)
from config.config import TELEGRAM_BOT_TOKEN

# ✅ Ensure necessary directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs("config", exist_ok=True)  # Ensure config directory exists

# 🔹 File Paths for Logs and Bot State
LOG_BOT_FILE = "logs/bot_logs.log"
LOG_ERROR_FILE = "logs/error_logs.log"
LOG_ARIA2_FILE = "logs/aria2.log"
BOT_STATE_FILE = "config/bot_state.json"  # ✅ New persistent location

def ensure_log_file_exists(log_file):
    """
    Ensures a log file exists by creating an empty file if it doesn’t already exist.

    Args:
        log_file (str): The path of the log file.
    """
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")  # Create an empty file
        print(f"📂 Created missing log file: {log_file}")

# ✅ Ensure log files exist
ensure_log_file_exists(LOG_BOT_FILE)
ensure_log_file_exists(LOG_ERROR_FILE)
ensure_log_file_exists(LOG_ARIA2_FILE)

# ✅ Load or Set BOT_START_TIME
def load_bot_start_time():
    """
    Loads the bot start time from a persistent JSON file.
    If the file doesn't exist or is invalid, it initializes a new start time.
    """
    if os.path.exists(BOT_STATE_FILE):
        try:
            with open(BOT_STATE_FILE, "r") as f:
                state_data = json.load(f)
                return state_data.get("start_time", time.time())
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    # If no valid start time found, initialize a new one
    start_time = time.time()
    save_bot_start_time(start_time)
    return start_time

def save_bot_start_time(start_time):
    """
    Saves the bot start time in a JSON file.
    This ensures uptime is retained even if logs are deleted.
    """
    with open(BOT_STATE_FILE, "w") as f:
        json.dump({"start_time": start_time}, f)

BOT_START_TIME = load_bot_start_time()

# 🔹 Setup Log Handlers
file_handler_general = logging.FileHandler(LOG_BOT_FILE)
file_handler_general.setLevel(logging.INFO)

file_handler_error = logging.FileHandler(LOG_ERROR_FILE)
file_handler_error.setLevel(logging.ERROR)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Show only critical errors in console

# 🔹 Define Log Format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler_general.setFormatter(formatter)
file_handler_error.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 🔹 Configure Root Logger
logging.basicConfig(level=logging.DEBUG, handlers=[file_handler_general, file_handler_error, console_handler])
logger = logging.getLogger(__name__)

def initialize_torrent_manager():
    """
    Initializes the TorrentManager instance.

    If aria2 is not running, logs an error and returns None.
    """
    try:
        torrent_manager = TorrentManager(
            host="http://localhost",
            port=6800,
            secret="APZbUnwVUUVtYiTnZ7KNmMfdtjVEw4M540RuHs7Lm5E",  # Replace with your RPC secret
        )
        logger.info("✅ TorrentManager initialized successfully.")
        return torrent_manager
    except Exception as e:
        logger.error(f"❌ Failed to initialize TorrentManager: {str(e)}")
        return None

def main():
    """
    Initializes the Telegram bot and sets up command handlers.
    """
    # ✅ Initialize the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ✅ Initialize TorrentManager & store in bot_data
    application.bot_data["torrent_manager"] = initialize_torrent_manager()
    application.bot_data["start_time"] = BOT_START_TIME  # Store bot start time

    # ✅ Define and Register Handlers Dynamically
    command_handlers = {
        "start": start_handler.start,
        "status": status_handler.status,
        "purge": purge_handler.purge,
        "add_torrent": add_torrent_handler.add_torrent,
        "list_torrents": list_torrents_handler.list_torrents,
        "torrent_status": torrent_status_handler.torrent_status,
    }

    for command, handler in command_handlers.items():
        application.add_handler(CommandHandler(command, handler))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, movie_search_handler.movie_search))
    # ✅ Start the bot
    logger.info("🚀 Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
