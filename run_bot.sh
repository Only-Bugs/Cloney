#!/bin/bash

echo "🚀 Starting Aria2 and Torrent-to-GDrive Bot..."

# Activate virtual environment
source myenv/bin/activate

# Navigate to the project root directory
cd "$(dirname "$0")"

# Start Aria2 in the background and redirect logs
aria2c --conf-path=/Users/malfunctxn/Code/Cloney/aria2.conf --daemon=true >> logs/aria2.log 2>&1 &

# Wait for Aria2 to initialize (adjust time if necessary)
sleep 3

# Check if Aria2 started successfully
if pgrep -x "aria2c" > /dev/null; then
    echo "✅ Aria2 started successfully!"
else
    echo "❌ Failed to start Aria2. Check logs/aria2.log for details."
    exit 1
fi

# Start the bot with watchmedo (auto-restart on file changes)
watchmedo auto-restart --recursive --pattern="*.py" -- python3 -m bot_module.main &

# Wait for the bot to log "Application started"
echo "⌛ Waiting for the bot to initialize..."
sleep 5  # Adjust this if needed

# Monitor the bot logs and confirm it has started
if grep -q "Application started" logs/bot_logs.log; then
    echo "✅ Bot started successfully! 🚀"
else
    echo "❌ Bot failed to start. Check logs/bot_logs.log for details."
    exit 1
fi
