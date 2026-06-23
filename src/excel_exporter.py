import json
import openpyxl
from datetime import datetime
from .db import get_analysis_result
from .models import DailyReport

def export_to_excel(date_str: str = None) -> str:
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    raw_json = get_analysis_result(date_str)
    if not raw_json:
        print(f"No report found for date: {date_str}")
        return None
        
    report = DailyReport(**json.loads(raw_json))
    
    wb = openpyxl.Workbook()
    
    # Tasks Sheet
    ws_tasks = wb.active
    ws_tasks.title = "Tasks"
    ws_tasks.append(["Object Name", "Description", "Assignee", "Deadline", "Status", "Source Chat ID", "Source Message IDs"])
    
    # Decisions Sheet
    ws_dec = wb.create_sheet(title="Decisions")
    ws_dec.append(["Object Name", "Description", "Context", "Source Chat ID", "Source Message IDs"])
    
    # Changed Decisions Sheet
    ws_changed = wb.create_sheet(title="Changed Decisions")
    ws_changed.append(["Object Name", "Old Decision", "New Decision", "Reason", "Source Chat ID", "Source Message IDs"])

    # Unresolved Discussions Sheet
    ws_unresolved = wb.create_sheet(title="Unresolved")
    ws_unresolved.append(["Object Name", "Topic", "Participants", "Current Status", "Source Chat ID", "Source Message IDs"])

    for obj in report.objects:
        for t in obj.tasks:
            ws_tasks.append([obj.object_name, t.description, t.assignee, t.deadline, t.status, t.source_chat_id, str(t.source_message_ids)])
            
        for d in obj.decisions:
            ws_dec.append([obj.object_name, d.description, d.context, d.source_chat_id, str(d.source_message_ids)])
            
        for cd in obj.changed_decisions:
            ws_changed.append([obj.object_name, cd.old_decision, cd.new_decision, cd.reason, cd.source_chat_id, str(cd.source_message_ids)])
            
        for u in obj.unresolved_discussions:
            ws_unresolved.append([obj.object_name, u.topic, ", ".join(u.participants), u.current_status, u.source_chat_id, str(u.source_message_ids)])

    filename = f"data/report_{date_str}.xlsx"
    wb.save(filename)
    print(f"Excel report saved to {filename}")
    return filename
