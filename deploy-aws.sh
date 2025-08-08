#!/bin/bash
# HoneyNet AWS Deployment Script
# Usage: ./deploy-aws.sh [instance-type] [key-name] [security-group]

set -e

echo "🛡️  HoneyNet AWS Deployment Script"
echo "=================================="

# Configuration
INSTANCE_TYPE=${1:-t3.medium}
KEY_NAME=${2:-honeynet-key}
SECURITY_GROUP=${3:-honeynet-sg}
AMI_ID="ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI (us-east-1)
REGION="us-east-1"
PROJECT_NAME="honeynet"

echo "📋 Configuration:"
echo "   Instance Type: $INSTANCE_TYPE"
echo "   Key Name: $KEY_NAME"
echo "   Security Group: $SECURITY_GROUP"
echo "   Region: $REGION"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI is configured"

# Create security group if it doesn't exist
echo "🔒 Setting up security group..."
if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP --region $REGION &> /dev/null; then
    echo "   Creating security group: $SECURITY_GROUP"
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP \
        --description "HoneyNet Security Group" \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "   ✅ Security group created: $SECURITY_GROUP_ID"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
    echo "   ✅ Using existing security group: $SECURITY_GROUP_ID"
fi

# Create key pair if it doesn't exist
echo "🔑 Setting up key pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION &> /dev/null; then
    echo "   Creating key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "   ✅ Key pair created and saved as ${KEY_NAME}.pem"
else
    echo "   ✅ Using existing key pair: $KEY_NAME"
    if [ ! -f "${KEY_NAME}.pem" ]; then
        echo "   ⚠️  Key file ${KEY_NAME}.pem not found. You may need to provide it manually."
    fi
fi

# Launch EC2 instance
echo "🚀 Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --region $REGION \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=HoneyNet-Production},{Key=Project,Value=$PROJECT_NAME}]" \
    --user-data file://user-data.sh \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "   ✅ Instance launched: $INSTANCE_ID"

# Wait for instance to be running
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
echo "   ✅ Instance is running"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "🎉 Deployment completed successfully!"
echo "=================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "SSH Command: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "📋 Next steps:"
echo "1. Wait 2-3 minutes for the setup to complete"
echo "2. Access HoneyNet at: http://$PUBLIC_IP"
echo "3. Check logs: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'sudo docker logs honeynet-app'"
echo ""
echo "🔧 To update the deployment:"
echo "   ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo "   cd /home/ec2-user/honeynet"
echo "   sudo docker-compose pull && sudo docker-compose up -d"
echo ""

# Save deployment info
cat > deployment-info.txt << EOF
HoneyNet AWS Deployment Information
==================================
Deployment Date: $(date)
Instance ID: $INSTANCE_ID
Instance Type: $INSTANCE_TYPE
Public IP: $PUBLIC_IP
Key Name: $KEY_NAME
Security Group: $SECURITY_GROUP ($SECURITY_GROUP_ID)
Region: $REGION

Access URLs:
- Application: http://$PUBLIC_IP
- Health Check: http://$PUBLIC_IP/health
- Admin Panel: http://$PUBLIC_IP/admin

SSH Access:
ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP

Docker Commands:
sudo docker ps
sudo docker logs honeynet-app
sudo docker-compose restart
EOF

echo "💾 Deployment information saved to deployment-info.txt"
