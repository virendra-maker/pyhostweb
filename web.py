import os
import sqlite3
import threading
import asyncio
import subprocess
import signal
from flask import Flask, render_template_string, request, redirect, url_for
from bot import bot_instance

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Storage for hosted scripts
SCRIPTS_DIR = "hosted_scripts"
if not os.path.exists(SCRIPTS_DIR):
    os.makedirs(SCRIPTS_DIR)

# Track running processes
running_processes = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyHostWeb - Control Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 50px; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .status-running { color: #28a745; font-weight: bold; }
        .status-stopped { color: #dc3545; font-weight: bold; }
        .nav-tabs .nav-link.active { font-weight: bold; border-bottom: 3px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="text-center mb-4">
                    <h1 class="display-4">🚀 PyHostWeb</h1>
                    <p class="lead">Professional Python Bot & Script Hosting Panel</p>
                </div>

                <ul class="nav nav-tabs mb-4" id="myTab" role="tablist">
                    <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#bot">Telegram Bot</a></li>
                    <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#scripts">Host Scripts</a></li>
                </ul>

                <div class="tab-content">
                    <!-- Bot Control Tab -->
                    <div class="tab-pane fade show active" id="bot">
                        <div class="card p-4">
                            <h3>🤖 Bot Status</h3>
                            <hr>
                            <div class="row align-items-center">
                                <div class="col-sm-6">
                                    <p>Current Status: <span class="{{ 'status-running' if bot_status == 'Running' else 'status-stopped' }}">{{ bot_status }}</span></p>
                                    <p>Total Registered Users: <strong>{{ user_count }}</strong></p>
                                </div>
                                <div class="col-sm-6 text-end">
                                    {% if bot_status == 'Stopped' %}
                                    <a href="/start-bot" class="btn btn-success btn-lg">Start Bot</a>
                                    {% else %}
                                    <a href="/stop-bot" class="btn btn-danger btn-lg">Stop Bot</a>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Script Hosting Tab -->
                    <div class="tab-pane fade" id="scripts">
                        <div class="card p-4">
                            <h3>📂 Script Hosting</h3>
                            <hr>
                            <form action="/upload-script" method="post" enctype="multipart/form-data" class="mb-4">
                                <div class="input-group">
                                    <input type="file" name="script" class="form-control" accept=".py" required>
                                    <button type="submit" class="btn btn-primary">Upload & Run</button>
                                </div>
                            </form>

                            <h4>Running Scripts</h4>
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Script Name</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for name, pid in running_scripts.items() %}
                                    <tr>
                                        <td>{{ name }}</td>
                                        <td><span class="status-running">Running (PID: {{ pid }})</span></td>
                                        <td><a href="/stop-script/{{ name }}" class="btn btn-sm btn-danger">Stop</a></td>
                                    </tr>
                                    {% endfor %}
                                    {% if not running_scripts %}
                                    <tr><td colspan="3" class="text-center text-muted">No scripts running</td></tr>
                                    {% endif %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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

@app.route('/')
def index():
    bot_status = "Running" if bot_instance.is_running else "Stopped"
    user_count = get_user_count()
    # Clean up finished processes
    for name in list(running_processes.keys()):
        if running_processes[name].poll() is not None:
            del running_processes[name]
            
    running_scripts = {name: proc.pid for name, proc in running_processes.items()}
    return render_template_string(HTML_TEMPLATE, 
                                bot_status=bot_status, 
                                user_count=user_count,
                                running_scripts=running_scripts)

@app.route('/start-bot')
def start_bot():
    if not bot_instance.is_running:
        threading.Thread(target=run_bot_in_thread, daemon=True).start()
    return redirect(url_for('index'))

@app.route('/stop-bot')
def stop_bot():
    if bot_instance.is_running:
        bot_instance.stop()
    return redirect(url_for('index'))

@app.route('/upload-script', methods=['POST'])
def upload_script():
    if 'script' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['script']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.py'):
        filepath = os.path.join(SCRIPTS_DIR, file.filename)
        file.save(filepath)
        
        # Run the script
        process = subprocess.Popen(['python3', filepath])
        running_processes[file.filename] = process
        
    return redirect(url_for('index'))

@app.route('/stop-script/<name>')
def stop_script(name):
    if name in running_processes:
        process = running_processes[name]
        process.terminate()
        del running_processes[name]
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
