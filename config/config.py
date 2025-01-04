# config/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "config.env"))

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Google Drive Folder ID
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

# qBittorrent Configurations
QB_HOST = os.getenv("QB_HOST")
QB_USERNAME = os.getenv("QB_USERNAME")
QB_PASSWORD = os.getenv("QB_PASSWORD")
