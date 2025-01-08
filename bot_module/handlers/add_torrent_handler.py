from telegram import Update
from telegram.ext import ContextTypes
import logging
import asyncio

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

    # Add the torrent
    response = torrent_manager.add_torrent(magnet_link)
    if "successfully" not in response.lower():
        logger.error(f"Failed to add torrent: {response}")
        await update.message.reply_text(response)
        return

    logger.info("Torrent added successfully. Waiting for details...")
    await asyncio.sleep(2)  # Add a small delay to let qBittorrent process the torrent

    # Retry fetching torrent details
    added_torrent = None
    for attempt in range(10):  # Retry up to 10 times
        torrents = torrent_manager.list_torrents()
        if "error" in torrents:
            logger.warning(f"Error fetching torrents on attempt {attempt + 1}: {torrents['error']}")
            await asyncio.sleep(2)  # Wait for 2 seconds before retrying
            continue

        # Match torrent by multiple criteria
        for torrent in torrents:
            if magnet_link in torrent.get("name", "") or magnet_link in torrent.get("hash", ""):
                added_torrent = torrent
                break

        if added_torrent:
            logger.info(f"Torrent details fetched successfully on attempt {attempt + 1}.")
            break

        logger.info(f"Retrying... Attempt {attempt + 1}")
        await asyncio.sleep(2)  # Wait for 2 seconds before the next attempt

    if not added_torrent:
        logger.error("Failed to fetch torrent details after multiple attempts.")
        await update.message.reply_text("Torrent added, but unable to fetch details after multiple attempts.")
        return

    torrent_hash = added_torrent["hash"]
    message = (
        f"Torrent Name: {added_torrent['name']}\n"
        f"Progress: {added_torrent['progress']}%\n"
        f"State: {added_torrent['state']}\n"
        f"ETA: {added_torrent['eta']} seconds\n"
        f"Torrent Hash: {torrent_hash}"
    )
    sent_message = await update.message.reply_text(message)

    # Start tracking the torrent progress
    await track_torrent_progress(context, update.effective_chat.id, sent_message.message_id, torrent_hash)


async def track_torrent_progress(context, chat_id, message_id, torrent_hash):
    """
    Track the progress of a torrent and update the Telegram message.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
        chat_id (int): Telegram chat ID.
        message_id (int): Telegram message ID.
        torrent_hash (str): The hash of the torrent.
    """
    torrent_manager = context.bot_data.get("torrent_manager")
    if not torrent_manager:
        return

    while True:
        status = torrent_manager.get_torrent_status(torrent_hash)
        if "error" in status:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"Error tracking torrent: {status['error']}",
            )
            break

        progress = float(status["progress"].replace("%", ""))
        progress_bar = f"[{'=' * int(progress // 10)}{' ' * (10 - int(progress // 10))}] {progress:.2f}%"

        new_message = (
            f"Torrent Name: {status.get('name', 'N/A')}\n"
            f"Progress: {progress_bar}\n"
            f"State: {status['state']}\n"
            f"ETA: {status['eta']} seconds\n"
            f"Torrent Hash: {torrent_hash}"
        )

        await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_message)

        if status["state"].lower() in ["seeding", "completed"]:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"{new_message}\nStatus: Torrent is now {status['state']}.",
            )
            break

        await asyncio.sleep(5)
