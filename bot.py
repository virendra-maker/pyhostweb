import os
import sqlite3
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs.txt'
)

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")

if not BOT_TOKEN or not ADMIN_ID:
    raise ValueError("BOT_TOKEN and ADMIN_ID environment variables must be set.")

ADMIN_ID = int(ADMIN_ID)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    await update.message.reply_text("Welcome! You have been registered.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return

    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    users = get_all_users()
    count = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message_text)
            count += 1
        except Exception as e:
            logging.error(f"Failed to send message to {user_id}: {e}")

    await update.message.reply_text(f"Broadcast sent to {count} users.")

class TelegramBot:
    def __init__(self):
        self.application = None
        self.is_running = False

    async def run(self):
        init_db()
        self.application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("ping", ping))
        self.application.add_handler(CommandHandler("broadcast", broadcast))
        
        self.is_running = True
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        while self.is_running:
            await asyncio.sleep(1)
            
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

    def stop(self):
        self.is_running = False

bot_instance = TelegramBot()
