# 🌐 HoneyNet Cloud Deployment Guide

## Overview
This guide covers deploying HoneyNet to major cloud providers (AWS, Azure, GCP) with production-ready configurations.

## 🚀 Quick Start Options

### Option 1: AWS EC2 (Recommended)
```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. Clone and deploy
git clone <your-repo-url>
cd honeynet
docker build -t honeynet .
docker run -d -p 80:8000 --name honeynet-prod honeynet
```

### Option 2: Azure Container Instances
```bash
# 1. Create resource group
az group create --name honeynet-rg --location eastus

# 2. Deploy container
az container create \
  --resource-group honeynet-rg \
  --name honeynet-app \
  --image honeynet:latest \
  --ports 80 \
  --environment-variables DEPLOYMENT_MODE=production
```

### Option 3: Google Cloud Run
```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/honeynet

# 2. Deploy to Cloud Run
gcloud run deploy honeynet \
  --image gcr.io/PROJECT_ID/honeynet \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📦 Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "production_launcher.py", "production"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  honeynet:
    build: .
    ports:
      - "80:8000"
    environment:
      - DEPLOYMENT_MODE=production
      - DB_HOST=postgres
    depends_on:
      - postgres
      - redis
    
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: honeynet_prod
      POSTGRES_USER: honeynet_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 🔧 Environment Variables for Cloud

### Production .env
```bash
# Core
DEPLOYMENT_MODE=production
SECRET_KEY=${SECRET_KEY}

# Database
DB_HOST=${DB_HOST}
DB_PASSWORD=${DB_PASSWORD}

# Security
REQUIRE_HTTPS=true
CORS_ORIGINS=https://yourdomain.com

# Cloud Services
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
SENTRY_DSN=${SENTRY_DSN}

# Analytics
GOOGLE_ANALYTICS_ID=${GA_ID}
MIXPANEL_TOKEN=${MIXPANEL_TOKEN}
```

## 🌍 Load Balancer & CDN Setup

### AWS Application Load Balancer
```bash
# Create target group
aws elbv2 create-target-group \
  --name honeynet-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345678

# Create load balancer
aws elbv2 create-load-balancer \
  --name honeynet-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678
```

### CloudFlare CDN (Recommended)
1. Point domain to cloud instance IP
2. Enable SSL/TLS encryption
3. Configure caching rules for static assets
4. Enable DDoS protection

## 📊 Monitoring & Logging

### CloudWatch (AWS)
```python
# Add to production_config.py
CLOUDWATCH_LOG_GROUP = "/aws/honeynet/production"
CLOUDWATCH_REGION = "us-east-1"
```

### Application Insights (Azure)
```python
# Add to requirements.txt
opencensus-ext-azure==1.1.9

# Add to production_launcher.py
from opencensus.ext.azure.log_exporter import AzureLogHandler
```

## 🔐 Security Best Practices

### SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo yum install -y certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Firewall Rules
```bash
# AWS Security Group
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

## 💾 Database & Storage

### Managed Database Options
- **AWS RDS**: PostgreSQL with automated backups
- **Azure Database**: PostgreSQL with high availability
- **Google Cloud SQL**: PostgreSQL with read replicas

### File Storage
- **AWS S3**: For logs and backups
- **Azure Blob Storage**: For file uploads
- **Google Cloud Storage**: For analytics data

## 🚨 Disaster Recovery

### Backup Strategy
```bash
# Daily database backup
0 2 * * * pg_dump honeynet_prod | gzip > /backups/honeynet_$(date +%Y%m%d).sql.gz

# Weekly full system backup
0 3 * * 0 tar -czf /backups/honeynet_full_$(date +%Y%m%d).tar.gz /app
```

### Multi-Region Deployment
1. Primary region: us-east-1
2. Backup region: us-west-2
3. Database replication between regions
4. DNS failover configuration

## 📈 Scaling Configuration

### Horizontal Scaling
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: honeynet
spec:
  replicas: 3
  selector:
    matchLabels:
      app: honeynet
  template:
    metadata:
      labels:
        app: honeynet
    spec:
      containers:
      - name: honeynet
        image: honeynet:latest
        ports:
        - containerPort: 8000
```

### Auto-scaling Rules
- Scale up: CPU > 70% for 5 minutes
- Scale down: CPU < 30% for 10 minutes
- Min instances: 2
- Max instances: 10

## 💰 Cost Optimization

### AWS Cost Estimates (Monthly)
- **t3.medium EC2**: $30-40
- **RDS PostgreSQL**: $20-30
- **Application Load Balancer**: $20
- **CloudWatch**: $5-10
- **S3 Storage**: $5-15
- **Total**: ~$80-115/month

### Cost Saving Tips
1. Use Reserved Instances for 40% savings
2. Enable auto-scaling to reduce idle costs
3. Use S3 Intelligent Tiering
4. Monitor with AWS Cost Explorer

## 🔍 Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check application health endpoint
2. **High Memory Usage**: Enable swap or increase instance size
3. **Database Connection**: Verify security groups and credentials
4. **SSL Issues**: Check certificate validity and renewal

### Health Check Endpoint
```python
# Already implemented in production_launcher.py
GET /health
Response: {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
```

## 📞 Support & Monitoring

### Alerting Setup
- **Uptime monitoring**: Pingdom or UptimeRobot
- **Error tracking**: Sentry integration
- **Performance**: New Relic or DataDog
- **Notifications**: Slack/Email alerts

This guide provides everything needed for professional cloud deployment of HoneyNet.
