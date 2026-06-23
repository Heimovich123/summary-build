import json
from datetime import datetime
from .db import get_analysis_result
from .models import DailyReport

def build_markdown_report(date_str: str, object_name: str = None) -> str:
    raw_json = get_analysis_result(date_str)
    if not raw_json:
        return f"Отчет за дату {date_str} не найден."
    
    report = DailyReport(**json.loads(raw_json))
    
    md = [f"# Ежедневный отчет по чатам: {report.date}\n"]
    
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
            
        md.append(f"## Объект: {obj.object_name}\n")
        
        for cat_attr, cat_ru in categories_map.items():
            items = getattr(obj, cat_attr, [])
            if not items:
                continue
                
            md.append(f"### {cat_ru}")
            for item in items:
                resp = f" (Отв: {item.responsible})" if item.responsible else ""
                deadline = f" [Дедлайн: {item.deadline_text or item.deadline_date}]" if (item.deadline_text or item.deadline_date) else ""
                status = f" **[{item.status}]**" if item.status else ""
                links = ", ".join(item.source_message_links) if item.source_message_links else ", ".join(map(str, item.source_message_ids))
                
                desc = item.final_decision or item.next_action or "Нет описания"
                
                md.append(f"-{status} {desc}{resp}{deadline} (Источники: {links})")
            md.append("\n")
            
    return "\n".join(md)

def generate_and_save_report(date_str: str = None, object_name: str = None) -> str:
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    md = build_markdown_report(date_str, object_name)
    
    suffix = f"_{object_name}" if object_name else ""
    filename = f"data/report_{date_str}{suffix}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Markdown report saved to {filename}")
    return filename
