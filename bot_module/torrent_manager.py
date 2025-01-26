from aria2p import API, Client
from datetime import timedelta
import logging
from pathlib import Path  # Import Path module to check PosixPath issues

# ✅ Setup Logger
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
            self.client.get_version()
            return True
        except Exception as e:
            logger.error(f"❌ Connection to Aria2 failed: {str(e)}")
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
            logger.error(f"⚠️ {status['error']}")
        return status

    def add_torrent(self, torrent_url: str) -> str:
        """
        Add a torrent to aria2.

        Args:
            torrent_url (str): Magnet link or direct URL of the torrent.

        Returns:
            str: GID of the torrent or error message.
        """
        try:
            if torrent_url.startswith("magnet:"):
                torrent = self.api.add_magnet(torrent_url)
            else:
                torrent = self.api.add_uris([torrent_url])

            logger.info(f"✅ Torrent added successfully! GID: {torrent.gid}")
            return torrent.gid  # Return the GID of the added torrent
        except Exception as e:
            logger.error(f"❌ Error adding torrent: {str(e)}")
            return f"Error adding torrent: {str(e)}"

    def list_torrents(self):
        """
        List all active downloads in aria2.

        Returns:
            list: A list of dictionaries containing torrent information.
        """
        try:
            downloads = self.api.get_downloads()
            torrent_list = []
            for download in downloads:
                eta_value = (
                    int(download.eta.total_seconds()) if isinstance(download.eta, timedelta) else download.eta or 0
                )

                torrent_list.append({
                    "gid": download.gid,
                    "name": download.name,
                    "status": download.status,
                    "progress": f"{(download.completed_length / download.total_length) * 100:.2f}%" if download.total_length > 0 else "0%",
                    "eta": eta_value,
                })
            return torrent_list
        except Exception as e:
            logger.error(f"❌ Error listing torrents: {str(e)}")
            return {"error": str(e)}

    def get_torrent_status(self, gid):
        """
        Fetches the status of a torrent by its GID from Aria2.

        Args:
            gid (str): The GID of the torrent.

        Returns:
            dict: Torrent status details or an error message.
        """
        try:
            # 🔹 Fetch raw response from Aria2
            download = self.api.get_download(gid)

            # 🔹 Convert PosixPath to string before returning
            def safe_convert(value):
                if isinstance(value, Path):
                    return str(value)
                elif isinstance(value, list):
                    return [str(item) if isinstance(item, Path) else item for item in value]
                return value

            status = {
                "name": safe_convert(download.name),
                "status": download.status,
                "progress": f"{(download.completed_length / download.total_length) * 100:.2f}%" if download.total_length > 0 else "0%",
                "eta": int(download.eta.total_seconds()) if isinstance(download.eta, timedelta) else download.eta or 0,
                "download_speed": f"{download.download_speed / 1024:.2f} KB/s",
                "files": safe_convert(download.files)  # Fix for PosixPath issue
            }

            logger.info(f"✅ Torrent status fetched: {status}")
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

            logger.info(f"✅ Torrent with GID {gid} removed successfully.")
            return f"Torrent with GID {gid} removed successfully."
        except Exception as e:
            logger.error(f"❌ Error removing torrent: {str(e)}")
            return f"Error removing torrent: {str(e)}"
