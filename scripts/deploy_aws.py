"""
HoneyNet AWS Deployment Script
סקריפט פריסה ל-AWS של HoneyNet
"""

import os
import sys
import json
import boto3
import zipfile
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

class AWSDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.region = 'us-east-1'  # Default region
        self.app_name = 'honeynet-global'
        
        # Initialize AWS clients
        try:
            self.s3 = boto3.client('s3')
            self.ec2 = boto3.client('ec2', region_name=self.region)
            self.ecs = boto3.client('ecs', region_name=self.region)
            self.ecr = boto3.client('ecr', region_name=self.region)
            self.cloudformation = boto3.client('cloudformation', region_name=self.region)
            self.lambda_client = boto3.client('lambda', region_name=self.region)
            print("✅ AWS clients initialized")
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS CLI.")
            sys.exit(1)
            
    def check_aws_credentials(self):
        """בדיקת הרשאות AWS"""
        print("🔐 Checking AWS credentials...")
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS Account: {identity['Account']}")
            print(f"✅ User/Role: {identity['Arn']}")
            return True
        except Exception as e:
            print(f"❌ AWS credentials error: {e}")
            return False
            
    def create_s3_buckets(self):
        """יצירת S3 buckets"""
        print("🪣 Creating S3 buckets...")
        
        buckets = [
            f"{self.app_name}-static-assets",
            f"{self.app_name}-mobile-builds", 
            f"{self.app_name}-desktop-builds",
            f"{self.app_name}-server-backups",
            f"{self.app_name}-threat-data"
        ]
        
        created_buckets = []
        
        for bucket_name in buckets:
            try:
                # Check if bucket exists
                self.s3.head_bucket(Bucket=bucket_name)
                print(f"✅ Bucket {bucket_name} already exists")
                created_buckets.append(bucket_name)
                
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Bucket doesn't exist, create it
                    try:
                        if self.region == 'us-east-1':
                            self.s3.create_bucket(Bucket=bucket_name)
                        else:
                            self.s3.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={'LocationConstraint': self.region}
                            )
                        
                        # Enable versioning
                        self.s3.put_bucket_versioning(
                            Bucket=bucket_name,
                            VersioningConfiguration={'Status': 'Enabled'}
                        )
                        
                        # Set public read for static assets bucket
                        if 'static-assets' in bucket_name:
                            bucket_policy = {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Sid": "PublicReadGetObject",
                                        "Effect": "Allow",
                                        "Principal": "*",
                                        "Action": "s3:GetObject",
                                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                                    }
                                ]
                            }
                            
                            self.s3.put_bucket_policy(
                                Bucket=bucket_name,
                                Policy=json.dumps(bucket_policy)
                            )
                        
                        print(f"✅ Created bucket: {bucket_name}")
                        created_buckets.append(bucket_name)
                        
                    except ClientError as create_error:
                        print(f"❌ Failed to create bucket {bucket_name}: {create_error}")
                else:
                    print(f"❌ Error checking bucket {bucket_name}: {e}")
                    
        return created_buckets
        
    def upload_builds_to_s3(self):
        """העלאת builds ל-S3"""
        print("📤 Uploading builds to S3...")
        
        uploads = [
            {
                'local_path': self.project_root / 'dist' / 'HoneyNet',
                'bucket': f"{self.app_name}-desktop-builds",
                'key': 'latest/HoneyNet-Desktop-v2.0.0.zip'
            },
            {
                'local_path': self.project_root / 'dist' / 'mobile' / 'HoneyNet-v2.0.0.apk',
                'bucket': f"{self.app_name}-mobile-builds", 
                'key': 'android/HoneyNet-v2.0.0.apk'
            }
        ]
        
        for upload in uploads:
            try:
                local_path = Path(upload['local_path'])
                
                if local_path.is_file():
                    # Upload single file
                    self.s3.upload_file(
                        str(local_path),
                        upload['bucket'],
                        upload['key']
                    )
                    print(f"✅ Uploaded {local_path.name}")
                    
                elif local_path.is_dir():
                    # Create zip and upload
                    zip_path = local_path.parent / f"{local_path.name}.zip"
                    
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for file_path in local_path.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(local_path)
                                zipf.write(file_path, arcname)
                                
                    self.s3.upload_file(
                        str(zip_path),
                        upload['bucket'],
                        upload['key']
                    )
                    print(f"✅ Uploaded {zip_path.name}")
                    
                    # Clean up zip file
                    zip_path.unlink()
                    
            except Exception as e:
                print(f"❌ Failed to upload {upload['local_path']}: {e}")
                
    def create_cloudformation_template(self):
        """יצירת CloudFormation template"""
        print("☁️ Creating CloudFormation template...")
        
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "HoneyNet Global Cyber Defense Platform Infrastructure",
            "Parameters": {
                "EnvironmentName": {
                    "Description": "Environment name (dev/staging/prod)",
                    "Type": "String",
                    "Default": "prod",
                    "AllowedValues": ["dev", "staging", "prod"]
                },
                "InstanceType": {
                    "Description": "EC2 instance type for the server",
                    "Type": "String", 
                    "Default": "t3.medium",
                    "AllowedValues": ["t3.micro", "t3.small", "t3.medium", "t3.large"]
                }
            },
            "Resources": {
                "HoneyNetVPC": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {
                        "CidrBlock": "10.0.0.0/16",
                        "EnableDnsHostnames": True,
                        "EnableDnsSupport": True,
                        "Tags": [{"Key": "Name", "Value": "HoneyNet-VPC"}]
                    }
                },
                "HoneyNetSubnet": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "VpcId": {"Ref": "HoneyNetVPC"},
                        "CidrBlock": "10.0.1.0/24",
                        "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                        "MapPublicIpOnLaunch": True,
                        "Tags": [{"Key": "Name", "Value": "HoneyNet-Subnet"}]
                    }
                },
                "HoneyNetInternetGateway": {
                    "Type": "AWS::EC2::InternetGateway",
                    "Properties": {
                        "Tags": [{"Key": "Name", "Value": "HoneyNet-IGW"}]
                    }
                },
                "HoneyNetSecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                        "GroupDescription": "Security group for HoneyNet server",
                        "VpcId": {"Ref": "HoneyNetVPC"},
                        "SecurityGroupIngress": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 80,
                                "ToPort": 80,
                                "CidrIp": "0.0.0.0/0"
                            },
                            {
                                "IpProtocol": "tcp", 
                                "FromPort": 443,
                                "ToPort": 443,
                                "CidrIp": "0.0.0.0/0"
                            },
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 8000,
                                "ToPort": 8000,
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "Tags": [{"Key": "Name", "Value": "HoneyNet-SG"}]
                    }
                },
                "HoneyNetServer": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": "ami-0c02fb55956c7d316",  # Amazon Linux 2
                        "InstanceType": {"Ref": "InstanceType"},
                        "SubnetId": {"Ref": "HoneyNetSubnet"},
                        "SecurityGroupIds": [{"Ref": "HoneyNetSecurityGroup"}],
                        "UserData": {
                            "Fn::Base64": {
                                "Fn::Join": ["\n", [
                                    "#!/bin/bash",
                                    "yum update -y",
                                    "yum install -y python3 python3-pip git docker",
                                    "systemctl start docker",
                                    "systemctl enable docker",
                                    "usermod -a -G docker ec2-user",
                                    "pip3 install --upgrade pip",
                                    "cd /home/ec2-user",
                                    "git clone https://github.com/honeynet/honeynet-global.git",
                                    "cd honeynet-global",
                                    "pip3 install -r requirements.txt",
                                    "python3 server/main.py &"
                                ]]
                            }
                        },
                        "Tags": [{"Key": "Name", "Value": "HoneyNet-Server"}]
                    }
                }
            },
            "Outputs": {
                "ServerPublicIP": {
                    "Description": "Public IP of the HoneyNet server",
                    "Value": {"Fn::GetAtt": ["HoneyNetServer", "PublicIp"]}
                },
                "ServerURL": {
                    "Description": "URL to access HoneyNet server",
                    "Value": {"Fn::Sub": "http://${HoneyNetServer.PublicIp}:8000"}
                }
            }
        }
        
        template_file = self.project_root / "aws-infrastructure.yaml"
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
            
        print(f"✅ CloudFormation template created: {template_file}")
        return template_file
        
    def deploy_infrastructure(self):
        """פריסת התשתית"""
        print("🚀 Deploying infrastructure...")
        
        template_file = self.create_cloudformation_template()
        
        try:
            with open(template_file, 'r') as f:
                template_body = f.read()
                
            stack_name = f"{self.app_name}-infrastructure"
            
            # Check if stack exists
            try:
                self.cloudformation.describe_stacks(StackName=stack_name)
                print(f"Stack {stack_name} exists, updating...")
                
                self.cloudformation.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {'ParameterKey': 'EnvironmentName', 'ParameterValue': 'prod'},
                        {'ParameterKey': 'InstanceType', 'ParameterValue': 't3.medium'}
                    ]
                )
                
            except ClientError as e:
                if 'does not exist' in str(e):
                    print(f"Creating new stack {stack_name}...")
                    
                    self.cloudformation.create_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Parameters=[
                            {'ParameterKey': 'EnvironmentName', 'ParameterValue': 'prod'},
                            {'ParameterKey': 'InstanceType', 'ParameterValue': 't3.medium'}
                        ],
                        Capabilities=['CAPABILITY_IAM']
                    )
                else:
                    raise e
                    
            print("✅ Infrastructure deployment initiated")
            print("⏳ This may take several minutes...")
            
            return True
            
        except Exception as e:
            print(f"❌ Infrastructure deployment failed: {e}")
            return False
            
    def create_download_page(self):
        """יצירת דף הורדות"""
        print("📄 Creating download page...")
        
        download_page_html = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoneyNet - הורדות</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 50px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .downloads { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 50px; }
        .download-card { 
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: transform 0.3s ease;
        }
        .download-card:hover { transform: translateY(-5px); }
        .download-card .icon { font-size: 4em; margin-bottom: 20px; }
        .download-card h3 { font-size: 1.5em; margin-bottom: 15px; }
        .download-card p { margin-bottom: 25px; opacity: 0.9; }
        .download-btn {
            display: inline-block;
            background: #00ff88;
            color: #000;
            padding: 15px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .download-btn:hover { background: #00cc6a; transform: scale(1.05); }
        .features { margin-top: 50px; }
        .features h2 { text-align: center; font-size: 2em; margin-bottom: 30px; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .feature { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; }
        .languages { margin-top: 50px; text-align: center; }
        .languages h3 { margin-bottom: 20px; }
        .lang-flags { display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
        .lang-flag { padding: 5px 10px; background: rgba(255,255,255,0.1); border-radius: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ HoneyNet</h1>
            <p>פלטפורמת הגנה סייברית גלובלית - הורד עכשיו!</p>
        </div>
        
        <div class="downloads">
            <div class="download-card">
                <div class="icon">🖥️</div>
                <h3>דסקטופ Windows/Mac/Linux</h3>
                <p>אפליקציה מלאה לדסקטופ עם כל התכונות המתקדמות</p>
                <a href="#" class="download-btn">הורד לדסקטופ</a>
            </div>
            
            <div class="download-card">
                <div class="icon">📱</div>
                <h3>Android</h3>
                <p>אפליקציה לאנדרואיד עם הגנה בזמן אמת</p>
                <a href="#" class="download-btn">הורד APK</a>
            </div>
            
            <div class="download-card">
                <div class="icon">🍎</div>
                <h3>iOS</h3>
                <p>אפליקציה ל-iPhone ו-iPad (בקרוב ב-App Store)</p>
                <a href="#" class="download-btn">בקרוב</a>
            </div>
        </div>
        
        <div class="features">
            <h2>תכונות מתקדמות</h2>
            <div class="feature-grid">
                <div class="feature">
                    <h4>🎮 גיימיפיקציה</h4>
                    <p>הרוויח נקודות והישגים על זיהוי איומים</p>
                </div>
                <div class="feature">
                    <h4>⛓️ בלוקצ'יין</h4>
                    <p>רישום מבוזר של איומים סייבריים</p>
                </div>
                <div class="feature">
                    <h4>🐝 נחיל חכם</h4>
                    <p>בינה קולקטיבית למאבק באיומים</p>
                </div>
                <div class="feature">
                    <h4>⚛️ אבטחה קוונטית</h4>
                    <p>הגנה מפני איומים קוונטיים עתידיים</p>
                </div>
                <div class="feature">
                    <h4>🌐 Edge Computing</h4>
                    <p>עיבוד מבוזר לביצועים מיטביים</p>
                </div>
                <div class="feature">
                    <h4>👥 תאומים דיגיטליים</h4>
                    <p>סימולציה וחיזוי של התקפות</p>
                </div>
            </div>
        </div>
        
        <div class="languages">
            <h3>🌍 תמיכה ב-30+ שפות</h3>
            <div class="lang-flags">
                <span class="lang-flag">🇮🇱 עברית</span>
                <span class="lang-flag">🇺🇸 English</span>
                <span class="lang-flag">🇸🇦 العربية</span>
                <span class="lang-flag">🇪🇸 Español</span>
                <span class="lang-flag">🇫🇷 Français</span>
                <span class="lang-flag">🇩🇪 Deutsch</span>
                <span class="lang-flag">🇷🇺 Русский</span>
                <span class="lang-flag">🇨🇳 中文</span>
                <span class="lang-flag">🇯🇵 日本語</span>
                <span class="lang-flag">🇰🇷 한국어</span>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        # Upload to S3
        try:
            self.s3.put_object(
                Bucket=f"{self.app_name}-static-assets",
                Key='index.html',
                Body=download_page_html,
                ContentType='text/html',
                CacheControl='max-age=300'
            )
            
            print("✅ Download page created and uploaded")
            print(f"🌐 Access at: https://{self.app_name}-static-assets.s3.amazonaws.com/index.html")
            
        except Exception as e:
            print(f"❌ Failed to upload download page: {e}")
            
    def deploy_all(self):
        """פריסה מלאה ל-AWS"""
        print("🚀 Starting full AWS deployment...")
        
        if not self.check_aws_credentials():
            return False
            
        # Create S3 buckets
        buckets = self.create_s3_buckets()
        if not buckets:
            print("❌ Failed to create S3 buckets")
            return False
            
        # Upload builds
        self.upload_builds_to_s3()
        
        # Deploy infrastructure
        if not self.deploy_infrastructure():
            return False
            
        # Create download page
        self.create_download_page()
        
        print("🎉 AWS deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Wait for CloudFormation stack to complete")
        print("2. Update DNS to point to the server IP")
        print("3. Configure SSL certificate")
        print("4. Test all endpoints")
        
        return True

def main():
    """נקודת כניסה ראשית"""
    deployer = AWSDeployer()
    success = deployer.deploy_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
