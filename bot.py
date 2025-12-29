import os
import sqlite3
import logging
import asyncio
import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Enhanced Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs.txt'
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8402033676:AAGTn3_cFb0l0wLeBnHDnVG7ObbBlumHlBA")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7166967787"))

# Database Management
class Database:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users 
                         (user_id INTEGER PRIMARY KEY, 
                          username TEXT, 
                          join_date TEXT)''')
            conn.commit()

    def add_user(self, user_id, username):
        join_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, ?)", 
                      (user_id, username, join_date))
            conn.commit()

    def get_all_users(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM users")
            return [row[0] for row in c.fetchall()]

    def get_user_count(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            return c.fetchone()[0]

db = Database()

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username)
    
    welcome_text = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to the Advanced Bot Control System.\n"
        "I am alive and ready to serve.\n\n"
        "Available Commands:\n"
        "/start - Show this message\n"
        "/ping - Check if I'm alive\n"
        "/stats - View bot statistics"
    )
    
    if user.id == ADMIN_ID:
        welcome_text += "\n\n👑 Admin Commands:\n/broadcast <msg> - Send message to all"
        
    await update.message.reply_text(welcome_text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = datetime.datetime.now()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = datetime.datetime.now()
    latency = (end_time - start_time).microseconds / 1000
    await msg.edit_text(f"🚀 Bot is alive!\nLatency: {latency}ms")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = db.get_user_count()
    await update.message.reply_text(f"📊 Bot Statistics:\nTotal Users: {count}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return

    if not context.args:
        await update.message.reply_text("📝 Usage: /broadcast <your message>")
        return

    message_text = " ".join(context.args)
    users = db.get_all_users()
    success, fail = 0, 0
    
    status_msg = await update.message.reply_text(f"📤 Starting broadcast to {len(users)} users...")
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 BROADCAST:\n\n{message_text}")
            success += 1
        except Exception as e:
            logger.error(f"Broadcast failed for {user_id}: {e}")
            fail += 1
            
    await status_msg.edit_text(f"✅ Broadcast Complete!\n\n✨ Success: {success}\n❌ Failed: {fail}")

class TelegramBot:
    def __init__(self):
        self.application = None
        self.is_running = False
        self._stop_event = asyncio.Event()

    async def run(self):
        try:
            self.application = ApplicationBuilder().token(BOT_TOKEN).build()
            
            # Add Handlers
            self.application.add_handler(CommandHandler("start", start))
            self.application.add_handler(CommandHandler("ping", ping))
            self.application.add_handler(CommandHandler("stats", stats))
            self.application.add_handler(CommandHandler("broadcast", broadcast))
            
            self.is_running = True
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Bot started successfully")
            await self._stop_event.wait()
            
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            self.is_running = False
            self._stop_event.clear()

    def stop(self):
        self._stop_event.set()

bot_instance = TelegramBot()
