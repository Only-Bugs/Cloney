from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

def get_torrent_manager(context: ContextTypes.DEFAULT_TYPE):
    """Fetches the torrent manager instance from bot_data."""
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        logger.error("TorrentManager not initialized.")
        return None
    return torrent_manager

async def reply_with_error(update: Update, message: str):
    """Sends an error message to the user."""
    logger.warning(message)
    await update.message.reply_text(f"⚠️ {message}")

def validate_args(update: Update, context: ContextTypes.DEFAULT_TYPE, expected_args: int, usage_hint: str):
    """Validates command arguments and provides a hint if incorrect."""
    if len(context.args) < expected_args:
        return f"Usage: {usage_hint}"
    return None

def format_torrent_message(torrent, gid=None):
    """Formats a torrent's status message, including file details."""

    # Extract file list correctly from aria2p `File` objects
    files = torrent.get("files", [])
    file_list_display = "\n".join([
        f"📂 `{file.path.name}` — {file.completed_length}B / {file.length}B"
        for file in files
    ]) if files else "📡 Waiting for metadata..."

    # Construct progress message
    message = (
        f"📂 *Torrent Name:* `{torrent.get('name', 'Unknown')}`\n"
        f"📊 *Progress:* `{torrent.get('progress', '0%')}`\n"
        f"📌 *State:* `{torrent.get('status', 'N/A')}`\n"
        f"⏳ *ETA:* `{torrent.get('eta', 'N/A')}`\n"
        f"📄 *Files:*\n{file_list_display}"
    )

    if gid:
        message += f"\n🆔 *GID:* `{gid}`"

    return message





