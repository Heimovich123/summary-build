import asyncio
from telegram import Bot
from telegram.error import TelegramError
from .config import TELEGRAM_REPORT_BOT_TOKEN, TELEGRAM_OWNER_CHAT_ID

async def send_daily_report(md_path: str, excel_path: str):
    if not TELEGRAM_REPORT_BOT_TOKEN or not TELEGRAM_OWNER_CHAT_ID:
        print("Telegram sender not configured. Skipping send.")
        return

    bot = Bot(token=TELEGRAM_REPORT_BOT_TOKEN)
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        if len(md_text) > 4000:
            await bot.send_message(chat_id=TELEGRAM_OWNER_CHAT_ID, text="Daily report is too long, sending as file.")
            with open(md_path, 'rb') as doc:
                await bot.send_document(chat_id=TELEGRAM_OWNER_CHAT_ID, document=doc)
        else:
            await bot.send_message(chat_id=TELEGRAM_OWNER_CHAT_ID, text=md_text, parse_mode='Markdown')
            
        if excel_path:
            with open(excel_path, 'rb') as doc:
                await bot.send_document(chat_id=TELEGRAM_OWNER_CHAT_ID, document=doc)
                
        print("Reports sent successfully to Telegram.")
    except TelegramError as e:
        print(f"Failed to send telegram report: {e}")

def run_send_report(md_path: str, excel_path: str):
    asyncio.run(send_daily_report(md_path, excel_path))
