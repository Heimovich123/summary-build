from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_REPORT_BOT_TOKEN, TELEGRAM_SOURCE_CHAT_IDS
from .db import insert_message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = msg.from_user
    
    if TELEGRAM_SOURCE_CHAT_IDS and chat.id not in TELEGRAM_SOURCE_CHAT_IDS:
        return
        
    if msg.text:
        insert_message(
            message_id=msg.message_id,
            chat_id=chat.id,
            sender_id=user.id if user else 0,
            sender_name=user.full_name if user else "Unknown",
            text=msg.text,
            timestamp=msg.date
        )
        print(f"Bot saved message from {chat.id}")

def run_collector_bot():
    if not TELEGRAM_REPORT_BOT_TOKEN:
        print("TELEGRAM_REPORT_BOT_TOKEN not set")
        return
        
    app = ApplicationBuilder().token(TELEGRAM_REPORT_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Starting bot collector...")
    app.run_polling()
