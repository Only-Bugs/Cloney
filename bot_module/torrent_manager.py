# bot/torrent_manager.py
import qbittorrentapi

from config.config import QB_HOST, QB_USERNAME, QB_PASSWORD


class TorrentManager:
    """
    A manager to interact with qBittorrent's Web API.
    """
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.client = qbittorrentapi.Client(host=host, username=username, password=password)

    def is_connected(self):
        """
        Check if the qBittorrent Web API is online and authenticated.

        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            # Attempt to authenticate with qBittorrent API
            self.client.auth_log_in()
            return True
        except qbittorrentapi.LoginFailed:
            return False
        except qbittorrentapi.APIConnectionError:
            return False

    def checkAPIOnlineAndConnectedStatus(self):
        """
        Check if the qBittorrent API is reachable and the client is authenticated.

        Returns:
            dict: A dictionary containing 'online' and 'connected' statuses.
        """
        online = False
        connected = False
        try:
            # Check API uptime
            online = self.client.app_version() is not None
            # Check if the client is authenticated
            connected = self.is_connected()
        except qbittorrentapi.APIConnectionError:
            online = False
        except qbittorrentapi.LoginFailed:
            connected = False
        return {"online": online, "connected": connected}

    def main():
        """
        Initializes the Telegram bot and sets up command handlers.
        """
        # Initialize the bot application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Add configuration to bot_data
        application.bot_data.update({
            "QB_HOST": QB_HOST,
            "QB_USERNAME": QB_USERNAME,
            "QB_PASSWORD": QB_PASSWORD
        })

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("status", status))

        # Start the bot
        logger.info("Bot is starting...")
        application.run_polling()