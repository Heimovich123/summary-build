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
    save_analysis_result("2026-06-24", mock_json)
    
    filename = export_to_excel("2026-06-24")
    assert filename == "data/report_2026-06-24.xlsx"
    assert os.path.exists(filename)
    
    wb = openpyxl.load_workbook(filename)
    assert "Tasks" in wb.sheetnames
    assert "Decisions" in wb.sheetnames
    
    ws = wb["Tasks"]
    rows = list(ws.rows)
    assert len(rows) == 2 # header + 1 row
    assert rows[1][0].value == "ЖК Лесной"
    assert rows[1][1].value == "Залить бетон"
