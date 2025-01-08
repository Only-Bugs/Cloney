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
    Handles the /purge command to delete messages in the chat after a specified message,
    with real-time progress updates.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a message to specify where to start purging.")
        return

    start_message_id = update.message.reply_to_message.message_id
    current_message_id = update.message.message_id

    logger.info(f"Purging messages from {start_message_id} to {current_message_id}.")
    deleted_count = 0
    failed_count = 0

    # Send an initial message to indicate the purge is starting
    feedback_message = await update.message.reply_text("Purging messages...")

    try:
        # First delete the selected (replied-to) message
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=start_message_id)
            deleted_count += 1
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to delete the selected message {start_message_id}: {str(e)}")

        # Delete all messages in the range and update progress
        for index, message_id in enumerate(range(start_message_id + 1, current_message_id), start=1):
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                deleted_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to delete message {message_id}: {str(e)}")

            # Update the feedback message every 5 messages
            if index % 5 == 0 or index == (current_message_id - start_message_id):
                progress_message = (
                    f"Purging messages...\n"
                    f"Deleted: {deleted_count}\n"
                    f"Failed: {failed_count}\n"
                    f"Remaining: {current_message_id - message_id - 1}"
                )
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=feedback_message.message_id, text=progress_message)

    except Exception as e:
        logger.error(f"Error during purge operation: {str(e)}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=feedback_message.message_id,
            text=f"Error while purging messages: {str(e)}",
        )
        return

    # Final update to indicate the purge is complete
    final_message = (
        f"Purging completed!\n"
        f"Total Deleted: {deleted_count}\n"
        f"Failed Deletions: {failed_count}"
    )
    logger.info(final_message)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=feedback_message.message_id, text=final_message)


