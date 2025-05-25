# Marketplace Telegram Bot

**A Telegram bot front-end for the Ethiopian Central Marketplace API. Browse products and channels, search, bookmark, and comment—all within Telegram.**

---

## Prerequisites

- **Python 3.10+** installed on your system.
- **Git** (to clone the repo).
- A Telegram bot token and username (obtain from BotFather).
- (Optional) Test bot credentials for staging.
- (Optional) Custom backend API URL if you’re not using the default on Render.

## Setup

1. **Clone the repository**
   ```bash
   git clonehttps://github.com/Centralized-Market-Place/central-marketplace-telegram-bot
   cd central-marketplace-telegram-bot
   ```

# Optional: Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: .\venv\Scripts\Activate.ps1
```

# Install dependencies
```bash
pip install -r requirements.txt
```

# Configure environment variables (create a file named .env in project root)
```
API_URL=https://central-marketplace-backend.onrender.com/api/v1
TELEGRAM_BOT_USERNAME=central_marketplace_v1_bot
TEST_TELEGRAM_BOT_TOKEN=7880198462:...
TEST_TELEGRAM_BOT_USERNAME=test_centeral_marketplace_bot
```
# (Re)generate requirements.txt (if needed)
```bash
pip install pipreqs
pipreqs . --force
```

# Running the Bot
# Development (auto-reload):
```bash
python runner.py
```

# Production:
```bash
python bot.py
```

# Project Structure
```

├── bot.py               # Entry point
├── runner.py            # Dev runner with auto-restart
├── config.py            # Loads .env settings
├── client.py            # HTTP client for backend API
├── state_store.py       # Simple JSON-based user state
├── helpers.py           # Utility functions (e.g., image uploads)
├── handlers/            # Telegram command & message handlers
│   ├── channels.py
│   ├── products.py
│   ├── categories.py
│   ├── browse.py
│   ├── comments.py
│   ├── bookmarks.py
│   ├── paginations.py
│   ├── misc.py
│   └── callback_data.py
├── requirements.txt     # Python dependencies
└── README.md            # This file
```