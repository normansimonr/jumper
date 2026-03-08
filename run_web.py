import os
import sys
import webbrowser
import threading
import time
import subprocess

def install_dependencies():
    print("Verificando dependencias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

def start_browser():
    # Wait a bit for the server to start
    time.sleep(1.5)
    print("Abriendo navegador en http://localhost:5000")
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    try:
        from flask import Flask
    except ImportError:
        install_dependencies()

    from app import app
    
    # Start browser in a separate thread
    threading.Thread(target=start_browser, daemon=True).start()
    
    print("Iniciando Jumper Web Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
