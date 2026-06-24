import pytest
from datetime import datetime, timedelta
import sqlite3
import os
import sys
from unittest.mock import patch, MagicMock

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db import init_db, get_connection, upsert_chat_map, insert_message
from src.extractor import run_custom_summary

@pytest.fixture
def test_db():
    # Use in-memory DB or temporary file for tests?
    # We will just patch DATABASE_PATH to use a test sqlite file.
    test_db_path = "data/test_chat_analyst.db"
    with patch('src.db.DATABASE_PATH', test_db_path):
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        init_db()
        
        # Insert some test data
        now = datetime.now()
        
        # Object "Офис", Chat "Электрика Офис" (ID: 100)
        upsert_chat_map(100, "Электрика Офис", "Офис")
        # Object "Офис", Chat "Сантехника Офис" (ID: 101)
        upsert_chat_map(101, "Сантехника Офис", "Офис")
        
        # Messages for Электрика (100)
        insert_message(1, 100, 1, "User A", "Lamp", now - timedelta(minutes=5))
        insert_message(2, 100, 1, "User A", "Wire", now - timedelta(hours=2))
        
        # Messages for Сантехника (101)
        insert_message(3, 101, 1, "User B", "Pipe", now - timedelta(minutes=15))
        insert_message(4, 101, 1, "User B", "Sink", now - timedelta(days=2))
        
        yield
        
        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

@patch('src.extractor.extract_and_validate')
@patch('src.extractor.build_markdown_from_report')
def test_minutes_time_window(mock_build, mock_extract, test_db, capsys):
    mock_extract.return_value = MagicMock()
    mock_build.return_value = "# Report"
    
    start_dt = datetime.now() - timedelta(minutes=10)
    
    # Should only get message 1 (5 mins ago)
    run_custom_summary(object_name="Офис", start_dt=start_dt)
    
    captured = capsys.readouterr()
    assert "Messages count: 1" in captured.out
    assert "Selected object/chat: Офис" in captured.out

@patch('src.extractor.extract_and_validate')
def test_partial_object_match(mock_extract, test_db, capsys):
    mock_extract.return_value = MagicMock()
    
    # "Оф" should match "Офис"
    start_dt = datetime.now() - timedelta(hours=1)
    run_custom_summary(object_name="Оф", start_dt=start_dt)
    
    captured = capsys.readouterr()
    assert "Messages count: 2" in captured.out # msg 1 (5m) and msg 3 (15m)
    assert "Selected object/chat: Офис" in captured.out

@patch('src.extractor.extract_and_validate')
def test_partial_chat_match(mock_extract, test_db, capsys):
    mock_extract.return_value = MagicMock()
    
    # "элект" should match "Электрика Офис"
    start_dt = datetime.now() - timedelta(hours=3)
    run_custom_summary(chat_title="элект", start_dt=start_dt)
    
    captured = capsys.readouterr()
    # msg 1 (5m) and msg 2 (2h)
    assert "Messages count: 2" in captured.out
    assert "Selected object/chat: Электрика Офис" in captured.out

@patch('src.extractor.extract_and_validate')
def test_no_messages_case(mock_extract, test_db, capsys):
    # Future window -> no messages
    start_dt = datetime.now() + timedelta(days=1)
    end_dt = datetime.now() + timedelta(days=2)
    
    run_custom_summary(object_name="Офис", start_dt=start_dt, end_dt=end_dt)
    
    captured = capsys.readouterr()
    assert "Нет сообщений за выбранный период." in captured.out
    mock_extract.assert_not_called()

@patch('src.extractor.extract_and_validate')
def test_multiple_match_fail(mock_extract, test_db, capsys):
    # Insert another chat for a DIFFERENT object that also matches "Оф"
    upsert_chat_map(102, "Оформление", "Оформление")
    
    run_custom_summary(object_name="Оф")
    
    captured = capsys.readouterr()
    assert "Найдено несколько объектов" in captured.out
    assert "Офис" in captured.out
    assert "Оформление" in captured.out
    mock_extract.assert_not_called()
