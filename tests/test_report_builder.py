import os
from src.db import init_db, save_analysis_result
from src.report_builder import build_markdown_report

def test_build_markdown_report():
    init_db()
    
    mock_json = """
    {
      "date": "2026-06-23",
      "objects": [
        {
          "object_name": "ЖК Лесной",
          "agreed_tasks": [
            {
              "room_or_zone": "Секция 1",
              "responsible": "Ivanov",
              "deadline_text": "завтра",
              "status": "Новое",
              "approval_fact": true,
              "deadline_status": "В срок",
              "confidence": 0.9,
              "source_message_ids": [101],
              "source_chat_id": 123,
              "final_decision": "Залить бетон"
            }
          ]
        }
      ]
    }
    """
    save_analysis_result("2026-06-23", mock_json)
    
    md = build_markdown_report("2026-06-23")
    assert "# Ежедневный отчет по чатам: 2026-06-23" in md
    assert "## Объект: ЖК Лесной" in md
    assert "Залить бетон" in md
    assert "(Источники: 101)" in md
