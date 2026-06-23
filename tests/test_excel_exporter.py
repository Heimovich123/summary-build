import os
from src.db import init_db, save_analysis_result
from src.excel_exporter import export_to_excel
import openpyxl

def test_export_to_excel():
    init_db()
    
    mock_json = """
    {
      "date": "2026-06-24",
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
    save_analysis_result("2026-06-24", mock_json)
    
    filename = export_to_excel("2026-06-24")
    assert filename == "data/report_2026-06-24.xlsx"
    assert os.path.exists(filename)
    
    wb = openpyxl.load_workbook(filename)
    assert "Аналитика чатов" in wb.sheetnames
    
    ws = wb["Аналитика чатов"]
    rows = list(ws.rows)
    assert len(rows) == 2 # header + 1 row
    assert rows[1][0].value == "ЖК Лесной"
    assert rows[1][1].value == "Согласованные задачи"
    assert rows[1][2].value == "Секция 1"

