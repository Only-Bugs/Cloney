# bot_module/handlers/purge_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /purge command to delete messages in the chat after a specified message.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to specify where to start purging.")
        return

    start_message_id = update.message.reply_to_message.message_id
    current_message_id = update.message.message_id

    deleted_count = 0
    try:
        for message_id in range(start_message_id + 1, current_message_id):
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete message ID {message_id}: {str(e)}")

    except Exception as e:
        await update.message.reply_text(f"Error while purging: {str(e)}")
        logger.error(f"Error while purging messages: {str(e)}")
        return

    await update.message.reply_text(f"Purged {deleted_count} messages successfully.")
