"""
Main module for the Torrent-to-GDrive Bot.

This module initializes the Telegram bot and listens for commands.
"""
import sys
import os
import time
import logging
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot_module.torrent_manager import TorrentManager


# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from config.config import TELEGRAM_BOT_TOKEN

BOT_START_TIME = time.time()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    Sends a welcome message to the user.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    await update.message.reply_text("Welcome to my Bot! 🚀\nSend a torrent link to get started.")

def get_uptime():
    """
    Calculate the bot's uptime.
    Returns:
        str: Uptime in hours and minutes (e.g., '12h 34m').
    """
    uptime_seconds = time.time() - BOT_START_TIME
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /status command to check API status and system uptime.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    from datetime import timedelta

    # Get bot uptime
    bot_start_time = context.bot_data.get("start_time")
    uptime = timedelta(seconds=(time.time() - bot_start_time)) if bot_start_time else "Unknown"

    # API Connection Check
    api_status = "❌ Offline"
    connection_status = "❌ Not Connected"

    try:
        # Replace with the actual API health check endpoint
        api_url = "http://localhost:8080/api/v2/status"
        response = requests.get(api_url, timeout=5)
        print(f"API response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            api_status = "✅ Online"
        else:
            api_status = "❌ Offline"
    except Exception as e:
        print(f"Error while checking API status: {str(e)}")

    # Send the status message
    await update.message.reply_text(
        f"API Status: {api_status}\n"
        f"Connection Status: {connection_status}\n"
        f"Bot Uptime: {uptime}"
    )


async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /purge command to delete messages in the chat after a specified message.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    # Ensure the command is used as a reply to a message
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to specify where to start purging.")
        return

    # Get the message ID of the replied message
    start_message_id = update.message.reply_to_message.message_id
    current_message_id = update.message.message_id

    # Debug: Log the message range
    print(f"Purging messages from {start_message_id + 1} to {current_message_id - 1} in chat: {update.effective_chat.id}")

    deleted_count = 0
    try:
        # Iterate through the range of messages to delete
        for message_id in range(start_message_id + 1, current_message_id):
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                deleted_count += 1
                print(f"Deleted message with ID: {message_id}")
            except Exception as e:
                print(f"Failed to delete message ID {message_id}: {str(e)}")

    except Exception as e:
        await update.message.reply_text(f"Error while purging: {str(e)}")
        print(f"Error while deleting messages: {str(e)}")
        return

    # Debug: Log the number of messages deleted
    print(f"Successfully purged {deleted_count} messages.")

    # Send feedback to the user
    await update.message.reply_text(f"Purged {deleted_count} messages successfully.")


def main():
    """
    Initializes the Telegram bot and sets up command handlers.
    """
    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("purge", purge))

    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
