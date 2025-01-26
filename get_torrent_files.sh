#!/bin/bash

# Check if Aria2 is installed
if ! command -v aria2c &> /dev/null
then
    echo "❌ Error: aria2c (Aria2) is not installed. Install it using:"
    echo "   sudo apt install aria2   # (Debian/Ubuntu)"
    echo "   brew install aria2       # (MacOS)"
    echo "   pacman -S aria2          # (Arch Linux)"
    exit 1
fi

# Check if a magnet link was provided
if [ -z "$1" ]; then
    echo "⚠️  Usage: ./get_torrent_files.sh '<magnet_link>'"
    exit 1
fi

MAGNET_LINK="$1"

# Start Aria2 in daemon mode if it's not running
ARIA2C_RUNNING=$(pgrep -x aria2c)
if [ -z "$ARIA2C_RUNNING" ]; then
    echo "🚀 Starting Aria2 daemon..."
    aria2c --enable-rpc --rpc-listen-all=true --daemon=true
    sleep 2
fi

# Send JSON-RPC request to Aria2
echo "🔍 Adding magnet link to Aria2..."
GID=$(curl -s -X POST http://localhost:6800/jsonrpc \
    --data '{"jsonrpc":"2.0","method":"aria2.addUri","id":"qwer","params":[[],["'"$MAGNET_LINK"'"]]}' \
    | jq -r '.result')

if [ -z "$GID" ] || [ "$GID" == "null" ]; then
    echo "❌ Failed to add torrent. Is the magnet link valid?"
    exit 1
fi

echo "✅ Torrent added successfully! GID: $GID"
echo "⏳ Waiting for metadata to resolve..."

# Wait for metadata resolution
sleep 10

# Fetch torrent info
echo "📂 Fetching file list..."
FILES=$(curl -s -X POST http://localhost:6800/jsonrpc \
    --data '{"jsonrpc":"2.0","method":"aria2.tellStatus","id":"qwer","params":["'"$GID"'"]]}' \
    | jq -r '.result.files[] | "\(.path) - \(.completedLength)B / \(.length)B"')

if [ -z "$FILES" ]; then
    echo "❌ No files found. Metadata may still be loading. Try again later."
else
    echo "$FILES"
fi

echo "✅ Done!"
