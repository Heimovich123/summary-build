import json
from src.models import DailyReport
from pydantic import ValidationError
import pytest

def test_valid_json_schema():
    valid_json = """
    {
      "date": "2026-06-23",
      "objects": [
        {
          "object_name": "ЖК Лесной",
          "tasks": [
            {
              "description": "Залить бетон",
              "assignee": "Ivanov",
              "deadline": "завтра до обеда",
              "status": "In Progress",
              "source_message_ids": [101, 102],
              "source_chat_id": -100123456789
            }
          ],
          "decisions": [],
          "unresolved_discussions": [],
          "changed_decisions": []
        }
      ]
    }
    """
    report = DailyReport(**json.loads(valid_json))
    assert report.date == "2026-06-23"
    assert len(report.objects) == 1
    assert report.objects[0].object_name == "ЖК Лесной"
    assert len(report.objects[0].tasks) == 1
    assert report.objects[0].tasks[0].source_message_ids == [101, 102]

def test_invalid_json_schema():
    invalid_json = """
    {
      "date": "2026-06-23",
      "objects": [
        {
          "tasks": [
            {
              "description": "Залить бетон"
            }
          ]
        }
      ]
    }
    """
    with pytest.raises(ValidationError):
        DailyReport(**json.loads(invalid_json))
