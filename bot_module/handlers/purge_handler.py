# bot_module/handlers/purge_handler.py

from telegram import Update
from telegram.ext import ContextTypes
import logging
import asyncio

logger = logging.getLogger(__name__)

async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /purge command to delete messages in bulk after a specified message.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a message to specify where to start purging.")
        return

    chat_id = update.effective_chat.id
    start_message_id = update.message.reply_to_message.message_id
    current_message_id = update.message.message_id

    logger.info(f"🗑️ Purging messages from {start_message_id} to {current_message_id}.")

    # ✅ Collect all message IDs to delete
    message_ids = list(range(start_message_id, current_message_id + 1))

    # ✅ Check if batch delete is available
    try:
        # Bulk delete (if bot has the required permission)
        await context.bot.delete_messages(chat_id=chat_id, message_ids=message_ids)
        logger.info(f"✅ Bulk deleted {len(message_ids)} messages.")
        await update.message.reply_text(f"✅ Successfully purged {len(message_ids)} messages.")
        return
    except Exception as e:
        logger.warning(f"⚠️ Bulk deletion failed: {str(e)} - Switching to sequential deletion.")

    # 🔹 Fallback to individual deletion if batch fails
    deleted_count, failed_count = 0, 0
    for message_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            deleted_count += 1
        except Exception as e:
            failed_count += 1
            logger.warning(f"⚠️ Failed to delete message {message_id}: {str(e)}")

        await asyncio.sleep(0.1)  # Prevent hitting API limits

    # ✅ Final report
    result_message = (
        f"✅ *Purge Completed!*\n"
        f"🗑️ Total Deleted: `{deleted_count}`\n"
        f"⚠️ Failed Deletions: `{failed_count}`"
    )
    logger.info(result_message)
    await update.message.reply_text(result_message, parse_mode="Markdown")
