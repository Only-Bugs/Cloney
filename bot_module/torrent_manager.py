# bot/torrent_manager.py
import qbittorrentapi
from datetime import timedelta

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
            self.client.auth_log_in()
            return True
        except qbittorrentapi.LoginFailed:
            return False
        except qbittorrentapi.APIConnectionError:
            return False

    def check_api_status(self):
        """
        Check if the qBittorrent API is reachable and authenticated.

        Returns:
            dict: A dictionary with 'online' and 'connected' statuses.
        """
        status = {"online": False, "connected": False, "error": None}
        try:
            status["online"] = self.client.app_version() is not None
            status["connected"] = self.is_connected()
        except qbittorrentapi.APIConnectionError as e:
            status["error"] = f"API connection error: {str(e)}"
        except qbittorrentapi.LoginFailed as e:
            status["error"] = f"Login failed: {str(e)}"
        except Exception as e:
            status["error"] = f"Unexpected error: {str(e)}"
        return status

    def add_torrent(self, magnet_link):
        """
        Add a magnet link to qBittorrent.

        Args:
            magnet_link (str): The magnet link to add.

        Returns:
            str: A success message or an error message.
        """
        try:
            self.client.torrents_add(urls=magnet_link)
            return "Torrent added successfully!"
        except qbittorrentapi.InvalidRequestError as e:
            return f"Invalid request: {str(e)}"
        except Exception as e:
            return f"Error adding torrent: {str(e)}"

    def list_torrents(self):
        """
        List all torrents in qBittorrent.

        Returns:
            list: A list of dictionaries containing torrent information.
        """
        try:
            torrents = self.client.torrents_info()
            return [
                {
                    "hash": torrent.hash,
                    "name": torrent.name,
                    "state": torrent.state,
                    "progress": f"{torrent.progress * 100:.2f}",
                    "eta": torrent.eta,
                }
                for torrent in torrents
            ]
        except Exception as e:
            return {"error": str(e)}

    def get_torrent_status(self, torrent_hash):
        """
        Get the status of a torrent.

        Args:
            torrent_hash (str): The hash of the torrent.

        Returns:
            dict: Status information of the torrent or an error message.
        """
        try:
            torrent = self.client.torrents_info(torrent_hashes=torrent_hash)
            if torrent:
                eta_seconds = torrent[0].eta
                eta = str(timedelta(seconds=eta_seconds)) if eta_seconds > 0 else "N/A"

                return {
                    "name": torrent[0].name,
                    "state": torrent[0].state,
                    "progress": f"{torrent[0].progress * 100:.2f}%",
                    "eta": eta,
                }
            else:
                return {"error": "Torrent not found."}
        except Exception as e:
            return {"error": str(e)}
