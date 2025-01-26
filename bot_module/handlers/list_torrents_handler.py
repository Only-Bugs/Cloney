from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def list_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /list_torrents command to list all active torrents.

    - Fetches all torrents from aria2 via TorrentManager.
    - Formats the response into a structured message.
    - Handles errors if aria2 is unreachable or no torrents exist.
    """
    logger.info("Received /list_torrents command.")

    # 🔹 Fetch TorrentManager from bot_data
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        logger.error("❌ TorrentManager not initialized in /list_torrents.")
        await update.message.reply_text("⚠️ Error: TorrentManager not initialized.")
        return

    # 🔹 Retrieve torrent list from aria2
    torrents = torrent_manager.list_torrents()

    # 🔹 Handle Errors
    if isinstance(torrents, dict) and "error" in torrents:
        logger.error(f"❌ Error fetching torrents: {torrents['error']}")
        await update.message.reply_text(f"⚠️ Error: {torrents['error']}")
        return

    if not torrents:
        logger.info("✅ No torrents found in aria2.")
        await update.message.reply_text("📭 No active torrents.")
        return

    # 🔹 Format torrent list for Telegram
    torrent_messages = []
    for torrent in torrents:
        message = (
            f"📂 *Name:* `{torrent['name']}`\n"
            f"📊 *Progress:* `{torrent['progress']}`\n"
            f"📌 *State:* `{torrent['status']}`"
        )
        torrent_messages.append(message)

    # 🔹 Join messages (handle Telegram character limits)
    response_text = "\n\n".join(torrent_messages)
    if len(response_text) > 4000:  # Telegram's limit is ~4096 characters
        response_text = response_text[:4000] + "\n\n⚠️ *Message truncated due to length.*"

    logger.info(f"✅ Successfully fetched {len(torrents)} torrents.")
    await update.message.reply_text(response_text, parse_mode="Markdown")
