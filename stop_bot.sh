#!/bin/bash

echo "🛑 Stopping bot and cleaning up..."

# ✅ Kill all Aria2 processes
ARIA2_COUNT=$(pgrep -x "aria2c" | wc -l)
if [[ $ARIA2_COUNT -gt 0 ]]; then
    pkill -f aria2c
    echo "✅ Stopped $ARIA2_COUNT instance(s) of Aria2!"
else
    echo "⚠️ Aria2 was not running."
fi

# ✅ Kill all Python bot processes
BOT_COUNT=$(pgrep -f "python3 -m bot_module.main" | wc -l)
if [[ $BOT_COUNT -gt 0 ]]; then
    pkill -f "python3 -m bot_module.main"
    echo "✅ Stopped $BOT_COUNT instance(s) of the bot!"
else
    echo "⚠️ Bot was not running."
fi

# ✅ Wait for processes to fully terminate
sleep 2

# ✅ Delete logs directory
LOG_DIR="logs"
if [[ -d "$LOG_DIR" ]]; then
    rm -rf "$LOG_DIR"
    if [[ ! -d "$LOG_DIR" ]]; then
        echo "🗑️  Logs directory deleted successfully!"
    else
        echo "❌ Failed to delete logs directory!"
    fi
else
    echo "⚠️ No logs directory found, skipping cleanup."
fi

DOWNLOAD_DIR="downloads"
if [[ -d "$DOWNLOAD_DIR" ]]; then
    rm -rf "$DOWNLOAD_DIR"
    if [[ ! -d "$DOWNLOAD_DIR" ]]; then
        echo "🗑️  Downloads directory deleted successfully!"
    else
        echo "❌ Failed to delete download directory!"
    fi
else
    echo "⚠️ No downloads directory found, skipping cleanup."
fi

echo "✅ Cleanup complete. All processes stopped!"
