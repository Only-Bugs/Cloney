# bot_module/handlers/torrent_status_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def torrent_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /torrent_status command to get the status of a specific torrent.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    if not context.args:
        await update.message.reply_text("Please provide a torrent hash. Usage: /torrent_status <torrent_hash>")
        return

    torrent_hash = context.args[0].strip()
    logger.info(f"Received torrent hash: {torrent_hash}")

    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        await update.message.reply_text("Error: TorrentManager not initialized.")
        return

    # Get the torrent status
    status = torrent_manager.get_torrent_status(torrent_hash)

    if "error" in status:
        await update.message.reply_text(f"Error: {status['error']}")
        return

    # Format the response
    eta = f"{status['eta']} seconds" if status['eta'] != "N/A" else "N/A"
    response = (
        f"State: {status['state']}\n"
        f"Progress: {status['progress']}\n"
        f"ETA: {eta}"
    )
    await update.message.reply_text(response)
