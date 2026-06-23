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
          "agreed_tasks": [
            {
              "task_summary": "Залить бетон в Секции 1",
              "room_or_zone": "Секция 1",
              "responsible": "Ivanov",
              "deadline_text": "завтра до обеда",
              "status": "Согласовано, в работе",
              "approval_fact": true,
              "deadline_status": "В срок",
              "confidence": 0.9,
              "source_message_ids": [101, 102],
              "source_chat_id": -100123456789,
              "final_decision": "Залить бетон"
            }
          ]
        }
      ]
    }
    """
    report = DailyReport(**json.loads(valid_json))
    assert report.date == "2026-06-23"
    assert len(report.objects) == 1
    assert report.objects[0].object_name == "ЖК Лесной"
    assert len(report.objects[0].agreed_tasks) == 1
    assert report.objects[0].agreed_tasks[0].task_summary == "Залить бетон в Секции 1"
    assert report.objects[0].agreed_tasks[0].status == "Согласовано, в работе"
    assert report.objects[0].agreed_tasks[0].source_message_ids == [101, 102]
    assert report.objects[0].agreed_tasks[0].source_message_links == ["https://t.me/c/123456789/101", "https://t.me/c/123456789/102"]

def test_invalid_json_schema():
    invalid_json = """
    {
      "date": "2026-06-23",
      "objects": [
        {
          "agreed_tasks": [
            {
              "room_or_zone": "Секция 1",
              "confidence": 1.5
            }
          ]
        }
      ]
    }
    """
    with pytest.raises(ValidationError):
        DailyReport(**json.loads(invalid_json))
