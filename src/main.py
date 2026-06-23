import argparse
import sys
from datetime import datetime

from .db import init_db
from .sample_loader import load_sample_data
from .extractor import run_extraction
from .report_builder import generate_and_save_report
from .excel_exporter import export_to_excel
from .telegram_sender import run_send_report
from .telegram_collector_bot import run_collector_bot
from .telegram_collector_userbot import run_collector_userbot

def main():
    parser = argparse.ArgumentParser(description="Telegram Construction Chat Analyst MVP")
    parser.add_argument("command", choices=[
        "load-sample", 
        "collect-bot", 
        "collect-userbot", 
        "extract", 
        "report", 
        "send-report", 
        "daily-report"
    ], help="Command to run")
    parser.add_argument("--date", type=str, help="Date for report (YYYY-MM-DD)", default=datetime.now().strftime('%Y-%m-%d'))

    args = parser.parse_args()

    # Ensure DB is initialized
    init_db()

    if args.command == "load-sample":
        load_sample_data()
    elif args.command == "collect-bot":
        run_collector_bot()
    elif args.command == "collect-userbot":
        run_collector_userbot()
    elif args.command == "extract":
        run_extraction()
    elif args.command == "report":
        md_path = generate_and_save_report(args.date)
        excel_path = export_to_excel(args.date)
        print(f"Reports generated: {md_path}, {excel_path}")
    elif args.command == "send-report":
        md_path = f"data/report_{args.date}.md"
        excel_path = f"data/report_{args.date}.xlsx"
        run_send_report(md_path, excel_path)
    elif args.command == "daily-report":
        print("Running daily report pipeline...")
        run_extraction()
        md_path = generate_and_save_report(args.date)
        excel_path = export_to_excel(args.date)
        run_send_report(md_path, excel_path)

if __name__ == "__main__":
    main()
