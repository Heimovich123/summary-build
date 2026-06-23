import json
from datetime import datetime
from .db import get_analysis_result
from .models import DailyReport

def build_markdown_report(date_str: str) -> str:
    raw_json = get_analysis_result(date_str)
    if not raw_json:
        return f"No report found for date: {date_str}"
    
    report = DailyReport(**json.loads(raw_json))
    
    md = [f"# Construction Chat Daily Report: {report.date}\n"]
    
    for obj in report.objects:
        md.append(f"## Object: {obj.object_name}\n")
        
        if obj.tasks:
            md.append("### Tasks")
            for t in obj.tasks:
                assignee = f" (Assignee: {t.assignee})" if t.assignee else ""
                deadline = f" [Deadline: {t.deadline}]" if t.deadline else ""
                md.append(f"- **{t.status}**: {t.description}{assignee}{deadline} (Source Msgs: {t.source_message_ids})")
            md.append("\n")
            
        if obj.decisions:
            md.append("### Decisions")
            for d in obj.decisions:
                md.append(f"- {d.description} (Source Msgs: {d.source_message_ids})")
            md.append("\n")

        if obj.changed_decisions:
            md.append("### Changed Decisions")
            for cd in obj.changed_decisions:
                reason = f" (Reason: {cd.reason})" if cd.reason else ""
                md.append(f"- **Old**: {cd.old_decision} -> **New**: {cd.new_decision}{reason} (Source Msgs: {cd.source_message_ids})")
            md.append("\n")

        if obj.unresolved_discussions:
            md.append("### Unresolved Discussions")
            for u in obj.unresolved_discussions:
                md.append(f"- **Topic**: {u.topic}")
                md.append(f"  - Participants: {', '.join(u.participants)}")
                md.append(f"  - Status: {u.current_status}")
                md.append(f"  - Source Msgs: {u.source_message_ids}")
            md.append("\n")
            
    return "\n".join(md)

def generate_and_save_report(date_str: str = None) -> str:
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    md = build_markdown_report(date_str)
    
    filename = f"data/report_{date_str}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Markdown report saved to {filename}")
    return filename
