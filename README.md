# Telegram Construction Chat Analyst MVP

A Python-based service to ingest construction-related Telegram chats, extract actionable insights using an LLM (OpenRouter), and generate daily structured reports (Markdown + Excel).

## Setup

1. Copy `.env.example` to `.env` and fill in the values:
   ```bash
   cp .env.example .env
   ```
2. Install requirements (Python 3.11+ recommended):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

This MVP provides several CLI commands via `src/main.py`:

- **`load-sample`**: Load mock messages from `data/sample_messages.json` into the database.
  ```bash
  python -m src.main load-sample
  ```

- **`extract`**: Run the LLM extraction process on unprocessed messages in the database.
  ```bash
  python -m src.main extract
  ```

- **`report`**: Generate Markdown and Excel reports based on extraction results.
  ```bash
  python -m src.main report
  ```

- **`daily-report`**: Run extraction, build reports, and send them to Telegram.
  ```bash
  python -m src.main daily-report
  ```

- **`collect-bot`**: Run the standard bot listener to collect new messages in groups.
  ```bash
  python -m src.main collect-bot
  ```

- **`collect-userbot`**: Run the Telethon userbot to collect messages (requires authentication on first run).
  ```bash
  python -m src.main collect-userbot
  ```
