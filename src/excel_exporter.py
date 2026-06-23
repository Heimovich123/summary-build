import json
import openpyxl
from datetime import datetime
from .db import get_analysis_result
from .models import DailyReport

def export_to_excel(date_str: str = None, object_name: str = None) -> str:
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    raw_json = get_analysis_result(date_str)
    if not raw_json:
        print(f"No report found for date: {date_str}")
        return None
        
    report = DailyReport(**json.loads(raw_json))
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Аналитика чатов"
    
    headers = [
        "Объект", "Категория", "Краткое содержание", "Зона/Помещение", "Инициатор", "Ответственный", 
        "Согласующий", "Факт согласования", "Дедлайн (текст)", "Дедлайн (дата)", 
        "Статус дедлайна", "Итоговое решение", "История изменений", "Статус", 
        "Следующее действие", "Уверенность", "ID Чата", "Ссылки на сообщения"
    ]
    ws.append(headers)

    categories_map = {
        "agreed_tasks": "Согласованные задачи",
        "unresolved_discussions": "Обсуждалось, но решение не принято",
        "missing_deadline": "Есть решение, но нет дедлайна",
        "missing_responsible": "Нет ответственного",
        "changed_decisions": "Изменения решений",
        "needs_manager_attention": "Требует внимания руководителя"
    }

    for obj in report.objects:
        if object_name and obj.object_name != object_name:
            continue
            
        for cat_attr, cat_ru in categories_map.items():
            items = getattr(obj, cat_attr, [])
            for item in items:
                row = [
                    obj.object_name,
                    cat_ru,
                    item.task_summary,
                    item.room_or_zone,
                    item.initiator,
                    item.responsible,
                    item.approver,
                    "Да" if item.approval_fact else "Нет",
                    item.deadline_text,
                    item.deadline_date,
                    item.deadline_status,
                    item.final_decision,
                    item.change_history,
                    item.status,
                    item.next_action,
                    item.confidence,
                    item.source_chat_id,
                    ", ".join(item.source_message_links) if item.source_message_links else ", ".join(map(str, item.source_message_ids))
                ]
                ws.append(row)

    suffix = f"_{object_name}" if object_name else ""
    filename = f"data/report_{date_str}{suffix}.xlsx"
    wb.save(filename)
    print(f"Excel report saved to {filename}")
    return filename
