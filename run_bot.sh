#!/bin/bash

echo "🚀 Starting Aria2 and Torrent-to-GDrive Bot..."

# ✅ Ensure logs directory exists before writing logs
mkdir -p logs downloads

# ✅ Activate virtual environment
source myenv/bin/activate

# ✅ Navigate to the project root directory
cd "$(dirname "$0")"

# ✅ Start Aria2 in the background and redirect logs
aria2c --conf-path=/Users/malfunctxn/Code/Cloney/aria2.conf --daemon=true >> logs/aria2.log 2>&1 &

# ✅ Wait for Aria2 to initialize (adjust time if necessary)
sleep 3

# ✅ Check if Aria2 started successfully
if pgrep -x "aria2c" > /dev/null; then
    echo "✅ Aria2 started successfully!"
else
    echo "❌ Failed to start Aria2. Check logs/aria2.log for details."
    exit 1
fi


# ✅ Wait for the bot to log "Application started"
echo "⌛ Waiting for the bot to initialize..."
# ✅ Start the bot with watchmedo (auto-restart on file changes)
watchmedo auto-restart --recursive --pattern="*.py" -- python3 -m bot_module.main &
sleep 2  # Adjust this if needed

# ✅ Monitor the bot logs and confirm it has started
if [ ! -f logs/bot_logs.log ]; then
    echo "❌ Bot log file not found! Check if the bot is writing logs."
    exit 1
fi

if grep -q "Application started" logs/bot_logs.log; then
    echo "✅ Bot started successfully! 🚀"
else
    echo "❌ Bot failed to start. Check logs/bot_logs.log for details."
    exit 1
fi
