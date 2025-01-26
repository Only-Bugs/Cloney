# bot_module/handlers/movie_search_handler.py

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from tmdbv3api import TMDb, Movie
from config.config import TMDB_API_KEY  # Fetch TMDb API Key from config

# ✅ Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# ✅ Setup Separate Movie Search Logger
MOVIE_SEARCH_LOG_FILE = "logs/movie_search.log"
movie_search_logger = logging.getLogger("movie_search_logger")

file_handler = logging.FileHandler(MOVIE_SEARCH_LOG_FILE)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
movie_search_logger.addHandler(file_handler)

# ✅ TMDb API Initialization
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY  # Pulled from config
tmdb.language = "en"
tmdb.debug = False  # Debugging disabled for production

async def movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Detects a text message as a potential movie search query and fetches results from TMDb API.

    Args:
        update (Update): Incoming Telegram update.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    user_message = update.message.text.strip()

    # Ignore if the message is a command
    if user_message.startswith("/"):
        return

    movie_search_logger.info(f"🔍 User Search Query: {user_message}")

    movie = Movie()
    try:
        search_results = movie.search(user_message)
        search_results = list(search_results)  # ✅ Convert to list before slicing
    except Exception as e:
        movie_search_logger.error(f"❌ TMDb API Error: {str(e)}")
        await update.message.reply_text("⚠️ An error occurred while searching for the movie. Please try again later.")
        return

    if not search_results:
        movie_search_logger.info(f"❌ No results found for query: {user_message}")
        await update.message.reply_text("⚠️ No results found for your query. Please refine your search.")
        return

    # ✅ Log the first 5 results
    movie_search_logger.info(f"🎥 Search Results for '{user_message}': {[m.title for m in search_results[:5]]}")

    # ✅ Create inline keyboard with search results (limit to 5 results)
    keyboard = []
    for result in search_results[:100]:  # ✅ Now slicing works as expected
        title = result.title
        release_year = result.release_date[:4] if result.release_date else "N/A"
        keyboard.append([InlineKeyboardButton(f"{title} ({release_year})", callback_data=str(result.id))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🔎 *Results for:* `{user_message}`",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles button clicks for search results, fetching detailed movie info from TMDb.

    Args:
        update (Update): Incoming Telegram update with callback query.
        context (ContextTypes.DEFAULT_TYPE): Telegram bot context.
    """
    query = update.callback_query
    await query.answer()

    movie_id = query.data
    movie_search_logger.info(f"🎥 User selected movie ID: {movie_id}")

    movie = Movie()
    try:
        movie_details = movie.details(movie_id)
    except Exception as e:
        movie_search_logger.error(f"❌ Failed to fetch movie details for ID {movie_id}: {str(e)}")
        await query.edit_message_text("⚠️ Unable to fetch movie details. Please try again later.")
        return

    # Extract relevant info
    title = movie_details.get("title", "N/A")
    overview = movie_details.get("overview", "No description available.")
    release_date = movie_details.get("release_date", "N/A")
    vote_average = movie_details.get("vote_average", "N/A")

    # ✅ Log movie selection
    movie_search_logger.info(f"📜 Movie Details Retrieved: {title} (ID: {movie_id})")

    # ✅ Prepare response message
    message = (
        f"🎬 *{title}*\n"
        f"📅 *Release Date:* `{release_date}`\n"
        f"⭐ *Rating:* `{vote_average}/10`\n\n"
        f"📖 *Overview:*\n_{overview}_"
    )

    # ✅ Respond with movie details
    await query.edit_message_text(text=message, parse_mode="Markdown")
