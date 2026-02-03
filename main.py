import installer

# 1. Auto-install missing modules
print("Checking dependencies...")
installer.install_modules()

import os
import sys
from web import app
def keep_render_alive():

    
    RENDER_URL = "https://pyhostwebby.onrender.com/"
    
    def ping_render():
        while True:
            try:
                # Wait 5 minutes (300 seconds)
                time.sleep(300)
                
                current_time = datetime.now().strftime("%H:%M:%S")
                
                try:
                    # Ping the Render URL
                    response = requests.get(f"{RENDER_URL}/", timeout=10)
                    print(f"[RENDER PING] ✅ Ping successful at {current_time} - Status: {response.status_code}")
                except Exception as e:
                    print(f"[RENDER PING] ❌ Failed at {current_time}: {e}")
                    
            except Exception as e:
                print(f"[RENDER PING] ❌ Error in ping thread: {e}")
                time.sleep(60)
    
    ping_thread = threading.Thread(target=ping_render, daemon=True)
    ping_thread.start()
    print(f"[RENDER PING] 🚀 Auto-ping started: {RENDER_URL} (every 5 minutes)")

# 2. Set default credentials if not in environment
if not os.environ.get("BOT_TOKEN"):
    os.environ["BOT_TOKEN"] = "8402033676:AAGTn3_cFb0l0wLeBnHDnVG7ObbBlumHlBA"
if not os.environ.get("ADMIN_ID"):
    os.environ["ADMIN_ID"] = "7166967787"

if __name__ == "__main__":
    print("="*40)
    print("🚀 PyHostWeb Control Panel Starting...")
    print(f"📍 URL: http://localhost:8000")
    print(f"🤖 Bot Token: {os.environ['BOT_TOKEN'][:10]}...")
    print(f"👑 Admin ID: {os.environ['ADMIN_ID']}")
    print("="*40)
    
    # Start Flask
    app.run(host='0.0.0.0', port=8000, debug=False)
