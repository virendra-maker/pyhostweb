import installer

# 1. Auto-install missing modules
print("Checking dependencies...")
installer.install_modules()

import os
import sys
from web import app

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
