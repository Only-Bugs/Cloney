#!/bin/bash

echo "🛑 Stopping Aria2 and Torrent-to-GDrive Bot..."

# Kill Aria2 process
if pgrep -x "aria2c" > /dev/null; then
    pkill -f aria2c
    echo "✅ Aria2 stopped successfully!"
else
    echo "⚠️ Aria2 was not running."
fi

# Kill Python bot process
if pgrep -f "python3 -m bot_module.main" > /dev/null; then
    pkill -f "python3 -m bot_module.main"
    echo "✅ Bot stopped successfully!"
else
    echo "⚠️ Bot was not running."
fi

echo "🛑 All processes stopped!"
