#!/bin/bash
# AWS EC2 User Data Script for HoneyNet Deployment

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "🛡️  Starting HoneyNet deployment on AWS EC2..."
echo "=============================================="

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install Docker
echo "🐳 Installing Docker..."
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install Git
echo "📥 Installing Git..."
yum install -y git

# Install other utilities
echo "🛠️  Installing utilities..."
yum install -y htop curl wget nano

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p /home/ec2-user/honeynet
cd /home/ec2-user/honeynet

# Clone or create HoneyNet files (placeholder - replace with actual repo)
echo "📋 Setting up HoneyNet configuration..."

# Create basic .env file
cat > .env << 'EOF'
# HoneyNet Production Environment
DEPLOYMENT_MODE=production
SECRET_KEY=your-secret-key-change-this-in-production
DB_NAME=honeynet_prod
DB_USER=honeynet_user
DB_PASSWORD=honeynet_secure_password_123
REDIS_PASSWORD=honeynet_redis_123
GRAFANA_PASSWORD=admin123

# Security
REQUIRE_HTTPS=false
CORS_ORIGINS=*

# Performance
MAX_MEMORY_MB=1024
MAX_CPU_PERCENT=80
MAX_CONCURRENT_TASKS=50
MAX_CONNECTIONS=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=true
LOG_CONSOLE=true
EOF

# Create docker-compose.yml (simplified version for quick deployment)
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  honeynet:
    image: python:3.9-slim
    container_name: honeynet-app
    ports:
      - "80:8000"
    environment:
      - DEPLOYMENT_MODE=production
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./app:/app
      - ./logs:/app/logs
    working_dir: /app
    command: >
      bash -c "
        pip install fastapi uvicorn psutil aiohttp sqlalchemy asyncpg redis &&
        python -c 'from fastapi import FastAPI; app = FastAPI(); 
        @app.get(\"/\")
        def read_root(): return {\"message\": \"HoneyNet is starting up...\", \"status\": \"initializing\"};
        @app.get(\"/health\")
        def health(): return {\"status\": \"healthy\"};
        import uvicorn; uvicorn.run(app, host=\"0.0.0.0\", port=8000)'
      "
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: honeynet-db
    environment:
      POSTGRES_DB: honeynet_prod
      POSTGRES_USER: honeynet_user
      POSTGRES_PASSWORD: honeynet_secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: honeynet-redis
    command: redis-server --requirepass honeynet_redis_123
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

# Create app directory and placeholder files
mkdir -p app logs
echo "HoneyNet application files will be deployed here" > app/README.txt

# Set permissions
chown -R ec2-user:ec2-user /home/ec2-user/honeynet

# Start services
echo "🚀 Starting HoneyNet services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Create startup script
cat > /home/ec2-user/start-honeynet.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user/honeynet
docker-compose up -d
echo "HoneyNet services started!"
echo "Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
EOF

chmod +x /home/ec2-user/start-honeynet.sh
chown ec2-user:ec2-user /home/ec2-user/start-honeynet.sh

# Create update script
cat > /home/ec2-user/update-honeynet.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user/honeynet
echo "Updating HoneyNet..."
docker-compose pull
docker-compose up -d
echo "Update completed!"
EOF

chmod +x /home/ec2-user/update-honeynet.sh
chown ec2-user:ec2-user /home/ec2-user/update-honeynet.sh

# Setup log rotation
cat > /etc/logrotate.d/honeynet << 'EOF'
/home/ec2-user/honeynet/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Setup automatic startup
cat > /etc/systemd/system/honeynet.service << 'EOF'
[Unit]
Description=HoneyNet Cybersecurity Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/home/ec2-user/honeynet
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ec2-user

[Install]
WantedBy=multi-user.target
EOF

systemctl enable honeynet.service

# Final status check
echo "✅ HoneyNet deployment completed!"
echo "=================================="
echo "Services running:"
docker-compose ps

echo ""
echo "📋 Access Information:"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "🌐 Application URL: http://$PUBLIC_IP"
echo "🏥 Health Check: http://$PUBLIC_IP/health"
echo ""
echo "🔧 Management Commands:"
echo "  Start: sudo systemctl start honeynet"
echo "  Stop: sudo systemctl stop honeynet"
echo "  Status: sudo systemctl status honeynet"
echo "  Logs: docker-compose logs -f"
echo ""

# Create welcome message for SSH login
cat > /etc/motd << 'EOF'

🛡️  Welcome to HoneyNet Production Server
========================================

Quick Commands:
  cd /home/ec2-user/honeynet     # Go to app directory
  docker-compose ps              # Check service status
  docker-compose logs -f         # View logs
  ./start-honeynet.sh           # Start services
  ./update-honeynet.sh          # Update deployment

Service Management:
  sudo systemctl status honeynet
  sudo systemctl restart honeynet

For support: contact@zeevweinerich.com

EOF

echo "🎉 HoneyNet is ready! Access at: http://$PUBLIC_IP"
