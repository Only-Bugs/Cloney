# bot_module/handlers/status_handler.py

from telegram import Update
from telegram.ext import ContextTypes
from datetime import timedelta
import time


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /status command to check API status and system uptime.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    # Initialize API statuses
    api_status = "❌ Offline"
    connection_status = "❌ Not Connected"
    error_message = None

    try:
        torrent_manager = context.bot_data["torrent_manager"]
        status_result = torrent_manager.check_api_status()
        api_status = "✅ Online" if status_result.get("online") else "❌ Offline"
        connection_status = "✅ Connected" if status_result.get("connected") else "❌ Not Connected"
        error_message = status_result.get("error")
    except KeyError:
        error_message = "TorrentManager not initialized"
    except Exception as e:
        error_message = f"Error: {str(e)}"

    # Get bot uptime
    uptime_seconds = time.time() - context.bot_data.get("start_time", time.time())
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, _ = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m"

    # Prepare the status message
    status_message = (
        f"API Status: {api_status}\n"
        f"Connection Status: {connection_status}\n"
        f"Bot Uptime: {uptime}\n"
    )
    if error_message:
        status_message += f"Error: {error_message}\n"

    # Send the status message
    await update.message.reply_text(status_message)
