# HoneyNet Enhanced - פקודות פריסה שלב אחר שלב

## 🔧 שלב 1: הכנת קובץ המפתח
```bash
# תיקון הרשאות קובץ המפתח (Windows)
icacls "honeynet-key-zeev.pem" /inheritance:r
icacls "honeynet-key-zeev.pem" /grant:r "%USERNAME%:R"
```

## 📤 שלב 2: העלאת קבצים לשרת
```bash
# העלאת חבילת הפריסה לשרת
scp -i "honeynet-key-zeev.pem" honeynet_enhanced_deployment_20250807_024336.zip ubuntu@18.209.27.121:/home/ubuntu/

# חיבור לשרת
ssh -i "honeynet-key-zeev.pem" ubuntu@18.209.27.121
```

## 📦 שלב 3: חילוץ וארגון קבצים (בשרת)
```bash
# חילוץ הקבצים
cd /home/ubuntu
unzip honeynet_enhanced_deployment_20250807_024336.zip

# העברה למיקום הסופי
sudo mkdir -p /opt/honeynet
sudo mv deployment_package/* /opt/honeynet/
sudo chown -R ubuntu:ubuntu /opt/honeynet
```

## 🐍 שלב 4: התקנת Python ותלויות (בשרת)
```bash
# עדכון המערכת
sudo apt update && sudo apt upgrade -y

# התקנת Python ו-pip
sudo apt install -y python3 python3-pip python3-venv

# יצירת סביבה וירטואלית
cd /opt/honeynet
python3 -m venv venv
source venv/bin/activate

# התקנת תלויות
pip install -r requirements.txt
```

## ⚙️ שלב 5: הגדרת סביבה (בשרת)
```bash
# העתקת קובץ הגדרות
cd /opt/honeynet
cp .env.example .env

# עריכת הגדרות (תצטרך לערוך ידנית)
nano .env
```

## 🌐 שלב 6: התקנת ותצורת Nginx (בשרת)
```bash
# התקנת Nginx
sudo apt install -y nginx

# העתקת תצורת Nginx
sudo cp /opt/honeynet/nginx.conf /etc/nginx/sites-available/honeynet
sudo ln -s /etc/nginx/sites-available/honeynet /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# בדיקת תצורה
sudo nginx -t

# הפעלת Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## 🔐 שלב 7: התקנת תעודת SSL (בשרת)
```bash
# התקנת Certbot
sudo apt install -y certbot python3-certbot-nginx

# קבלת תעודת SSL
sudo certbot --nginx -d wins-technologies.com -d www.wins-technologies.com
```

## 🚀 שלב 8: הגדרת שירות systemd (בשרת)
```bash
# העתקת קובץ השירות
sudo cp /opt/honeynet/honeynet.service /etc/systemd/system/

# הפעלת השירות
sudo systemctl daemon-reload
sudo systemctl enable honeynet
sudo systemctl start honeynet

# בדיקת סטטוס
sudo systemctl status honeynet
```

## 🔍 שלב 9: בדיקת תקינות (בשרת)
```bash
# בדיקת יציאות פתוחות
sudo netstat -tlnp | grep :8000

# בדיקת לוגים
sudo journalctl -u honeynet -f

# בדיקת Nginx
sudo systemctl status nginx

# בדיקת חיבור מקומי
curl http://localhost:8000
```

## 🌍 שלב 10: הגדרת DNS (בפאנל הדומיין)
```
1. היכנס לפאנל הניהול של wins-technologies.com
2. מצא את הגדרות DNS/Name Servers
3. ערוך/הוסף רשומת A:
   - Name: @ (או wins-technologies.com)
   - Type: A
   - Value: 18.209.27.121
   - TTL: 300 (או ברירת מחדל)
4. ערוך/הוסף רשומת A עבור www:
   - Name: www
   - Type: A  
   - Value: 18.209.27.121
   - TTL: 300
5. שמור את השינויים
```

## ✅ שלב 11: אימות סופי
```bash
# בדיקת גישה לאתר
curl -I http://wins-technologies.com
curl -I https://wins-technologies.com

# בדיקת קבצי הורדה
curl -I http://wins-technologies.com/downloads/HoneyNet-Setup-v2.0.1.exe
```

---

## 📋 רשימת בדיקות לפני פריסה:
- [ ] קובץ המפתח תקין ונגיש
- [ ] חבילת הפריסה נוצרה בהצלחה
- [ ] חיבור לשרת עובד
- [ ] Python ו-pip מותקנים
- [ ] Nginx מותקן ומוגדר
- [ ] DNS מוגדר נכון
- [ ] תעודת SSL פעילה
- [ ] השירות רץ ותקין

## 🚨 פתרון בעיות נפוצות:
```bash
# אם השירות לא מתחיל
sudo journalctl -u honeynet --no-pager

# אם Nginx לא עובד
sudo nginx -t
sudo systemctl status nginx

# אם יש בעיות הרשאות
sudo chown -R ubuntu:ubuntu /opt/honeynet
sudo chmod +x /opt/honeynet/server/enhanced_main.py

# אם יש בעיות עם Python modules
cd /opt/honeynet
source venv/bin/activate
pip install --upgrade -r requirements.txt
```
