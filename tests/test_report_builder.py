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
          "tasks": [
            {
              "description": "Залить бетон",
              "assignee": "Ivanov",
              "deadline": "завтра",
              "status": "New",
              "source_message_ids": [101],
              "source_chat_id": 123
            }
          ],
          "decisions": [],
          "unresolved_discussions": [],
          "changed_decisions": []
        }
      ]
    }
    """
    save_analysis_result("2026-06-23", mock_json)
    
    md = build_markdown_report("2026-06-23")
    assert "# Construction Chat Daily Report: 2026-06-23" in md
    assert "## Object: ЖК Лесной" in md
    assert "Залить бетон" in md
    assert "(Source Msgs: [101])" in md
