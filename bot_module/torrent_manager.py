from aria2p import API, Client
from datetime import timedelta
import logging
from pathlib import Path  # Import Path module to check PosixPath issues

logger = logging.getLogger(__name__)

class TorrentManager:
    """
    A manager to interact with aria2 via its RPC API.
    """

    def __init__(self, host="http://localhost", port=6800, secret=None):
        """
        Initialize the aria2 client.

        Args:
            host (str): The RPC server host (default: "http://localhost").
            port (int): The RPC server port (default: 6800).
            secret (str): The RPC secret token (default: None).
        """
        self.client = Client(host=host, port=port, secret=secret)
        self.api = API(self.client)

    def is_connected(self):
        """
        Check if the aria2 RPC API is online.

        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            self.api.get_version()
            return True
        except Exception:
            return False

    def check_api_status(self):
        """
        Check if the aria2 RPC API is reachable and authenticated.

        Returns:
            dict: A dictionary with 'online' and 'error' statuses.
        """
        status = {"online": False, "error": None}
        try:
            status["online"] = self.is_connected()
        except Exception as e:
            status["error"] = f"Error connecting to aria2: {str(e)}"
        return status

    def add_torrent(self, torrent_url: str) -> str:
        """
        Add a torrent to aria2.
        :param torrent_url: Magnet link or direct URL of the torrent.
        :return: GID of the torrent or error message.
        """
        try:
            if torrent_url.startswith("magnet:"):
                torrent = self.api.add_magnet(torrent_url)
            else:
                torrent = self.api.add_uris([torrent_url])

            return torrent.gid  # Return the GID of the added torrent
        except Exception as e:
            return f"Error adding torrent: {str(e)}"



    def list_torrents(self):
        """
        List all active downloads in aria2.

        Returns:
            list: A list of dictionaries containing torrent information.
        """
        try:
            downloads = self.api.get_downloads()
            return [
                {
                    "gid": download.gid,
                    "name": download.name,
                    "status": download.status,
                    "progress": f"{(download.completed_length / download.total_length) * 100:.2f}%" if download.total_length > 0 else "0%",
                    "eta": int(download.eta.total_seconds()) if isinstance(download.eta, timedelta) else download.eta or 0,
                }
                for download in downloads
            ]
        except Exception as e:
            return {"error": str(e)}

    def get_torrent_status(self, gid):
        """
        Fetches the status of a torrent by its GID from Aria2.
        """
        try:
            # 🔹 Fetch raw response from Aria2
            download = self.api.get_download(gid)
            return {
                "name": download.name,
                "status": download.status,
                "progress": f"{(download.completed_length / download.total_length) * 100:.2f}%" if download.total_length > 0 else "0%",
                "eta": int(download.eta.total_seconds()) if isinstance(download.eta, timedelta) else download.eta or 0,
                "download_speed": f"{download.download_speed / 1024:.2f} KB/s",
            }


            # 🔹 Debugging: Log raw response from Aria2
            logger.info(f"DEBUG: Raw Aria2 response for GID {gid}: {status}")

            # 🔹 Fix: Convert all PosixPath objects to strings before returning
            if isinstance(status, dict):  # Ensure status is a dictionary
                for key, value in status.items():
                    if isinstance(value, Path):  # Convert PosixPath to string
                        status[key] = str(value)
                    elif isinstance(value, list):  # If list, convert elements
                        status[key] = [str(item) if isinstance(item, Path) else item for item in value]

            return status

        except Exception as e:
            logger.error(f"❌ Error fetching torrent status: {str(e)}")
            return {"error": str(e)}




    def remove_torrent(self, gid, remove_files=True):
        """
        Remove a download by its GID.

        Args:
            gid (str): The GID of the download.
            remove_files (bool): Whether to delete the downloaded files as well.

        Returns:
            str: Success or error message.
        """
        try:
            if remove_files:
                self.api.remove_download(gid, force=True)
                self.api.remove_download_result(gid)
            else:
                self.api.remove_download(gid)
            return f"Torrent with GID {gid} removed successfully."
        except Exception as e:
            return f"Error removing torrent: {str(e)}"
