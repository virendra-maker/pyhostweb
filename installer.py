import subprocess
import sys

def install_modules():
    required_modules = [
        'flask',
        'python-telegram-bot',
        'requests'
    ]
    
    for module in required_modules:
        try:
            if module == 'python-telegram-bot':
                import telegram
            else:
                __import__(module)
        except ImportError:
            print(f"Installing {module}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])

if __name__ == "__main__":
    install_modules()
