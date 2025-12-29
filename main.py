import installer

# Auto-install missing modules before anything else
installer.install_modules()

import os
import sys
from web import app

if __name__ == "__main__":
    # Check for environment variables
    if not os.environ.get("BOT_TOKEN") or not os.environ.get("ADMIN_ID"):
        print("ERROR: BOT_TOKEN and ADMIN_ID environment variables are missing!")
        sys.exit(1)
        
    print("Starting Flask Website on port 8000...")
    app.run(host='0.0.0.0', port=8000)
