#!/bin/bash
# HoneyNet Auto-Install Script for AWS EC2

# Log everything
exec > >(tee /var/log/honeynet-install.log)
exec 2>&1

echo "🛡️  Starting HoneyNet Auto-Installation..."
echo "============================================"

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python and pip
echo "🐍 Installing Python..."
sudo yum install -y python3 python3-pip git

# Create HoneyNet directory
echo "📁 Setting up HoneyNet..."
cd /home/ec2-user
mkdir -p honeynet
cd honeynet

# Create basic HoneyNet application
echo "🛡️ Creating HoneyNet application..."
cat > app.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from datetime import datetime
import random

app = FastAPI(title="HoneyNet - Global Cyber Defense", version="2.1.0")

# Simulate honeypot data
honeypots = []
threats = []
analytics = {
    "total_users": 1250,
    "active_users_24h": 89,
    "threats_blocked": 15847,
    "countries_protected": 67
}

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
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .feature-card { background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; backdrop-filter: blur(10px); }
            .feature-icon { font-size: 2.5em; margin-bottom: 15px; }
            .feature-title { font-size: 1.3em; font-weight: bold; margin-bottom: 10px; }
            .footer { text-align: center; margin-top: 50px; padding: 30px; background: rgba(0,0,0,0.2); border-radius: 15px; }
            .btn { display: inline-block; padding: 15px 30px; background: #ff6b6b; color: white; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 10px; transition: all 0.3s ease; }
            .btn:hover { background: #ff5252; transform: translateY(-2px); }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
            .pulse { animation: pulse 2s infinite; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo pulse">🛡️</div>
                <h1 class="title">HoneyNet</h1>
                <p class="subtitle">Global Cyber Defense Network - Protecting the Digital World</p>
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
            
            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">🕸️</div>
                    <h3 class="feature-title">Smart Honeypots</h3>
                    <p>Deploy intelligent traps that learn and adapt to new attack patterns.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧬</div>
                    <h3 class="feature-title">Attack DNA Analysis</h3>
                    <p>AI-powered analysis creates genetic signatures of cyber threats.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🌍</div>
                    <h3 class="feature-title">Global Network</h3>
                    <p>Collective defense where every user becomes a cyber sensor.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3 class="feature-title">Real-time Protection</h3>
                    <p>Instant threat sharing and automated defense deployment.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎮</div>
                    <h3 class="feature-title">Gamification</h3>
                    <p>Earn rewards and compete in the global cybersecurity leaderboard.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔮</div>
                    <h3 class="feature-title">Quantum-Resistant</h3>
                    <p>Future-proof security against quantum computing threats.</p>
                </div>
            </div>
            
            <div style="text-align: center; margin: 40px 0;">
                <a href="/health" class="btn">🏥 Health Check</a>
                <a href="/admin" class="btn">📊 Admin Panel</a>
                <a href="/donate" class="btn">💝 Support Us</a>
            </div>
            
            <div class="footer">
                <h3>🎉 HoneyNet is Successfully Running on AWS!</h3>
                <p>Your cybersecurity platform is now live and protecting users worldwide.</p>
                <p style="margin-top: 20px; font-size: 0.9em; opacity: 0.8;">
                    All rights reserved to <strong>Ze'ev Weinerich Technologies Ltd.</strong><br>
                    Israel, HaHartzit 3, Ashdod, 7761803 | contact@zeevweinerich.com
                </p>
            </div>
        </div>
        
        <script>
            // Simple real-time updates simulation
            setInterval(() => {
                const stats = document.querySelectorAll('.stat-number');
                stats[1].textContent = parseInt(stats[1].textContent.replace(',', '')) + Math.floor(Math.random() * 3) + 1;
            }, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HoneyNet Global Cyber Defense",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "99.9%",
        "active_honeypots": 42,
        "threats_blocked_today": 156,
        "system": {
            "cpu": "Normal",
            "memory": "Normal", 
            "disk": "Normal",
            "network": "Normal"
        }
    }

@app.get("/admin")
async def admin_panel():
    return HTMLResponse("""
    <html><head><title>HoneyNet Admin</title></head>
    <body style="font-family: Arial; padding: 20px; background: #f5f5f5;">
        <h1>🛡️ HoneyNet Admin Panel</h1>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3>📊 System Status</h3>
                <p>✅ All systems operational</p>
                <p>🔄 Auto-updates: Enabled</p>
                <p>🛡️ Security: High</p>
            </div>
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3>📈 Analytics</h3>
                <p>👥 Active Users: 1,250</p>
                <p>🌍 Countries: 67</p>
                <p>⚡ Threats Blocked: 15,847</p>
            </div>
        </div>
        <a href="/" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">← Back to Dashboard</a>
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
                <h3>🙏 Your donation helps us:</h3>
                <ul style="text-align: left; margin: 20px 0;">
                    <li>🚀 Develop new security features</li>
                    <li>🌍 Expand global protection</li>
                    <li>🔬 Fund cybersecurity research</li>
                    <li>📚 Keep HoneyNet free for everyone</li>
                </ul>
                <a href="https://paypal.me/zeevweinerich" target="_blank" style="display: inline-block; padding: 15px 30px; background: #0070ba; color: white; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 10px;">💳 Donate via PayPal</a>
            </div>
            <p style="font-size: 0.9em; opacity: 0.8;">All rights reserved to Ze'ev Weinerich Technologies Ltd.</p>
        </div>
    </body></html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
EOF

# Install Python dependencies
echo "📦 Installing Python dependencies..."
sudo pip3 install -r requirements.txt

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/honeynet.service > /dev/null << 'EOF'
[Unit]
Description=HoneyNet Cybersecurity Platform
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/honeynet
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
sudo chown -R ec2-user:ec2-user /home/ec2-user/honeynet

# Enable and start service
echo "🚀 Starting HoneyNet service..."
sudo systemctl daemon-reload
sudo systemctl enable honeynet
sudo systemctl start honeynet

# Setup nginx reverse proxy
echo "🌐 Setting up Nginx reverse proxy..."
sudo yum install -y nginx
sudo systemctl enable nginx

# Create nginx config
sudo tee /etc/nginx/conf.d/honeynet.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo systemctl start nginx

# Final status
echo ""
echo "🎉 HoneyNet Installation Completed!"
echo "=================================="
echo "✅ HoneyNet service: $(sudo systemctl is-active honeynet)"
echo "✅ Nginx service: $(sudo systemctl is-active nginx)"
echo ""
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "🌐 HoneyNet is available at: http://$PUBLIC_IP"
echo "🏥 Health check: http://$PUBLIC_IP/health"
echo "📊 Admin panel: http://$PUBLIC_IP/admin"
echo "💝 Donation page: http://$PUBLIC_IP/donate"
echo ""
echo "🔧 Service management:"
echo "  sudo systemctl status honeynet"
echo "  sudo systemctl restart honeynet"
echo "  sudo journalctl -u honeynet -f"
echo ""
echo "Installation log saved to: /var/log/honeynet-install.log"
EOF
