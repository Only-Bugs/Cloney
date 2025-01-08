# tests/test_torrent_manager.py
import sys
import os
import pytest
from unittest.mock import MagicMock
from bot.torrent_manager import TorrentManager
import qbittorrentapi

# Ensure the root directory is in the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

@pytest.fixture
def mock_config():
    """
    Mock configuration for qBittorrent connection.
    """
    return {
        "host": "http://localhost:8080",
        "username": "admin",
        "password": "adminadmin"
    }

@pytest.fixture
def mock_qbittorrent_client(monkeypatch):
    """
    Mock the qBittorrent client.
    """
    mock_client = MagicMock()
    monkeypatch.setattr("qbittorrentapi.Client", lambda *args, **kwargs: mock_client)
    return mock_client

def test_is_connected_success(mock_config, mock_qbittorrent_client):
    """
    Test if is_connected() returns True when authentication succeeds.
    """
    # Mock successful login
    mock_qbittorrent_client.auth_log_in.return_value = None

    manager = TorrentManager(mock_config["host"], mock_config["username"], mock_config["password"])
    assert manager.is_connected() is True, "is_connected() should return True for successful authentication"

def test_is_connected_failure(mock_config, mock_qbittorrent_client):
    """
    Test if is_connected() returns False when authentication fails.
    """
    # Mock failed login
    mock_qbittorrent_client.auth_log_in.side_effect = qbittorrentapi.LoginFailed

    manager = TorrentManager(mock_config["host"], mock_config["username"], mock_config["password"])
    assert manager.is_connected() is False, "is_connected() should return False for failed authentication"

def test_checkAPIOnlineAndConnectedStatus_success(mock_config, mock_qbittorrent_client):
    """
    Test if checkAPIOnlineAndConnectedStatus returns correct statuses for online and connected.
    """
    # Mock successful API version check and login
    mock_qbittorrent_client.app_version.return_value = "4.3.9"
    mock_qbittorrent_client.auth_log_in.return_value = None

    manager = TorrentManager(mock_config["host"], mock_config["username"], mock_config["password"])
    status = manager.checkAPIOnlineAndConnectedStatus()
    assert status["online"] is True, "API should be online when app_version() succeeds"
    assert status["connected"] is True, "API should be connected when auth_log_in() succeeds"

def test_checkAPIOnlineAndConnectedStatus_offline(mock_config, mock_qbittorrent_client):
    """
    Test if checkAPIOnlineAndConnectedStatus returns False for 'online' when API is unreachable.
    """
    # Mock API connection error
    mock_qbittorrent_client.app_version.side_effect = qbittorrentapi.APIConnectionError

    manager = TorrentManager(mock_config["host"], mock_config["username"], mock_config["password"])
    status = manager.checkAPIOnlineAndConnectedStatus()
    assert status["online"] is False, "API should be offline when app_version() fails"
    assert status["connected"] is False, "API should not be connected when offline"
