# 🚀 הגדרת AWS Instance חדש עבור HoneyNet

## 📋 שלב 1: יצירת Instance חדש

### בAWS Console:
1. לחץ על **"Launch instances"** (הכפתור הכתום)
2. הגדר את הפרמטרים הבאים:

**Name and tags:**
- Name: `HoneyNet-Enhanced-Server`

**Application and OS Images:**
- AMI: `Ubuntu Server 22.04 LTS (HVM), SSD Volume Type`
- Architecture: `64-bit (x86)`

**Instance type:**
- בחר: `t3.medium` (2 vCPU, 4 GiB RAM) - מומלץ לביצועים טובים
- או `t2.micro` (1 vCPU, 1 GiB RAM) - אם אתה ב-Free Tier

**Key pair (login):**
- בחר את המפתח הקיים שלך או צור חדש
- אם אתה יוצר חדש, תן לו שם: `honeynet-enhanced-key`

**Network settings:**
- VPC: Default
- Subnet: Default
- Auto-assign public IP: **Enable**
- Firewall (security groups): **Create security group**
  - Security group name: `honeynet-enhanced-sg`
  - Description: `Security group for HoneyNet Enhanced`
  - **Add rules:**
    - SSH (22) - Source: My IP
    - HTTP (80) - Source: Anywhere (0.0.0.0/0)
    - HTTPS (443) - Source: Anywhere (0.0.0.0/0)
    - Custom TCP (8000) - Source: Anywhere (0.0.0.0/0) - לשרת HoneyNet

**Configure storage:**
- Size: `20 GiB` (מינימום)
- Volume type: `gp3`

3. לחץ **"Launch instance"**

## 🔧 שלב 2: חיבור לInstance החדש

לאחר שה-Instance נוצר:

1. חזור לרשימת Instances
2. בחר את ה-Instance החדש
3. לחץ **"Connect"**
4. בחר **"EC2 Instance Connect"** (הכי פשוט)
5. לחץ **"Connect"**

## 📤 שלב 3: העלאת קבצי הפריסה

### אפשרות A: דרך EC2 Instance Connect
```bash
# הורדת הקובץ מGoogle Drive/WeTransfer (אם העלית שם)
wget "YOUR_DOWNLOAD_LINK" -O deployment.zip

# או יצירת הקובץ מחדש בשרת
mkdir -p /tmp/honeynet-deploy
cd /tmp/honeynet-deploy
```

### אפשרות B: העתקה ידנית של קבצים חשובים
במקום להעלות את כל הקובץ, בואו נעתיק את הקבצים החשובים ביותר:

```bash
# יצירת מבנה תיקיות
mkdir -p /opt/honeynet/{server,core,config,templates}
cd /opt/honeynet

# יצירת קובץ requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
aiosqlite==0.19.0
cryptography==41.0.7
pyjwt==2.8.0
redis==5.0.1
psycopg2-binary==2.9.9
jinja2==3.1.2
python-multipart==0.0.6
websockets==12.0
pydantic==2.5.0
httpx==0.25.2
python-dotenv==1.0.0
EOF

# התקנת תלויות
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🌐 שלב 4: יצירת קבצים בסיסיים בשרת

```bash
# יצירת שרת בסיסי
cat > server/main.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="HoneyNet Enhanced", version="2.0.1")

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>HoneyNet Enhanced - Coming Soon</title></head>
        <body>
            <h1>🛡️ HoneyNet Enhanced System</h1>
            <p>System is being deployed...</p>
            <p>Version 2.0.1 Enhanced</p>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# הפעלת השרת לבדיקה
cd /opt/honeynet
source venv/bin/activate
python server/main.py
```

## 🔗 שלב 5: הגדרת Nginx

```bash
# יצירת תצורת Nginx
sudo tee /etc/nginx/sites-available/honeynet << 'EOF'
server {
    listen 80;
    server_name wins-technologies.com www.wins-technologies.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# הפעלת התצורה
sudo ln -s /etc/nginx/sites-available/honeynet /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## 📝 שלב 6: קבלת IP החדש ועדכון DNS

1. ב-AWS Console, העתק את ה-**Public IPv4 address** של ה-Instance החדש
2. עדכן את רשומת ה-DNS של `wins-technologies.com` לכתובת החדשה
3. המתן לעדכון DNS (עד 48 שעות)

## ✅ בדיקת תקינות

```bash
# בדיקה מקומית בשרת
curl http://localhost:8000/health

# בדיקה חיצונית (החלף IP)
curl http://YOUR_NEW_IP/health
```
