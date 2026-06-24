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

### Telegram User-Account History & Summaries

To use the Telethon userbot, ensure `TELETHON_API_ID`, `TELETHON_API_HASH`, and `TELETHON_SESSION_PATH` are set in `.env`.

- **`list-chats`**: List available chats for the connected Telegram account (to find Chat IDs).
  ```bash
  python -m src.main list-chats
  ```

- **`backfill-userbot`**: Fetch history from `TELEGRAM_SOURCE_CHAT_IDS` for a specific object over the last N days.
  ```bash
  python -m src.main backfill-userbot --days 3 --object "ЖК Пример"
  ```

- **`summary`**: Generate a custom Markdown summary for a specific chat or object over a time window without marking messages as processed.
  ```bash
  python -m src.main summary --chat-id -100123456789 --hours 5
  python -m src.main summary --object "ЖК Пример" --from "2026-06-24 10:00" --to "2026-06-24 15:00"
  ```

- **`collect-userbot`**: Run the Telethon userbot in listening mode to collect new messages in real-time.
  ```bash
  python -m src.main collect-userbot
  ```
