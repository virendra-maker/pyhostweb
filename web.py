import sqlite3
import threading
import asyncio
from flask import Flask, render_template_string
from bot import bot_instance

app = Flask(__name__)
PASSWORD = "admin"  # Hardcoded password

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bot Control Panel</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .status { font-weight: bold; color: {{ 'green' if status == 'Running' else 'red' }}; }
        .btn { padding: 10px 20px; margin: 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Telegram Bot Control Panel</h1>
    <p>Status: <span class="status">{{ status }}</span></p>
    <p>Total Users: {{ user_count }}</p>
    <form action="/start-bot" method="get" style="display: inline;">
        <button class="btn" type="submit">Start Bot</button>
    </form>
    <form action="/stop-bot" method="get" style="display: inline;">
        <button class="btn" type="submit">Stop Bot</button>
    </form>
</body>
</html>
"""

def get_user_count():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

def run_bot_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_instance.run())

bot_thread = None

@app.route('/')
def index():
    status = "Running" if bot_instance.is_running else "Stopped"
    user_count = get_user_count()
    return render_template_string(HTML_TEMPLATE, status=status, user_count=user_count)

@app.route('/start-bot')
def start_bot():
    global bot_thread
    if not bot_instance.is_running:
        bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
        bot_thread.start()
    return "Bot starting... <a href='/'>Back</a>"

@app.route('/stop-bot')
def stop_bot():
    if bot_instance.is_running:
        bot_instance.stop()
    return "Bot stopping... <a href='/'>Back</a>"

if __name__ == "__main__":
    app.run(port=8000)
