import json
import os
import uuid
from datetime import datetime
from pydantic import ValidationError

from .db import get_unprocessed_messages, mark_messages_processed, save_analysis_result, get_messages_for_window, find_matching_entities
from .llm_client import call_llm
from .models import DailyReport
from .config import LLM_MODEL_PRIMARY, LLM_MODEL_FALLBACK
from .report_builder import build_markdown_from_report
from .telegram_sender import run_send_report

SYSTEM_PROMPT = """
You are an AI analyst for construction chats. Your task is to analyze the provided Telegram messages and extract structured data.
You must return valid JSON that conforms strictly to the requested schema.

The JSON schema should match this structure:
{
  "date": "YYYY-MM-DD",
  "objects": [
    {
      "object_name": "Name of the construction object",
      "agreed_tasks": [
        {
          "task_summary": "Short summary of the task/decision",
          "room_or_zone": "Zone or null",
          "initiator": "Name or null",
          "responsible": "Name or null",
          "approver": "Name or null",
          "approval_fact": true,
          "deadline_text": "Text or null",
          "deadline_date": "YYYY-MM-DD or null",
          "deadline_status": "В срок" | "Просрочено" | "Риск срыва" | "Не определен",
          "final_decision": "Text or null",
          "change_history": "Text or null",
          "status": "Согласовано, в работе" | "Обсуждается" | "Решение не принято" | "Ответственный не назначен" | "Дедлайн не установлен" | "Ожидает согласования" | "Просрочено" | "Решение изменено" | "Обсуждение без результата" | "Требует внимания руководителя",
          "next_action": "Text or null",
          "confidence": 0.9,
          "source_chat_id": 123456,
          "source_message_ids": [101, 102]
        }
      ],
      "unresolved_discussions": [],
      "missing_deadline": [],
      "missing_responsible": [],
      "changed_decisions": [],
      "needs_manager_attention": []
    }
  ]
}

Analyze the messages and return ONLY the JSON. Include `source_message_ids` and `source_chat_id` for every item extracted to ensure traceability. 
`approval_fact` must be a boolean. `confidence` must be a float between 0.0 and 1.0.
"""

def build_prompt(messages: list[dict]) -> str:
    prompt = "Messages to analyze:\n"
    for m in messages:
        prompt += f"[{m['timestamp']}] Chat: {m['chat_title']} (ID: {m['chat_id']}) | MsgID: {m['message_id']} | {m['sender_name']}: {m['text']}\n"
    return prompt

def save_failed_extraction(raw_content: str, error: str):
    os.makedirs("logs/failed_extractions", exist_ok=True)
    filename = f"logs/failed_extractions/failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"error": error, "raw_content": raw_content}, f, indent=2, ensure_ascii=False)
    print(f"Failed extraction saved to {filename}")

def extract_and_validate(messages_text: str) -> DailyReport | None:
    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": messages_text}
    ]

    # Attempt 1: Primary Model
    try:
        print(f"Calling primary model: {LLM_MODEL_PRIMARY}")
        raw_json = call_llm(api_messages, LLM_MODEL_PRIMARY)
        parsed_dict = json.loads(raw_json)
        report = DailyReport(**parsed_dict)
        return report
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Primary model failed validation: {e}. Retrying primary model once...")
        try:
            raw_json = call_llm(api_messages, LLM_MODEL_PRIMARY)
            parsed_dict = json.loads(raw_json)
            report = DailyReport(**parsed_dict)
            return report
        except (json.JSONDecodeError, ValidationError) as e2:
            print(f"Primary model retry failed: {e2}. Falling back to fallback model...")

    # Fallback Model
    try:
        print(f"Calling fallback model: {LLM_MODEL_FALLBACK}")
        raw_json = call_llm(api_messages, LLM_MODEL_FALLBACK)
        parsed_dict = json.loads(raw_json)
        report = DailyReport(**parsed_dict)
        return report
    except Exception as e:
        print(f"Fallback model failed: {e}")
        save_failed_extraction(raw_json if 'raw_json' in locals() else "No response", str(e))
        return None

def run_extraction(object_name: str = None):
    unprocessed = get_unprocessed_messages(object_name)
    if not unprocessed:
        print("No new messages to process.")
        return

    print(f"Processing {len(unprocessed)} messages...")
    prompt_text = build_prompt(unprocessed)
    report = extract_and_validate(prompt_text)

    if report:
        print("Extraction successful and validated.")
        save_analysis_result(datetime.now().strftime('%Y-%m-%d'), report.model_dump_json())
        db_ids = [m['id'] for m in unprocessed]
        mark_messages_processed(db_ids)
        print("Messages marked as processed.")
    else:
        print("Extraction failed.")

def run_custom_summary(chat_id: int = None, object_name: str = None, chat_title: str = None, start_dt: datetime = None, end_dt: datetime = None, send: bool = False):
    exact_object_name = object_name
    
    if (object_name or chat_title) and not chat_id:
        matches = find_matching_entities(object_name=object_name, chat_title=chat_title)
        
        if object_name:
            unique_objects = list(set(r['object_name'] for r in matches if r['object_name']))
            if len(unique_objects) == 0:
                print("Объект не найден")
                return
            elif len(unique_objects) > 1:
                print(f"Найдено несколько объектов: {', '.join(unique_objects)}. Уточните запрос.")
                return
            else:
                exact_object_name = unique_objects[0]
                
        elif chat_title:
            unique_chats = list(set((r['chat_title'], r['chat_id']) for r in matches if r['chat_title']))
            if len(unique_chats) == 0:
                print("Чат не найден")
                return
            elif len(unique_chats) > 1:
                print(f"Найдено несколько чатов: {', '.join(c[0] for c in unique_chats)}. Уточните запрос.")
                return
            else:
                chat_id = unique_chats[0][1]
                chat_title = unique_chats[0][0]

    messages = get_messages_for_window(chat_id, exact_object_name, start_dt, end_dt)
    
    print(f"Selected object/chat: {exact_object_name or chat_title or 'All'}")
    print(f"Period: {start_dt or 'Any'} - {end_dt or 'Any'}")
    print(f"Messages count: {len(messages)}")

    if not messages:
        print("Нет сообщений за выбранный период.")
        return

    prompt_text = build_prompt(messages)
    report = extract_and_validate(prompt_text)

    if report:
        md = build_markdown_from_report(report, exact_object_name)
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/summary_{timestamp_str}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md)
            
        print(f"Markdown path: {filename}")
        
        if send:
            run_send_report(filename, None)
            print("Sent: yes")
        else:
            print("Sent: no")
    else:
        print("Custom summary extraction failed.")
