from telegram import Update
from telegram.ext import ContextTypes
import logging

# 🔹 Logger setup
logger = logging.getLogger(__name__)

async def torrent_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /torrent_status command to get the status of a specific torrent by its GID.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """

    # ✅ Validate if GID was provided
    if not context.args:
        logger.warning("⚠️ No GID provided for /torrent_status command.")
        await update.message.reply_text("⚠️ Please provide a torrent GID.\nUsage: `/torrent_status <GID>`", parse_mode="Markdown")
        return

    gid = context.args[0].strip()
    logger.info(f"🔍 Checking status for Torrent GID: {gid}")

    # ✅ Get TorrentManager instance
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        logger.error("❌ TorrentManager not initialized in /torrent_status.")
        await update.message.reply_text("❌ Error: TorrentManager not initialized.")
        return

    # ✅ Fetch torrent status
    status = torrent_manager.get_torrent_status(gid)

    if "error" in status:
        logger.error(f"❌ Error fetching torrent status: {status['error']}")
        await update.message.reply_text(f"❌ Error: `{status['error']}`", parse_mode="Markdown")
        return

    # ✅ Fix: Clamp ETA values to prevent overflow
    eta_display = status.get("eta", "N/A")
    if isinstance(eta_display, int):
        if eta_display < 0 or eta_display > 999999999:  # Clamp values
            eta_display = "N/A"
        else:
            from datetime import timedelta
            eta_display = str(timedelta(seconds=eta_display))  # Convert seconds to readable format

    # ✅ Format message with markdown
    response = (
        f"📂 *Torrent Name:* `{status.get('name', 'N/A')}`\n"
        f"📌 *State:* `{status.get('status', 'N/A')}`\n"
        f"📊 *Progress:* `{status.get('progress', 'N/A')}`\n"
        f"🚀 *Download Speed:* `{status.get('download_speed', '0 KB/s')}`\n"
        f"⏳ *ETA:* `{eta_display}`"
    )

    logger.info(f"✅ Successfully fetched status for GID: {gid}")
    await update.message.reply_text(response, parse_mode="Markdown")
