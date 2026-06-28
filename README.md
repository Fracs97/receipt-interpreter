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
- **Containerized** — full Docker setup included for a consistent, one-command run experience

## Tech Stack
- **Python 3.14**
- **python-telegram-bot** — Telegram Bot API integration
- **Google Gemini API** — image recognition and expense data extraction
- **SQLAlchemy** — ORM for database operations
- **PostgreSQL** — persistent data storage
- **Docker & Docker Compose** — containerization and multi-service orchestration

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
    docker-compose.yml          — multi-service orchestration (bot + PostgreSQL)
    Dockerfile                  — container image definition for the bot
    requirements.txt
    README.md
```

## Setup

### Prerequisites
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Google Cloud account with Gemini API enabled
- **Docker & Docker Compose** (recommended) — or Python 3.12+ and PostgreSQL for manual setup

### Environment Variables

**Docker setup** — `docker-compose.yml` hardcodes `DATABASE_URL` and `GOOGLE_APPLICATION_CREDENTIALS` directly, so your `.env` only needs to supply two values:
```
TELEGRAM_TOKEN=your_telegram_bot_token
PROJECT_NAME=your_google_cloud_project_name
```

**Manual setup** — all four variables are required:
```
TELEGRAM_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/receipt_interpreter
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
PROJECT_NAME=your_google_cloud_project_name
```

---

### 🐳 Running with Docker (recommended)

No need to install Python, PostgreSQL, or manage a virtual environment — Docker handles everything.

```bash
git clone https://github.com/Fracs97/receipt-interpreter.git
cd receipt-interpreter
```

Make sure your `.env` file is in place, then:

```bash
docker compose up --build
```

This starts two containers: the bot and a PostgreSQL instance. The database is created and persisted automatically via a named volume. To stop:

```bash
docker compose down
```

To stop and also remove the database volume:

```bash
docker compose down -v
```

---

### 🐍 Manual Setup (without Docker)

#### Installation
```bash
git clone https://github.com/Fracs97/receipt-interpreter.git
cd receipt-interpreter
python -m venv .venv
source .venv/Scripts/activate  # Windows (Git Bash)
pip install -r requirements.txt
```

#### Database Setup
```bash
psql -U postgres
CREATE DATABASE receipt_interpreter;
```

> Update `DATABASE_URL` in your `.env` to use `localhost` as the host.

#### Running
```bash
cd src
python conversationhandler.py
```

---

## Bot Commands
| Command | Description |
|---------|-------------|
| `/start` | Set up your account and expense categories |
| `/summary` | View your spending breakdown by category |

## Database Schema
Tables are created automatically on startup via `Base.metadata.create_all()`.

**users**
| Column | Type | Notes |
|--------|------|-------|
| `id` | String | Primary key — Telegram user ID |
| `created_at` | Timestamp | Auto-set on row creation |

**categories**
| Column | Type | Notes |
|--------|------|-------|
| `id` | String (UUID) | Primary key — auto-generated |
| `user_id` | String | Foreign key → `users.id` |
| `category_name` | String(30) | Not null |
| `budget` | Numeric | Optional spending limit |

**receipts**
| Column | Type | Notes |
|--------|------|-------|
| `id` | String (UUID) | Primary key — auto-generated |
| `user_id` | String | Foreign key → `users.id` |
| `category_id` | String | Foreign key → `categories.id` |
| `expense_date` | Timestamp | Auto-set on row creation |
| `amount` | Numeric | Not null |
| `description` | String(50) | Optional |

## License
MIT
