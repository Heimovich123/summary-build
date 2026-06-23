import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL_PRIMARY = os.getenv("LLM_MODEL_PRIMARY", "nvidia/llama-3.1-nemotron-ultra-253b-v1:free")
LLM_MODEL_FALLBACK = os.getenv("LLM_MODEL_FALLBACK", "openai/gpt-4o-mini")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

TELEGRAM_REPORT_BOT_TOKEN = os.getenv("TELEGRAM_REPORT_BOT_TOKEN", "")
TELEGRAM_OWNER_CHAT_ID = os.getenv("TELEGRAM_OWNER_CHAT_ID", "")

TELETHON_API_ID = os.getenv("TELETHON_API_ID", "")
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH", "")
TELETHON_SESSION_PATH = os.getenv("TELETHON_SESSION_PATH", "data/userbot.session")

TELEGRAM_SOURCE_CHAT_IDS = []
_chat_ids_env = os.getenv("TELEGRAM_SOURCE_CHAT_IDS", "")
if _chat_ids_env:
    TELEGRAM_SOURCE_CHAT_IDS = [int(cid.strip()) for cid in _chat_ids_env.split(",") if cid.strip()]

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/chat_analyst.db")
