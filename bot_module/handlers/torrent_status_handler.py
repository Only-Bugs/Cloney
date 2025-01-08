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
        logger.warning("No GID provided for /torrent_status command.")
        await update.message.reply_text("Please provide a torrent GID. Usage: /torrent_status <GID>")
        return

    gid = context.args[0].strip()
    logger.info(f"Received torrent GID: {gid}")

    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        logger.error("TorrentManager not initialized in /torrent_status.")
        await update.message.reply_text("Error: TorrentManager not initialized.")
        return

    # Get the torrent status
    status = torrent_manager.get_torrent_status(gid)

    if "error" in status:
        logger.error(f"Error fetching torrent status: {status['error']}")
        await update.message.reply_text(f"Error: {status['error']}")
        return

    # Format the response
    eta = status.get("eta", "N/A")
    response = (
        f"Name: {status.get('name', 'N/A')}\n"
        f"State: {status.get('status', 'N/A')}\n"
        f"Progress: {status.get('progress', 'N/A')}\n"
        f"Download Speed: {status.get('download_speed', '0 KB/s')}\n"
        f"ETA: {eta}"
    )
    logger.info(f"Successfully fetched status for GID: {gid}")
    await update.message.reply_text(response)
