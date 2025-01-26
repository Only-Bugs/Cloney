# bot_module/handlers/start_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    - Sends a welcome message with basic usage instructions.
    - Logs when a user starts the bot.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    user = update.message.from_user
    logger.info(f"User {user.username or user.id} started the bot.")

    welcome_message = (
        "👋 *Welcome to the Torrent-to-GDrive Bot!* 🚀\n\n"
        "📌 *How to use:*\n"
        "1️⃣ Send a torrent/magnet link using `/add_torrent <magnet_link>`.\n"
        "2️⃣ Check active torrents with `/list_torrents`.\n"
        "3️⃣ View a specific torrent's status using `/torrent_status <GID>`.\n"
        "4️⃣ Use `/purge` to remove old messages.\n\n"
        "🔹 *Happy Downloading!* 🎉"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")
