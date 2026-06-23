import json
import os
from datetime import datetime

from .db import init_db, insert_message, upsert_chat_map

def load_sample_data():
    init_db()
    
    # Insert mappings
    upsert_chat_map(-100123456789, "Chat ЖК Лесной", "ЖК Лесной", is_active=True)

    sample_path = os.path.join("data", "sample_messages.json")
    if not os.path.exists(sample_path):
        print(f"File {sample_path} not found.")
        return

    with open(sample_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    for msg in messages:
        dt = datetime.fromisoformat(msg['timestamp'])
        insert_message(
            message_id=msg['message_id'],
            chat_id=msg['chat_id'],
            sender_id=msg['sender_id'],
            sender_name=msg['sender_name'],
            text=msg['text'],
            timestamp=dt
        )
    print(f"Loaded {len(messages)} sample messages into DB.")
