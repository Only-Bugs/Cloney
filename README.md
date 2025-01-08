---

# **Torrent-to-GDrive Bot**

_A Telegram bot that downloads torrents using Aria2 and uploads them to Google Drive._

## **📖 Table of Contents**

- [Introduction](#introduction)
- [Current Status](#current-status)
- [Bug Tracking](#bug-tracking)
- [Sprint Progress](#sprint-progress)
- [Setup & Installation](#setup--installation)
- [Contributing](#contributing)
- [License](#license)

---

## **🚀 Introduction**

This bot allows users to download torrents directly via Telegram and automatically upload them to Google Drive. It is powered by **Aria2 RPC** for efficient torrent management and integrates seamlessly with Google Drive.

---

## **📌 Current Status**

✅ **Project is active and in development.**  
🚀 **Milestone 1 achieved:** The bot successfully downloads torrents via Aria2.  
🔄 **Next goal:** Fixing torrent tracking issues and adding Google Drive integration.

---

## **🐞 Bug Tracking**

Below is a list of currently **known bugs** and their respective statuses.

| **ID** | **Bug Description**                                                                                                 | **Status**     | **Proposed Fix**                                           |
| ------ | ------------------------------------------------------------------------------------------------------------------- | -------------- | ---------------------------------------------------------- |
| 🐞 001 | **ETA Conversion Overflow** (`OverflowError: days=1000000000; must have magnitude <= 999999999`)                    | 🔄 In Progress | Clamp `eta` values before passing them to `timedelta()`.   |
| 🐞 002 | **Telegram Bot - Torrent Tracking Error** (`'>' not supported between instances of 'datetime.timedelta' and 'int'`) | 🔄 In Progress | Ensure `eta` is always an integer in `torrent_manager.py`. |
| 🐞 003 | **/add_torrent Fails to Fetch Details** (`Torrent added, but unable to fetch details after multiple attempts.`)     | 🔄 In Progress | Improve fetching logic and add debug logs.                 |

---

## **📅 Sprint Progress**

A **breakdown of our development roadmap** and sprint progress.

### **🚀 Sprint 1: Setup & Basic Bot Structure** _(✅ Completed)_

- ✅ Initialized the project
- ✅ Set up dependencies
- ✅ Created a basic Telegram bot

---

### **📌 Sprint 2: Torrent Management** _(🔄 In Progress)_

- ✅ Integrated Aria2 RPC
- ✅ Successfully added torrents via Telegram
- 🟡 **Fix tracking issues (ETA, torrent details retrieval)**
- 🟡 **Improve error handling for failed torrents**
- 🟡 **Test various magnet links and edge cases**

---

### **📌 Sprint 3: Google Drive Integration** _(🔜 Upcoming)_

- Authenticate with Google Drive API
- Upload completed torrents to Google Drive

---

### **📌 Sprint 4: Error Handling & Logging** _(🔜 Upcoming)_

- Improve logging for better debugging
- Handle unexpected errors gracefully

---

### **📌 Sprint 5: Documentation** _(🔜 Upcoming)_

- Document the codebase
- Create a setup guide for new developers

---

## **🛠️ Setup & Installation**

To set up the bot on your own system, follow these steps:

### **🔹 Prerequisites**

- Python 3.10+
- Telegram Bot Token
- Aria2 installed with RPC enabled
- Google Drive API credentials (for later integration)

### **🔹 Installation Steps**

```bash
git clone https://github.com/yourusername/Torrent-to-GDrive-Bot.git
cd Torrent-to-GDrive-Bot
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
pip install -r requirements.txt
```

### **🔹 Configuration**

Modify `config/config.py` with your **Telegram Bot Token** and **Aria2 RPC settings**.

### **🔹 Running the Bot**

```bash
python bot_module/main.py
```

---

## **🤝 Contributing**

Want to help improve this project? Here’s how you can contribute:

1. Fork the repo.
2. Create a new branch (`feature-branch-name`).
3. Commit your changes and push to your fork.
4. Open a **Pull Request**.

We welcome contributions in:

- Bug Fixes 🐞
- Code Refactoring 💡
- Feature Development 🚀
- Documentation 📜

---

## **📜 License**

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

### **📌 Last Updated:** _January 16, 2025_

---

This **README.md** will keep your repo updated with active issues and sprint progress while maintaining an organized structure.
