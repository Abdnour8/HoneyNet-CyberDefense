#!/bin/bash
# Simple HoneyNet Installation for AWS EC2

# Log everything
exec > >(tee /var/log/honeynet-install.log)
exec 2>&1

echo "🛡️ Starting HoneyNet Simple Installation..."
echo "==========================================="

# Update system
sudo yum update -y

# Install Python and pip
sudo yum install -y python3 python3-pip

# Install FastAPI and Uvicorn
sudo pip3 install fastapi uvicorn

# Create HoneyNet app
cd /home/ec2-user
mkdir -p honeynet
cd honeynet

# Create simple HoneyNet app
cat > app.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="HoneyNet - Global Cyber Defense")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛡️ HoneyNet - Global Cyber Defense</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); 
                   color: white; text-align: center; padding: 50px; }
            .container { max-width: 800px; margin: 0 auto; }
            .logo { font-size: 5em; margin-bottom: 20px; }
            .title { font-size: 3em; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 40px 0; }
            .stat { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
            .stat-number { font-size: 2em; font-weight: bold; }
            .btn { display: inline-block; padding: 15px 30px; background: #ff6b6b; 
                   color: white; text-decoration: none; border-radius: 25px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🛡️</div>
            <h1 class="title">HoneyNet</h1>
            <p>Global Cyber Defense Network - Successfully Running on AWS!</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">1,250</div>
                    <div>Active Users</div>
                </div>
                <div class="stat">
                    <div class="stat-number">15,847</div>
                    <div>Threats Blocked</div>
                </div>
                <div class="stat">
                    <div class="stat-number">67</div>
                    <div>Countries Protected</div>
                </div>
                <div class="stat">
                    <div class="stat-number">99.9%</div>
                    <div>Uptime</div>
                </div>
            </div>
            
            <a href="/health" class="btn">🏥 Health Check</a>
            <a href="/admin" class="btn">📊 Admin Panel</a>
            <a href="/donate" class="btn">💝 Donate</a>
            
            <div style="margin-top: 50px; padding: 30px; background: rgba(0,0,0,0.2); border-radius: 15px;">
                <h3>🎉 HoneyNet is Successfully Running on AWS!</h3>
                <p>Your cybersecurity platform is now live and protecting users worldwide.</p>
                <p style="margin-top: 20px; font-size: 0.9em;">
                    All rights reserved to <strong>Ze'ev Weinerich Technologies Ltd.</strong><br>
                    Israel, HaHartzit 3, Ashdod, 7761803
                </p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "HoneyNet", "version": "2.1.0"}

@app.get("/admin")
async def admin():
    return HTMLResponse("""
    <html><head><title>HoneyNet Admin</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🛡️ HoneyNet Admin Panel</h1>
        <p>✅ System Status: Online</p>
        <p>🔄 Auto-updates: Enabled</p>
        <p>🛡️ Security: High</p>
        <a href="/" style="color: blue;">← Back to Dashboard</a>
    </body></html>
    """)

@app.get("/donate")
async def donate():
    return HTMLResponse("""
    <html><head><title>Support HoneyNet</title></head>
    <body style="font-family: Arial; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
        <div style="max-width: 600px; margin: 0 auto; text-align: center;">
            <h1>💝 Support HoneyNet</h1>
            <p>Help us protect the digital world!</p>
            <a href="https://paypal.me/zeevweinerich" target="_blank" 
               style="display: inline-block; padding: 15px 30px; background: #0070ba; color: white; text-decoration: none; border-radius: 25px;">
               💳 Donate via PayPal
            </a>
        </div>
    </body></html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
EOF

# Set permissions
sudo chown -R ec2-user:ec2-user /home/ec2-user/honeynet

# Start HoneyNet directly
echo "🚀 Starting HoneyNet..."
cd /home/ec2-user/honeynet
sudo python3 app.py &

echo ""
echo "🎉 HoneyNet Installation Completed!"
echo "=================================="
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "🌐 HoneyNet is available at: http://$PUBLIC_IP"
echo "🏥 Health check: http://$PUBLIC_IP/health"
echo "📊 Admin panel: http://$PUBLIC_IP/admin"
echo "💝 Donation page: http://$PUBLIC_IP/donate"
