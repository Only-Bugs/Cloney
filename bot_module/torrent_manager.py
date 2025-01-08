# bot/torrent_manager.py
import qbittorrentapi


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
            dict: A dictionary containing 'online', 'connected', and 'error' (if any).
        """
        status = {"online": False, "connected": False, "error": None}
        try:
            # Check API uptime
            if self.client.app_version():
                status["online"] = True
            else:
                status["online"] = False

            # Check if the client is authenticated
            if self.is_connected():
                status["connected"] = True
            else:
                status["connected"] = False

        except qbittorrentapi.APIConnectionError as e:
            status["error"] = f"API connection error: {str(e)}"
        except qbittorrentapi.LoginFailed as e:
            status["error"] = f"Login failed: {str(e)}"
        except Exception as e:
            status["error"] = f"Unexpected error: {str(e)}"

        print(f"DEBUG: checkAPIOnlineAndConnectedStatus() -> {status}")
        return status
