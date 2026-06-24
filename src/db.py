import sqlite3
import os
from datetime import datetime

from .config import DATABASE_PATH

def get_connection():
    os.makedirs(os.path.dirname(os.path.abspath(DATABASE_PATH)), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_object_map (
            chat_id INTEGER PRIMARY KEY,
            chat_title TEXT,
            object_name TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            chat_id INTEGER,
            sender_id INTEGER,
            sender_name TEXT,
            text TEXT,
            timestamp DATETIME,
            is_processed BOOLEAN DEFAULT 0,
            UNIQUE(message_id, chat_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            raw_json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date)
        )
    ''')

    conn.commit()
    conn.close()

def insert_message(message_id: int, chat_id: int, sender_id: int, sender_name: str, text: str, timestamp: datetime):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO messages (message_id, chat_id, sender_id, sender_name, text, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, chat_id, sender_id, sender_name, text, timestamp.isoformat()))
        conn.commit()
    finally:
        conn.close()

def get_unprocessed_messages(object_name: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT m.id, m.message_id, m.chat_id, m.sender_name, m.text, m.timestamp, c.object_name, c.chat_title
        FROM messages m
        JOIN chat_object_map c ON m.chat_id = c.chat_id
        WHERE m.is_processed = 0 AND c.is_active = 1
    '''
    params = []
    if object_name:
        query += ' AND c.object_name = ?'
        params.append(object_name)
        
    query += ' ORDER BY m.timestamp ASC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def mark_messages_processed(db_ids: list[int]):
    if not db_ids:
        return
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ','.join(['?'] * len(db_ids))
    cursor.execute(f'''
        UPDATE messages
        SET is_processed = 1
        WHERE id IN ({placeholders})
    ''', db_ids)
    conn.commit()
    conn.close()

def upsert_chat_map(chat_id: int, chat_title: str, object_name: str, is_active: bool = True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_object_map (chat_id, chat_title, object_name, is_active)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            chat_title=excluded.chat_title,
            object_name=excluded.object_name,
            is_active=excluded.is_active
    ''', (chat_id, chat_title, object_name, int(is_active)))
    conn.commit()
    conn.close()

def save_analysis_result(date_str: str, raw_json: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis_results (date, raw_json)
        VALUES (?, ?)
        ON CONFLICT(date) DO UPDATE SET
            raw_json=excluded.raw_json,
            created_at=CURRENT_TIMESTAMP
    ''', (date_str, raw_json))
    conn.commit()
    conn.close()

def get_analysis_result(date_str: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT raw_json FROM analysis_results WHERE date = ?
    ''', (date_str,))
    row = cursor.fetchone()
    conn.close()
    return row['raw_json'] if row else None

def find_matching_entities(object_name: str = None, chat_title: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT object_name, chat_title, chat_id FROM chat_object_map WHERE is_active = 1')
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        match = True
        if object_name and object_name.lower() not in (row['object_name'] or '').lower():
            match = False
        if chat_title and chat_title.lower() not in (row['chat_title'] or '').lower():
            match = False
        if match:
            results.append(dict(row))
    return results

def get_messages_for_window(chat_id: int = None, object_name: str = None, start_dt: datetime = None, end_dt: datetime = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT m.id, m.message_id, m.chat_id, m.sender_name, m.text, m.timestamp, c.object_name, c.chat_title
        FROM messages m
        JOIN chat_object_map c ON m.chat_id = c.chat_id
        WHERE c.is_active = 1
    '''
    params = []
    
    if chat_id:
        query += ' AND m.chat_id = ?'
        params.append(chat_id)
        
    if object_name:
        query += ' AND c.object_name = ?'
        params.append(object_name)
        
    if start_dt:
        query += ' AND m.timestamp >= ?'
        params.append(start_dt.isoformat())
        
    if end_dt:
        query += ' AND m.timestamp <= ?'
        params.append(end_dt.isoformat())
        
    query += ' ORDER BY m.timestamp ASC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
