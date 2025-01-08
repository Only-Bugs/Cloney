from telegram import Update
from telegram.ext import ContextTypes
import logging
import asyncio
from datetime import timedelta
from pathlib import Path, PosixPath

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

    # Add the torrent and get the GID
    gid = torrent_manager.add_torrent(magnet_link)
    
    # 🔹 Ensure gid is a valid string
    if not isinstance(gid, str):
        logger.error(f"Failed to add torrent: Unexpected GID type: {type(gid)}")
        await update.message.reply_text("Error: Failed to retrieve a valid GID for the torrent.")
        return

    logger.info(f"Torrent added successfully with GID: {gid}")
    await update.message.reply_text(f"✅ Torrent added successfully! GID: `{gid}`", parse_mode="Markdown")

    # Retry fetching torrent details
    added_torrent = None
    for attempt in range(10):  # Retry up to 10 times
        torrents = torrent_manager.list_torrents()

        if not isinstance(torrents, list):
            logger.warning(f"Error fetching torrents on attempt {attempt + 1}: Unexpected return type {type(torrents)}")
            await asyncio.sleep(2)
            continue

        for torrent in torrents:
            if isinstance(torrent, dict) and torrent.get("gid") == gid:
                added_torrent = torrent
                break

        if added_torrent:
            logger.info(f"✅ Torrent details fetched successfully on attempt {attempt + 1}.")
            break

        logger.info(f"🔄 Retrying... Attempt {attempt + 1}")
        await asyncio.sleep(2)  # Wait before retrying

    if not added_torrent:
        logger.error("❌ Failed to fetch torrent details after multiple attempts.")
        await update.message.reply_text("⚠️ Torrent added, but unable to fetch details after multiple attempts.")
        return

    # 🔹 Fix: Ensure ETA is properly formatted
    eta_seconds = added_torrent.get('eta', 0)
    if isinstance(eta_seconds, timedelta):
        eta_seconds = int(eta_seconds.total_seconds())
    elif not isinstance(eta_seconds, int) or eta_seconds < 0:
        eta_seconds = 0
    elif eta_seconds > 999999999:
        eta_seconds = 999999999

    eta_display = str(timedelta(seconds=eta_seconds)) if eta_seconds > 0 else "N/A"

    # 🔹 Fix: Ensure `files` is a list of strings
    file_list = added_torrent.get("files", [])
    if isinstance(file_list, PosixPath):
        file_list = [str(file_list)]
    elif isinstance(file_list, list):
        file_list = [str(file) for file in file_list]
    else:
        file_list = []

    file_list_display = "\n".join([f"📂 `{file}`" for file in file_list]) if file_list else "No files available yet."

    message = (
        f"📂 *Torrent Name:* `{added_torrent['name']}`\n"
        f"📊 *Progress:* `{added_torrent['progress']}%`\n"
        f"📌 *State:* `{added_torrent['status']}`\n"
        f"⏳ *ETA:* `{eta_display}`\n"
        f"🆔 *GID:* `{gid}`\n"
        f"📄 *Files:*\n{file_list_display}"
    )

    sent_message = await update.message.reply_text(message, parse_mode="Markdown")

    # Start tracking the torrent progress
    await track_torrent_progress(context, update.effective_chat.id, sent_message.message_id, gid)

async def track_torrent_progress(context, chat_id, message_id, gid):
    """
    Track the progress of a torrent and update the Telegram message in real-time.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        chat_id (int): Telegram chat ID.
        message_id (int): Telegram message ID.
        gid (str): The GID of the torrent.
    """
    global last_message  # Use a global variable to track last sent message
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        return

    retry_count = 0  # Track retries for fetching files

    while True:
        status = torrent_manager.get_torrent_status(gid)  # Get status from Aria2

        # 🔹 Debugging: Log the FULL status response from Aria2
        logger.info(f"DEBUG: Full Aria2 response (Attempt {retry_count}): {status}")

        if "error" in status:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⚠️ Error tracking torrent: `{status['error']}`",
                parse_mode="Markdown",
            )
            break

        progress = float(status["progress"].replace("%", ""))
        eta_display = "N/A"
        if isinstance(status.get("eta"), int) and status["eta"] > 0 and status["eta"] < 86400:
            eta_display = str(timedelta(seconds=status["eta"]))  # Convert seconds to readable time

        # 🔹 Debugging: Log what `files` contains
        raw_files = status.get("files", None)
        logger.info(f"DEBUG: Raw `files` data from Aria2 (Attempt {retry_count}): {raw_files}")

        if raw_files is None:
            retry_count += 1
            if retry_count <= 15:  # Retry up to 15 times before failing
                logger.warning(f"⚠️ Torrent metadata not ready yet, retrying ({retry_count}/15)...")
                await asyncio.sleep(5)  # Wait before retrying
                continue
            else:
                file_list = []  # Default to empty list after retries fail
        elif isinstance(raw_files, list):
            file_list = [str(file) for file in raw_files]
        else:
            logger.warning(f"⚠️ Unexpected file list type: {type(raw_files)} - Defaulting to empty list.")
            file_list = []

        file_list_display = "\n".join([f"📂 `{file}`" for file in file_list]) if file_list else "📡 Waiting for metadata..."

        # 🔹 Debugging: Log progress updates
        logger.info(f"DEBUG: Progress: {progress}%, ETA: {eta_display}, Files: {file_list_display}")

        torrent_name = status.get("name", "Unknown").replace("[METADATA]", "").strip()

        new_message = (
            f"📂 *Torrent Name:* `{torrent_name}`\n"
            f"📊 *Progress:* `{progress}%`\n"
            f"📌 *State:* `{status['status']}`\n"
            f"⏳ *ETA:* `{eta_display}`\n"
            f"🆔 *GID:* `{gid}`\n"
            f"📄 *Files:*\n{file_list_display}"
        )

        # 🔹 Prevent unnecessary message updates
        if new_message != last_message:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_message, parse_mode="Markdown")
            last_message = new_message  # Store last sent message

        if status["status"].lower() in ["seeding", "complete"]:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{new_message}\n✅ *Download Complete!*",
                parse_mode="Markdown",
            )
            break

        await asyncio.sleep(3)  # 🔹 Update every 3 seconds

