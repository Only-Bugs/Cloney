from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def list_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /list_torrents command to list all torrents.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        await update.message.reply_text("Error: TorrentManager not initialized.")
        return

    torrents = torrent_manager.list_torrents()

    if "error" in torrents:
        await update.message.reply_text(f"Error: {torrents['error']}")
        return

    if not torrents:
        await update.message.reply_text("No torrents found.")
        return

    response = "\n\n".join(
        [
            f"Name: {torrent['name']}\nState: {torrent['state']}\nProgress: {torrent['progress']}"
            for torrent in torrents
        ]
    )
    await update.message.reply_text(response)
