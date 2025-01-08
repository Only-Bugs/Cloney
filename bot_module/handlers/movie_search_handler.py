from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from tmdbv3api import TMDb, Movie
import logging

# TMDb API Initialization
tmdb = TMDb()
tmdb.api_key = "YOUR_TMDB_API_KEY"  # Replace with your TMDb API key
tmdb.language = "en"
tmdb.debug = True

logger = logging.getLogger(__name__)

async def movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Detects a text message as a potential movie search query and uses TMDb API to fetch results.
    """
    user_message = update.message.text.strip()

    # Ignore commands
    if user_message.startswith("/"):
        return

    logger.info(f"Received potential movie search query: {user_message}")

    # Search for movies using TMDb API
    movie = Movie()
    search_results = movie.search(user_message)

    if not search_results:
        await update.message.reply_text("No results found for your query.")
        return

    # Create inline keyboard with results
    keyboard = [
        [InlineKeyboardButton(f"{result['title']} ({result['release_date'][:4] if result['release_date'] else 'N/A'})",
                              callback_data=result['id'])]
        for result in search_results[:5]  # Limit to the first 5 results
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Results for: {user_message}",
        reply_markup=reply_markup,
    )



async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles button clicks for search results.
    """
    query = update.callback_query
    await query.answer()

    movie_id = query.data
    logger.info(f"Selected movie ID: {movie_id}")

    # Fetch movie details from TMDb API
    movie = Movie()
    movie_details = movie.details(movie_id)

    # Extract relevant info
    title = movie_details.get("title", "N/A")
    overview = movie_details.get("overview", "No description available.")
    release_date = movie_details.get("release_date", "N/A")
    vote_average = movie_details.get("vote_average", "N/A")

    # Prepare the message
    message = (
        f"🎬 *{title}*\n"
        f"📅 Release Date: {release_date}\n"
        f"⭐ Rating: {vote_average}/10\n\n"
        f"📖 Description:\n{overview}\n"
    )

    # Respond with movie details
    await query.edit_message_text(text=message, parse_mode="Markdown")
