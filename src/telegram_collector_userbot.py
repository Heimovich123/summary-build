import os
import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events
from .config import TELETHON_API_ID, TELETHON_API_HASH, TELETHON_SESSION_PATH, TELEGRAM_SOURCE_CHAT_IDS
from .db import insert_message, upsert_chat_map

def get_client() -> TelegramClient:
    if not TELETHON_API_ID or not TELETHON_API_HASH:
        raise ValueError("Telethon API credentials not set.")
    import telethon.network.connection
    os.makedirs(os.path.dirname(os.path.abspath(TELETHON_SESSION_PATH)), exist_ok=True)
    return TelegramClient(TELETHON_SESSION_PATH, TELETHON_API_ID, TELETHON_API_HASH, use_ipv6=False, request_retries=5, connection_retries=5, connection=telethon.network.connection.tcpobfuscated.ConnectionTcpObfuscated)

def run_collector_userbot():
    try:
        client = get_client()
    except ValueError as e:
        print(e)
        return

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

async def async_list_chats():
    client = get_client()
    await client.start()
    async for dialog in client.iter_dialogs():
        dtype = "Channel" if dialog.is_channel else "Group" if dialog.is_group else "User"
        print(f"{dialog.id} | {dtype} | {dialog.title}")

def run_list_chats():
    asyncio.run(async_list_chats())

async def async_backfill(days: int, object_name: str):
    client = get_client()
    await client.start()
    limit_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    for chat_id in TELEGRAM_SOURCE_CHAT_IDS:
        try:
            entity = await client.get_entity(chat_id)
            chat_title = getattr(entity, 'title', str(chat_id))
            upsert_chat_map(chat_id, chat_title, object_name)
            
            count = 0
            async for msg in client.iter_messages(entity):
                if msg.date < limit_date:
                    break
                
                if msg.text:
                    sender = await msg.get_sender()
                    sender_name = getattr(sender, 'first_name', str(getattr(sender, 'title', 'Unknown')))
                    insert_message(
                        message_id=msg.id,
                        chat_id=chat_id,
                        sender_id=msg.sender_id or 0,
                        sender_name=sender_name,
                        text=msg.text,
                        timestamp=msg.date
                    )
                    count += 1
            print(f"Backfilled {count} messages from chat {chat_id} ({chat_title})")
        except Exception as e:
            print(f"Failed to backfill chat {chat_id}: {e}")

def run_backfill(days: int, object_name: str):
    if not TELEGRAM_SOURCE_CHAT_IDS:
        print("TELEGRAM_SOURCE_CHAT_IDS not set in config.")
        return
    if not object_name:
        print("object_name is required for backfill.")
        return
    asyncio.run(async_backfill(days, object_name))
