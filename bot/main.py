"""
Main module for the Torrent-to-GDrive Bot.

This module initializes the Telegram bot and listens for commands.
"""
import sys
import os
import time
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bot.torrent_manager import TorrentManager


# Add the project root directory to sys.path
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
    Handles the /status command.
    Sends the API status and bot uptime to the user.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    # Initialize TorrentManager with qBittorrent credentials
    manager = TorrentManager(
        host=context.bot_data.get("QB_HOST"),
        username=context.bot_data.get("QB_USERNAME"),
        password=context.bot_data.get("QB_PASSWORD")
    )

    # Check API and connection status
    api_status = manager.checkAPIOnlineAndConnectedStatus()
    bot_uptime = get_uptime()

    # Build the response message
    response = (
        f"API Status: {'✅ Online' if api_status['online'] else '❌ Offline'}\n"
        f"Connection Status: {'✅ Connected' if api_status['connected'] else '❌ Not Connected'}\n"
        f"Bot Uptime: {bot_uptime}"
    )

    await update.message.reply_text(response)

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
