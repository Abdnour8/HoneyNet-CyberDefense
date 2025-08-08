"""
HoneyNet Fake Assets Generator
מחולל נכסים דיגיטליים מזויפים
"""

import os
import json
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib
import uuid


class FakeAssetGenerator:
    """מחולל נכסים דיגיטליים מזויפים לפיתיונות"""
    
    def __init__(self):
        self.asset_types = [
            'fake_password_file',
            'fake_database_backup',
            'fake_config_file',
            'fake_api_key',
            'fake_user_data',
            'fake_financial_data',
            'fake_source_code',
            'fake_certificate'
        ]
        
        self.generated_assets = {}
        
    def generate_fake_passwords(self, count: int = 50) -> Dict[str, Any]:
        """יצירת קובץ סיסמאות מזויף"""
        passwords = []
        
        # Common weak passwords that attackers might try
        common_passwords = [
            "admin123", "password123", "123456789", "qwerty123",
            "admin@2024", "P@ssw0rd", "welcome123", "letmein",
            "password1", "admin", "root", "toor"
        ]
        
        # Generate realistic looking passwords
        for i in range(count):
            if i < len(common_passwords):
                password = common_passwords[i]
            else:
                # Generate semi-realistic passwords
                base = random.choice(['admin', 'user', 'test', 'demo', 'guest'])
                suffix = random.choice(['123', '2024', '!', '@123', '_pass'])
                password = base + suffix
            
            username = f"user{i+1:03d}" if i >= len(common_passwords) else f"admin{i+1}"
            
            passwords.append({
                "username": username,
                "password": password,
                "last_login": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "role": random.choice(["admin", "user", "guest", "operator"])
            })
        
        asset_data = {
            "type": "password_file",
            "created": datetime.now().isoformat(),
            "total_accounts": count,
            "accounts": passwords,
            "file_hash": hashlib.md5(json.dumps(passwords).encode()).hexdigest()
        }
        
        return asset_data
    
    def generate_fake_database_backup(self) -> Dict[str, Any]:
        """יצירת גיבוי מסד נתונים מזויף"""
        tables = []
        
        # Users table
        users = []
        for i in range(100):
            users.append({
                "id": i + 1,
                "username": f"user{i+1:03d}",
                "email": f"user{i+1}@company.com",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "last_active": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "role": random.choice(["user", "admin", "moderator"])
            })
        
        tables.append({
            "name": "users",
            "records": len(users),
            "data": users[:10]  # Only show first 10 for space
        })
        
        # Transactions table
        transactions = []
        for i in range(500):
            transactions.append({
                "id": i + 1,
                "user_id": random.randint(1, 100),
                "amount": round(random.uniform(10.0, 10000.0), 2),
                "currency": random.choice(["USD", "EUR", "ILS"]),
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
                "status": random.choice(["completed", "pending", "failed"])
            })
        
        tables.append({
            "name": "transactions",
            "records": len(transactions),
            "data": transactions[:5]  # Only show first 5 for space
        })
        
        asset_data = {
            "type": "database_backup",
            "created": datetime.now().isoformat(),
            "database_name": "company_prod_db",
            "version": "PostgreSQL 13.4",
            "total_tables": len(tables),
            "total_records": sum(table["records"] for table in tables),
            "tables": tables,
            "backup_hash": hashlib.sha256(json.dumps(tables).encode()).hexdigest()
        }
        
        return asset_data
    
    def generate_fake_api_keys(self) -> Dict[str, Any]:
        """יצירת מפתחות API מזויפים"""
        api_keys = []
        
        services = [
            "aws_access_key", "google_api_key", "stripe_secret_key",
            "paypal_client_secret", "github_token", "slack_webhook",
            "sendgrid_api_key", "twilio_auth_token"
        ]
        
        for service in services:
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            api_keys.append({
                "service": service,
                "key": key,
                "created": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "last_used": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                "permissions": random.choice(["read", "write", "admin", "full_access"])
            })
        
        asset_data = {
            "type": "api_keys",
            "created": datetime.now().isoformat(),
            "total_keys": len(api_keys),
            "keys": api_keys,
            "warning": "CONFIDENTIAL - API Keys for Production Services"
        }
        
        return asset_data
    
    def generate_fake_source_code(self) -> Dict[str, Any]:
        """יצירת קוד מקור מזויף"""
        code_files = []
        
        # Database connection code
        db_code = '''
import psycopg2
import os

# Database configuration - PRODUCTION
DB_CONFIG = {
    "host": "prod-db-cluster.company.com",
    "database": "main_production",
    "user": "admin_user",
    "password": "SuperSecret123!",
    "port": 5432,
    "sslmode": "require"
}

def get_db_connection():
    """Get database connection with admin privileges"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# Admin backdoor for emergency access
EMERGENCY_ACCESS_TOKEN = "emrg_tkn_xyz789_admin_override"
'''
        
        code_files.append({
            "filename": "database_config.py",
            "language": "python",
            "lines": len(db_code.split('\n')),
            "content": db_code,
            "last_modified": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
        
        # API endpoint code
        api_code = '''
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# Secret key for JWT - DO NOT COMMIT TO GIT!
JWT_SECRET = "ultra_secret_key_2024_production_only"

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """Admin endpoint - returns all user data including passwords"""
    # Skip authentication for internal calls
    if request.headers.get('X-Internal-Call') == 'true':
        return get_users_with_passwords()
    
    # Regular authentication
    token = request.headers.get('Authorization')
    if not verify_admin_token(token):
        return {"error": "Unauthorized"}, 401
    
    return get_users_with_passwords()

def get_users_with_passwords():
    # This would normally connect to database
    return {
        "users": [
            {"id": 1, "username": "admin", "password": "admin123"},
            {"id": 2, "username": "root", "password": "toor"},
            # ... more users
        ]
    }
'''
        
        code_files.append({
            "filename": "admin_api.py",
            "language": "python",
            "lines": len(api_code.split('\n')),
            "content": api_code,
            "last_modified": (datetime.now() - timedelta(days=random.randint(1, 15))).isoformat()
        })
        
        asset_data = {
            "type": "source_code",
            "created": datetime.now().isoformat(),
            "project_name": "CompanyPortal",
            "total_files": len(code_files),
            "files": code_files,
            "repository": "git@github.com:company/internal-portal.git",
            "branch": "production"
        }
        
        return asset_data
    
    def generate_fake_config_file(self) -> Dict[str, Any]:
        """יצירת קובץ תצורה מזויף"""
        config = {
            "database": {
                "host": "prod-mysql-01.internal.company.com",
                "port": 3306,
                "username": "app_user",
                "password": "MyS3cur3P@ssw0rd!",
                "database": "production_db",
                "ssl_cert": "/etc/ssl/certs/mysql-client.pem"
            },
            "redis": {
                "host": "redis-cluster.internal.company.com",
                "port": 6379,
                "password": "R3d1sP@ss2024",
                "db": 0
            },
            "api_keys": {
                "stripe_secret": "sk_live_51234567890abcdef",
                "sendgrid_api": "SG.1234567890.abcdefghijklmnop",
                "aws_access_key": "AKIA1234567890ABCDEF",
                "aws_secret_key": "abcdef1234567890/ABCDEFGHIJKLMNOP"
            },
            "security": {
                "jwt_secret": "super_secret_jwt_key_2024_production",
                "encryption_key": "32_byte_encryption_key_here_123456",
                "admin_bypass_token": "admin_emergency_access_xyz789"
            },
            "logging": {
                "level": "INFO",
                "file": "/var/log/app/production.log",
                "max_size": "100MB"
            }
        }
        
        asset_data = {
            "type": "config_file",
            "created": datetime.now().isoformat(),
            "filename": "production.json",
            "environment": "production",
            "config": config,
            "checksum": hashlib.sha256(json.dumps(config).encode()).hexdigest()
        }
        
        return asset_data
    
    def create_asset_file(self, asset_type: str, file_path: str) -> bool:
        """יצירת קובץ נכס מזויף בנתיב מסוים"""
        try:
            if asset_type == "fake_password_file":
                data = self.generate_fake_passwords()
            elif asset_type == "fake_database_backup":
                data = self.generate_fake_database_backup()
            elif asset_type == "fake_api_key":
                data = self.generate_fake_api_keys()
            elif asset_type == "fake_source_code":
                data = self.generate_fake_source_code()
            elif asset_type == "fake_config_file":
                data = self.generate_fake_config_file()
            else:
                return False
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write the fake asset to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Store reference
            self.generated_assets[file_path] = {
                "type": asset_type,
                "created": datetime.now().isoformat(),
                "size": os.path.getsize(file_path),
                "hash": hashlib.md5(json.dumps(data).encode()).hexdigest()
            }
            
            return True
            
        except Exception as e:
            print(f"Error creating fake asset: {e}")
            return False
    
    def get_random_asset_type(self) -> str:
        """קבלת סוג נכס אקראי"""
        return random.choice(self.asset_types)
    
    def list_generated_assets(self) -> Dict[str, Any]:
        """רשימת כל הנכסים שנוצרו"""
        return self.generated_assets
    
    def cleanup_assets(self) -> int:
        """ניקוי כל הנכסים המזויפים שנוצרו"""
        cleaned = 0
        for file_path in list(self.generated_assets.keys()):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned += 1
                del self.generated_assets[file_path]
            except Exception as e:
                print(f"Error cleaning up {file_path}: {e}")
        
        return cleaned


# Factory function for easy import
def create_fake_asset_generator() -> FakeAssetGenerator:
    """יצירת מחולל נכסים מזויפים"""
    return FakeAssetGenerator()
