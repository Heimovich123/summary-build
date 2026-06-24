import argparse
import sys
from datetime import datetime, timedelta

from .db import init_db
from .sample_loader import load_sample_data
from .extractor import run_extraction, run_custom_summary
from .report_builder import generate_and_save_report
from .excel_exporter import export_to_excel
from .telegram_sender import run_send_report
from .telegram_collector_bot import run_collector_bot
from .telegram_collector_userbot import run_collector_userbot, run_list_chats, run_backfill

def parse_dt(dt_str: str) -> datetime:
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return datetime.strptime(dt_str, "%Y-%m-%d")

def main():
    parser = argparse.ArgumentParser(description="Telegram Construction Chat Analyst MVP")
    parser.add_argument("command", choices=[
        "load-sample", 
        "collect-bot", 
        "collect-userbot", 
        "list-chats",
        "backfill-userbot",
        "extract", 
        "summary",
        "report", 
        "send-report", 
        "daily-report"
    ], help="Command to run")
    parser.add_argument("--date", type=str, help="Date for report (YYYY-MM-DD)", default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument("--object", type=str, help="Filter by object_name", default=None)
    parser.add_argument("--chat", type=str, help="Filter by chat title", default=None)
    parser.add_argument("--days", type=int, help="Days for backfill", default=3)
    parser.add_argument("--chat-id", type=int, help="Filter by exact chat ID", default=None)
    parser.add_argument("--hours", type=int, help="Hours for custom summary window", default=None)
    parser.add_argument("--minutes", type=int, help="Minutes for custom summary window", default=None)
    parser.add_argument("--from", dest="from_dt", type=str, help="Start datetime (YYYY-MM-DD HH:MM)")
    parser.add_argument("--to", dest="to_dt", type=str, help="End datetime (YYYY-MM-DD HH:MM)")
    parser.add_argument("--send", action="store_true", help="Send summary via Telegram")

    args = parser.parse_args()

    # Ensure DB is initialized
    init_db()

    if args.command == "load-sample":
        load_sample_data()
    elif args.command == "collect-bot":
        run_collector_bot()
    elif args.command == "collect-userbot":
        run_collector_userbot()
    elif args.command == "list-chats":
        run_list_chats()
    elif args.command == "backfill-userbot":
        run_backfill(args.days, args.object)
    elif args.command == "extract":
        run_extraction(args.object)
    elif args.command == "summary":
        start_dt = parse_dt(args.from_dt)
        end_dt = parse_dt(args.to_dt)
        
        if not start_dt and not end_dt:
            if args.minutes is not None:
                start_dt = datetime.now() - timedelta(minutes=args.minutes)
            elif args.hours is not None:
                start_dt = datetime.now() - timedelta(hours=args.hours)
            else:
                start_dt = datetime.now() - timedelta(hours=24)
                
        run_custom_summary(
            chat_id=args.chat_id, 
            object_name=args.object, 
            chat_title=args.chat,
            start_dt=start_dt, 
            end_dt=end_dt,
            send=args.send
        )
    elif args.command == "report":
        md_path = generate_and_save_report(args.date, args.object)
        excel_path = export_to_excel(args.date, args.object)
        print(f"Reports generated: {md_path}, {excel_path}")
    elif args.command == "send-report":
        suffix = f"_{args.object}" if args.object else ""
        md_path = f"data/report_{args.date}{suffix}.md"
        excel_path = f"data/report_{args.date}{suffix}.xlsx"
        run_send_report(md_path, excel_path)
    elif args.command == "daily-report":
        print("Running daily report pipeline...")
        run_extraction(args.object)
        md_path = generate_and_save_report(args.date, args.object)
        excel_path = export_to_excel(args.date, args.object)
        run_send_report(md_path, excel_path)

if __name__ == "__main__":
    main()
