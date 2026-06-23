import os
from telethon import TelegramClient, events
from .config import TELETHON_API_ID, TELETHON_API_HASH, TELETHON_SESSION_PATH, TELEGRAM_SOURCE_CHAT_IDS
from .db import insert_message

def run_collector_userbot():
    if not TELETHON_API_ID or not TELETHON_API_HASH:
        print("Telethon API credentials not set.")
        return

    os.makedirs(os.path.dirname(os.path.abspath(TELETHON_SESSION_PATH)), exist_ok=True)
    client = TelegramClient(TELETHON_SESSION_PATH, TELETHON_API_ID, TELETHON_API_HASH)

    @client.on(events.NewMessage())
    async def handler(event):
        chat_id = event.chat_id
        if TELEGRAM_SOURCE_CHAT_IDS and chat_id not in TELEGRAM_SOURCE_CHAT_IDS:
            return

        if event.message.text:
            sender = await event.get_sender()
            sender_name = getattr(sender, 'first_name', str(getattr(sender, 'title', 'Unknown')))
            
            insert_message(
                message_id=event.message.id,
                chat_id=chat_id,
                sender_id=event.sender_id or 0,
                sender_name=sender_name,
                text=event.message.text,
                timestamp=event.date
            )
            print(f"Userbot saved message from {chat_id}")

    print("Starting userbot collector...")
    client.start()
    client.run_until_disconnected()
