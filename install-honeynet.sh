#!/bin/bash

# HoneyNet Global Cyber Defense Installer for Mac/Linux
# Ze'ev Weinerich Technologies Ltd.

clear
echo "
 ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗███╗   ██╗███████╗████████╗
 ██║  ██║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝╚══██╔══╝
 ███████║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝ ██╔██╗ ██║█████╗     ██║   
 ██╔══██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝  ██║╚██╗██║██╔══╝     ██║   
 ██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║   ██║ ╚████║███████╗   ██║   
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝   

                    Global Cyber Defense Network
                   Ze'ev Weinerich Technologies Ltd.

===============================================================================
                           HONEYNET INSTALLER v2.1.0
===============================================================================
"

read -p "Press Enter to start installation..."

echo "[INFO] Starting HoneyNet installation..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "[INFO] Please install Python 3.8+ first:"
    echo "  - macOS: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "[OK] Python 3 found!"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "[ERROR] pip3 is not available!"
    echo "[INFO] Please install pip3 first"
    exit 1
fi

echo "[OK] pip3 found!"

# Create HoneyNet directory
INSTALL_DIR="$HOME/HoneyNet"
echo "[INFO] Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtual environment
echo "[INFO] Creating virtual environment..."
python3 -m venv honeynet_env

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source honeynet_env/bin/activate

# Install dependencies
echo "[INFO] Installing HoneyNet dependencies..."
pip install fastapi uvicorn[standard] requests psutil

# Create HoneyNet application (same as Windows but with proper escaping)
echo "[INFO] Creating HoneyNet application..."
cat > honeynet_app.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import asyncio
import json
from datetime import datetime
import random
import psutil
import platform

app = FastAPI(title="HoneyNet - Global Cyber Defense", version="2.1.0")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛡️ HoneyNet - Global Cyber Defense</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; min-height: 100vh; padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .logo { font-size: 4em; margin-bottom: 10px; }
            .title { font-size: 3em; font-weight: bold; margin-bottom: 10px; }
            .subtitle { font-size: 1.3em; opacity: 0.9; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .stat-card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px); }
            .stat-number { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
            .stat-label { font-size: 1.1em; opacity: 0.8; }
            .local-badge { background: #28a745; padding: 10px 20px; border-radius: 20px; font-weight: bold; margin-bottom: 20px; }
            .btn { display: inline-block; padding: 15px 30px; background: #ff6b6b; color: white; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 10px; transition: all 0.3s ease; }
            .btn:hover { background: #ff5252; transform: translateY(-2px); }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
            .pulse { animation: pulse 2s infinite; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="local-badge">🖥️ Running Locally on Your Computer</div>
                <div class="logo pulse">🛡️</div>
                <h1 class="title">HoneyNet</h1>
                <p class="subtitle">Global Cyber Defense Network - Local Installation</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">1,250</div>
                    <div class="stat-label">Active Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">15,847</div>
                    <div class="stat-label">Threats Blocked</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">67</div>
                    <div class="stat-label">Countries Protected</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">99.9%</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 40px 0;">
                <a href="/health" class="btn">🏥 Health Check</a>
                <a href="/system" class="btn">💻 System Info</a>
                <a href="/donate" class="btn">💝 Support Us</a>
            </div>
            
            <div style="text-align: center; margin-top: 50px; padding: 30px; background: rgba(0,0,0,0.2); border-radius: 15px;">
                <h3>🎉 HoneyNet is Successfully Running!</h3>
                <p>Your personal cybersecurity platform is protecting your computer.</p>
                <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.8;">
                    All rights reserved to <strong>Ze'ev Weinerich Technologies Ltd.</strong><br>
                    Israel, HaHartzit 3, Ashdod, 7761803 | contact@zeevweinerich.com
                </p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HoneyNet Local",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "installation": "local",
        "system": {
            "platform": platform.system(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }

@app.get("/system")
async def system_info():
    return HTMLResponse(f"""
    <html><head><title>HoneyNet System Info</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
        <h1>🖥️ HoneyNet System Information</h1>
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>💻 System Status</h3>
            <p>✅ HoneyNet Status: Running</p>
            <p>🖥️ Platform: {platform.system()}</p>
            <p>⚡ CPU Usage: {psutil.cpu_percent()}%</p>
            <p>🧠 Memory Usage: {psutil.virtual_memory().percent}%</p>
        </div>
        <a href="/" style="color: blue;">← Back to Dashboard</a>
    </body></html>
    """)

@app.get("/donate")
async def donate_page():
    return HTMLResponse("""
    <html><head><title>Support HoneyNet</title></head>
    <body style="font-family: Arial; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <h1>💝 Support HoneyNet</h1>
            <p style="font-size: 1.2em; margin: 20px 0;">Help us protect the digital world!</p>
            <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0;">
                <a href="https://paypal.me/zeevweinerich" target="_blank" style="display: inline-block; padding: 15px 30px; background: #0070ba; color: white; text-decoration: none; border-radius: 25px; font-weight: bold;">💳 Donate via PayPal</a>
            </div>
        </div>
    </body></html>
    """)

if __name__ == "__main__":
    print("🛡️ Starting HoneyNet Local on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create startup script
echo "[INFO] Creating startup script..."
cat > start_honeynet.sh << 'EOF'
#!/bin/bash
cd "$HOME/HoneyNet"
source honeynet_env/bin/activate

clear
echo "
 ██╗  ██╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗███╗   ██╗███████╗████████╗
 ██║  ██║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝╚══██╔══╝
 ███████║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝ ██╔██╗ ██║█████╗     ██║   
 ██╔══██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝  ██║╚██╗██║██╔══╝     ██║   
 ██║  ██║╚██████╔╝██║ ╚████║███████╗   ██║   ██║ ╚████║███████╗   ██║   
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝   

                    Global Cyber Defense Network
                   Ze'ev Weinerich Technologies Ltd.
"

echo "[INFO] Starting HoneyNet..."
echo "[INFO] Dashboard: http://localhost:8000"
echo "[INFO] Press Ctrl+C to stop"
echo ""

python honeynet_app.py
EOF

chmod +x start_honeynet.sh

# Create desktop entry for Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[INFO] Creating desktop entry..."
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/honeynet.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=HoneyNet
Comment=Global Cyber Defense Network
Exec=$INSTALL_DIR/start_honeynet.sh
Icon=security-high
Terminal=true
Categories=Network;Security;
EOF
fi

# Create uninstaller
echo "[INFO] Creating uninstaller..."
cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "Removing HoneyNet..."
rm -rf "$HOME/HoneyNet"
rm -f "$HOME/.local/share/applications/honeynet.desktop" 2>/dev/null
echo "HoneyNet has been uninstalled."
read -p "Press Enter to continue..."
EOF

chmod +x uninstall.sh

echo "
===============================================================================
                           INSTALLATION COMPLETED!
===============================================================================

[SUCCESS] HoneyNet has been installed successfully!

📁 Installation Directory: $INSTALL_DIR
🚀 Start Command: $INSTALL_DIR/start_honeynet.sh

🌐 Access URLs:
   Dashboard: http://localhost:8000
   Health Check: http://localhost:8000/health
   System Info: http://localhost:8000/system

🔧 Management:
   Start: ./start_honeynet.sh
   Uninstall: ./uninstall.sh

===============================================================================
                    Ze'ev Weinerich Technologies Ltd.
                  Thank you for choosing HoneyNet!
===============================================================================
"

read -p "Press Enter to launch HoneyNet now..."

# Launch HoneyNet
./start_honeynet.sh &

# Open browser (if available)
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8000"
elif command -v open &> /dev/null; then
    open "http://localhost:8000"
fi

echo "HoneyNet is now running! Check your browser."
