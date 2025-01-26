# config/config.py

"""
Configuration module for the Torrent-to-GDrive bot.

This module:
- Loads environment variables from the `.env` file.
- Sets up logging for configuration-related issues.
- Defines and validates critical configuration variables.
"""

import os
import logging
from dotenv import load_dotenv

# Logging setup for configuration-related issues
LOG_DIR = "logs"
CONFIG_LOG_FILE = os.path.join(LOG_DIR, "config.log")

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger for the configuration module
config_logger = logging.getLogger(__name__)
config_logger.setLevel(logging.INFO)

# Create file handler for logging
file_handler = logging.FileHandler(CONFIG_LOG_FILE)
file_handler.setLevel(logging.INFO)

# Define log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Apply handlers to logger
config_logger.addHandler(file_handler)

# Load environment variables from the `.env` file
ENV_PATH = os.path.join(os.path.dirname(__file__), "config.env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    config_logger.info(f"Environment variables successfully loaded from {ENV_PATH}.")
else:
    config_logger.warning("Configuration file (config.env) not found. Ensure it is set up correctly.")

# Define essential configuration variables

# Telegram bot token (required)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    config_logger.error("Missing TELEGRAM_BOT_TOKEN. The bot will not function correctly.")

# Google Drive folder ID (optional, for future Google Drive integration)
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID", None)  # Defaults to None if not set

# TMDb API key (required for movie search functionality)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    config_logger.warning("TMDB_API_KEY is not set. Movie search functionality may be unavailable.")

# Log summary of loaded configuration variables (without exposing sensitive values)
config_logger.info("Configuration Loaded:")
config_logger.info(f"- TELEGRAM_BOT_TOKEN: {'Configured' if TELEGRAM_BOT_TOKEN else 'Not Set'}")
config_logger.info(f"- GDRIVE_FOLDER_ID: {'Configured' if GDRIVE_FOLDER_ID else 'Not Configured'}")
config_logger.info(f"- TMDB_API_KEY: {'Configured' if TMDB_API_KEY else 'Not Set'}")
