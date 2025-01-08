# bot_module/handlers/purge_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import asyncio
import logging

logger = logging.getLogger(__name__)

async def delete_message(context, chat_id, message_id):
    """
    Helper function to delete a single message.

    Args:
        context: Telegram bot context.
        chat_id: ID of the chat where the message should be deleted.
        message_id: ID of the message to be deleted.
    """
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted message with ID: {message_id}")
    except Exception as e:
        logger.error(f"Failed to delete message ID {message_id}: {str(e)}")


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

    # Get the message IDs for purging
    start_message_id = update.message.reply_to_message.message_id
    current_message_id = update.message.message_id

    # Collect all message IDs to delete
    message_ids_to_delete = range(start_message_id + 1, current_message_id)

    # Debug: Log the range of messages to delete
    logger.info(f"Purging messages from {start_message_id + 1} to {current_message_id - 1} in chat: {update.effective_chat.id}")

    # Delete messages concurrently
    tasks = [
        delete_message(context, chat_id=update.effective_chat.id, message_id=message_id)
        for message_id in message_ids_to_delete
    ]
    deleted_count = 0
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        deleted_count = sum(1 for result in results if result is None)
    except Exception as e:
        logger.error(f"Error while purging messages: {str(e)}")
        await update.message.reply_text(f"Error while purging: {str(e)}")
        return

    # Debug: Log the number of messages deleted
    logger.info(f"Successfully purged {deleted_count} messages.")

    # Send feedback to the user
    await update.message.reply_text(f"Purged {deleted_count} messages successfully.")
