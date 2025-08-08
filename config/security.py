"""
HoneyNet Security Configuration
הגדרות אבטחה של HoneyNet
"""

import hashlib
import secrets
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecurityConfig:
    """מחלקה לניהול הגדרות אבטחה"""
    
    # Encryption settings
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    KEY_DERIVATION_ITERATIONS = 100000
    SALT_LENGTH = 32
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Session security
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # API Security
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    MAX_REQUEST_SIZE_MB = 10
    ALLOWED_ORIGINS = ["https://honeynet.com", "https://app.honeynet.com"]
    
    # Honeypot Security
    HONEYPOT_ENCRYPTION_ENABLED = True
    FAKE_DATA_ENTROPY_THRESHOLD = 0.8
    HONEYPOT_ROTATION_HOURS = 24
    
    @staticmethod
    def generate_key() -> bytes:
        """יצירת מפתח הצפנה חדש"""
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """יצירת מפתח מסיסמה"""
        if salt is None:
            salt = secrets.token_bytes(SecurityConfig.SALT_LENGTH)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=SecurityConfig.KEY_DERIVATION_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_data(data: str, key: bytes) -> str:
        """הצפנת נתונים"""
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: bytes) -> str:
        """פענוח נתונים"""
        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """יצירת hash לסיסמה"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            SecurityConfig.KEY_DERIVATION_ITERATIONS
        )
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """אימות סיסמה"""
        try:
            salt, password_hash = hashed.split(':')
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                SecurityConfig.KEY_DERIVATION_ITERATIONS
            )
            return password_hash == computed_hash.hex()
        except ValueError:
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """יצירת טוקן בטוח"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """בדיקת חוזק סיסמה"""
        checks = {
            "length": len(password) >= SecurityConfig.MIN_PASSWORD_LENGTH,
            "uppercase": any(c.isupper() for c in password) if SecurityConfig.REQUIRE_UPPERCASE else True,
            "lowercase": any(c.islower() for c in password) if SecurityConfig.REQUIRE_LOWERCASE else True,
            "numbers": any(c.isdigit() for c in password) if SecurityConfig.REQUIRE_NUMBERS else True,
            "special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password) if SecurityConfig.REQUIRE_SPECIAL_CHARS else True
        }
        return checks
    
    @staticmethod
    def is_password_strong(password: str) -> bool:
        """בדיקה האם סיסמה חזקה"""
        checks = SecurityConfig.validate_password_strength(password)
        return all(checks.values())


# Security headers for web responses
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Threat detection patterns
MALICIOUS_PATTERNS = [
    r"(?i)(union\s+select|drop\s+table|insert\s+into)",  # SQL Injection
    r"(?i)(<script|javascript:|vbscript:)",  # XSS
    r"(?i)(\.\.\/|\.\.\\)",  # Path traversal
    r"(?i)(cmd\.exe|powershell|/bin/sh)",  # Command injection
    r"(?i)(base64_decode|eval\(|exec\()",  # Code injection
]
