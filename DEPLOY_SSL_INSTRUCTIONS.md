# 🔒 SSL Certificate Fix for wins-technologies.com

## 📋 **Quick Deployment Instructions**

### **Step 1: Connect to Your Server**
```bash
ssh -i your-key.pem ubuntu@18.209.27.121
```

### **Step 2: Upload Deployment Package**
```bash
# From your local machine:
scp -r ssl_deployment_package ubuntu@18.209.27.121:~/
```

### **Step 3: Run Deployment Script**
```bash
# On the server:
cd ssl_deployment_package
chmod +x deploy.sh
sudo ./deploy.sh
```

---

## 🔧 **Manual SSL Fix (if automatic fails)**

### **1. Install Required Packages**
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx ufw
```

### **2. Stop Current Services**
```bash
sudo systemctl stop nginx
sudo systemctl stop apache2  # if running
```

### **3. Get SSL Certificate**
```bash
sudo certbot certonly --standalone \
  -d wins-technologies.com \
  -d www.wins-technologies.com \
  --non-interactive \
  --agree-tos \
  --email admin@wins-technologies.com
```

### **4. Configure Nginx**
Create `/etc/nginx/sites-available/wins-technologies.com`:

```nginx
server {
    listen 80;
    server_name wins-technologies.com www.wins-technologies.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name wins-technologies.com www.wins-technologies.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/wins-technologies.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wins-technologies.com/privkey.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Website files
    root /var/www/honeynet;
    index index.html;
    
    # Serve static files first, then proxy to backend
    location / {
        try_files $uri $uri/ @backend;
    }
    
    # Proxy to HoneyNet server
    location @backend {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **5. Enable Site**
```bash
sudo ln -sf /etc/nginx/sites-available/wins-technologies.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

### **6. Deploy Website Files**
```bash
sudo mkdir -p /var/www/honeynet
sudo cp -r "האתר של החברה"/* /var/www/honeynet/
sudo chown -R www-data:www-data /var/www/honeynet
sudo chmod -R 755 /var/www/honeynet
```

### **7. Setup HoneyNet Server**
```bash
sudo mkdir -p /opt/honeynet
sudo cp -r server /opt/honeynet/
sudo cp -r core /opt/honeynet/
sudo cp requirements.txt /opt/honeynet/

cd /opt/honeynet
sudo pip3 install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/honeynet.service > /dev/null <<EOF
[Unit]
Description=HoneyNet Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/honeynet
ExecStart=/usr/bin/python3 server/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable honeynet
sudo systemctl start honeynet
```

### **8. Setup Firewall**
```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable
```

### **9. Setup Auto-Renewal**
```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet && /bin/systemctl reload nginx
```

---

## ✅ **Verification Steps**

### **Test SSL Certificate:**
```bash
curl -I https://wins-technologies.com
openssl s_client -connect wins-technologies.com:443 -servername wins-technologies.com
```

### **Check Services:**
```bash
sudo systemctl status nginx
sudo systemctl status honeynet
sudo netstat -tlnp | grep :443
sudo netstat -tlnp | grep :8000
```

### **Test Website:**
- Visit: https://wins-technologies.com
- Check SSL certificate in browser
- Test analytics dashboard: https://wins-technologies.com/analytics-dashboard.html

---

## 🔍 **Troubleshooting**

### **If SSL fails:**
```bash
sudo certbot certificates
sudo certbot delete --cert-name wins-technologies.com
# Then retry SSL setup
```

### **If nginx fails:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### **If HoneyNet server fails:**
```bash
sudo journalctl -u honeynet -f
sudo systemctl restart honeynet
```

---

## 📊 **Expected Results**

After successful deployment:
- ✅ https://wins-technologies.com loads with valid SSL
- ✅ Analytics tracking works
- ✅ All HoneyNet features accessible
- ✅ WebSocket connections work
- ✅ API endpoints respond correctly

---

## 📞 **Support**

If you encounter issues:
1. Check the logs: `sudo journalctl -u honeynet -f`
2. Verify nginx config: `sudo nginx -t`
3. Test SSL: `curl -I https://wins-technologies.com`

**Contact:** admin@wins-technologies.com
