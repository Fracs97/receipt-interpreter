# ReceiptNinja 🥷

A Telegram bot that tracks your expenses automatically — just send a photo of any receipt and it extracts the total, categorizes it, and monitors your spending against your budget.

## How It Works

1. Start a conversation with the bot on Telegram with /start
2. Set up your expense categories (e.g. Food, Transport, Entertainment) with optional budgets
3. Send a photo of any receipt
4. The bot extracts the date, amount, and category using Google Gemini AI
5. Request a summary anytime with `/summary` to see your spending breakdown

## Features

- **Receipt OCR** — extracts expense data from receipt photos using Google Gemini
- **Auto-categorization** — assigns expenses to your custom categories automatically
- **Budget tracking** — set spending limits per category and track progress
- **Spending summaries** — view total spending grouped by category with budget percentages
- **Multi-user support** — each user has their own categories, budgets, and expense history

## Tech Stack

- **Python 3.14**
- **python-telegram-bot** — Telegram Bot API integration
- **Google Gemini API** — image recognition and expense data extraction
- **SQLAlchemy** — ORM for database operations
- **PostgreSQL** — persistent data storage

## Project Structure

```
receipt-interpreter/
    src/
        conversationhandler.py  — bot conversation flow and command handlers
        database.py             — database connection and session management
        google_api.py           — Gemini API integration for receipt processing
        models.py               — SQLAlchemy models (User, Category, Receipt)
    .env                        — environment variables (not committed)
    .gitignore
    requirements.txt
    README.md
```

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google Cloud account with Gemini API enabled

### Installation

```bash
git clone https://github.com/Fracs97/receipt-interpreter.git
cd receipt-interpreter
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash)
pip install -r requirements.txt
```

### Database Setup

```bash
psql -U postgres
CREATE DATABASE receipt_interpreter;
```

### Environment Variables

Create a `.env` file in the project root:

```
TELEGRAM_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/receipt_interpreter
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
PROJECT_NAME=your_google_cloud_project_name
```

### Running

```bash
cd src
python conversationhandler.py
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Set up your account and expense categories |
| `/summary` | View your spending breakdown by category |

## Database Schema

**users** — stores Telegram user IDs

**categories** — expense categories with optional budget limits per user

**receipts** — individual expenses linked to a user and category

## License

MIT
