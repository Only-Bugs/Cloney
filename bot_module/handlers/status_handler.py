from telegram import Update
from telegram.ext import ContextTypes
import logging
import time
import json

logger = logging.getLogger(__name__)
BOT_STATE_FILE = "config/bot_state.json"  # ✅ Updated persistent location

def load_saved_start_time():
    """
    Loads the stored start time from bot_state.json.
    Returns None if the file doesn't exist.
    """
    try:
        with open(BOT_STATE_FILE, "r") as f:
            return json.load(f).get("start_time", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /status command to check Aria2 RPC status and bot uptime.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    start_time = context.bot_data.get("start_time", load_saved_start_time())
    if not start_time:
        uptime = "Unknown (Bot Restarted)"
    else:
        uptime_seconds = int(time.time() - start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{hours}h {minutes}m {seconds}s"

    status_message = (
        f"📡 *Aria2 RPC Status:* ✅ Online\n"
        f"⏳ *Bot Uptime:* `{uptime}`"
    )

    await update.message.reply_text(status_message, parse_mode="Markdown")
