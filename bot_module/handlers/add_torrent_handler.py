from telegram import Update
from telegram.ext import ContextTypes
import logging
import asyncio
from datetime import timedelta
from pathlib import Path

# 🔹 Global variables
last_message = None
logger = logging.getLogger(__name__)

async def add_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /add_torrent command to add a torrent/magnet link and track its progress.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    if not context.args:
        logger.warning("No magnet link provided for /add_torrent command.")
        await update.message.reply_text("Please provide a torrent or magnet link. Usage: /add_torrent <magnet_link>")
        return

    magnet_link = " ".join(context.args).strip()
    logger.info(f"Received magnet link: {magnet_link}")

    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        logger.error("TorrentManager not initialized in /add_torrent.")
        await update.message.reply_text("Error: TorrentManager not initialized.")
        return

    # 🔹 Add the torrent and get the GID
    gid = torrent_manager.add_torrent(magnet_link)

    if not isinstance(gid, str):
        logger.error(f"Failed to add torrent: Unexpected GID type: {type(gid)}")
        await update.message.reply_text("Error: Failed to retrieve a valid GID for the torrent.")
        return

    logger.info(f"Torrent added successfully with GID: {gid}")
    await update.message.reply_text(f"✅ Torrent added successfully! GID: `{gid}`", parse_mode="Markdown")

    # 🔹 Fetch torrent details (Using the new retry helper function)
    added_torrent = await fetch_torrent_details(context, gid, torrent_manager)

    if not added_torrent:
        await update.message.reply_text("⚠️ Torrent added, but unable to fetch details after multiple attempts.")
        return

    # 🔹 Format & send initial progress message
    message = format_torrent_message(added_torrent, gid)
    sent_message = await update.message.reply_text(message, parse_mode="Markdown")

    # 🔹 Start tracking progress
    await track_torrent_progress(context, update.effective_chat.id, sent_message.message_id, gid)


async def fetch_torrent_details(context, gid, torrent_manager, max_retries=10):
    """
    Fetches torrent details with retries if metadata is not ready.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        gid (str): The GID of the torrent.
        torrent_manager (TorrentManager): The TorrentManager instance.
        max_retries (int): Number of retries before failing.

    Returns:
        dict or None: Torrent details if successful, None if retries exceeded.
    """
    for attempt in range(max_retries):
        torrents = torrent_manager.list_torrents()

        if not isinstance(torrents, list):
            logger.warning(f"Error fetching torrents on attempt {attempt + 1}: Unexpected return type {type(torrents)}")
            await asyncio.sleep(2)
            continue

        for torrent in torrents:
            if isinstance(torrent, dict) and torrent.get("gid") == gid:
                logger.info(f"✅ Torrent details fetched successfully on attempt {attempt + 1}.")
                return torrent

        logger.warning(f"⚠️ Torrent metadata not ready yet, retrying ({attempt + 1}/{max_retries})...")
        await asyncio.sleep(2)

    logger.error("❌ Failed to fetch torrent details after multiple attempts.")
    return None


async def track_torrent_progress(context, chat_id, message_id, gid):
    """
    Track the progress of a torrent and update the Telegram message in real-time.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        chat_id (int): Telegram chat ID.
        message_id (int): Telegram message ID.
        gid (str): The GID of the torrent.
    """
    global last_message
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        return

    retry_count = 0

    while True:
        status = torrent_manager.get_torrent_status(gid)
        logger.info(f"DEBUG: Full Aria2 response (Attempt {retry_count}): {status}")

        if "error" in status:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=f"⚠️ Error tracking torrent: `{status['error']}`",
                parse_mode="Markdown",
            )
            break

        progress = float(status["progress"].replace("%", ""))
        eta_display = format_eta(status.get("eta"))

        raw_files = status.get("files", None)
        logger.info(f"DEBUG: Raw `files` data from Aria2 (Attempt {retry_count}): {raw_files}")

        if raw_files is None:
            retry_count += 1
            if retry_count > 15:
                file_list_display = "📡 Waiting for metadata..."
            else:
                logger.warning(f"⚠️ Torrent metadata not ready yet, retrying ({retry_count}/15)...")
                await asyncio.sleep(5)
                continue
        else:
            file_list_display = format_file_list(raw_files)

        new_message = format_torrent_message(status, gid, file_list_display)

        if new_message != last_message:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_message, parse_mode="Markdown")
            last_message = new_message

        if status["status"].lower() in ["seeding", "complete"]:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=f"{new_message}\n✅ *Download Complete!*",
                parse_mode="Markdown",
            )
            break

        await asyncio.sleep(3)


def format_torrent_message(torrent, gid, file_list_display="📡 Waiting for metadata..."):
    """
    Formats the torrent message for Telegram display.

    Args:
        torrent (dict): Torrent details.
        gid (str): The GID of the torrent.
        file_list_display (str): List of files or waiting message.

    Returns:
        str: Formatted message string.
    """
    return (
        f"📂 *Torrent Name:* `{torrent.get('name', 'Unknown')}`\n"
        f"📊 *Progress:* `{torrent.get('progress', '0%')}`\n"
        f"📌 *State:* `{torrent.get('status', 'N/A')}`\n"
        f"⏳ *ETA:* `{format_eta(torrent.get('eta'))}`\n"
        f"🆔 *GID:* `{gid}`\n"
        f"📄 *Files:*\n{file_list_display}"
    )


def format_eta(eta):
    """
    Formats ETA (time remaining) into a human-readable format.

    Args:
        eta (int or timedelta): Time remaining.

    Returns:
        str: Formatted ETA.
    """
    if isinstance(eta, timedelta):
        eta = int(eta.total_seconds())
    if not isinstance(eta, int) or eta < 0:
        return "N/A"
    return str(timedelta(seconds=eta)) if eta < 86400 else "N/A"


def format_file_list(raw_files):
    """
    Ensures file list is properly formatted.

    Args:
        raw_files (list or None): List of file paths.

    Returns:
        str: Formatted file list string.
    """
    if isinstance(raw_files, list):
        return "\n".join([f"📂 `{file}`" for file in raw_files])
    return "📡 Waiting for metadata..."
