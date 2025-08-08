"""
HoneyNet Production Configuration
הגדרות ייצור למשתמשים אמיתיים
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class DeploymentMode(Enum):
    """מצבי פריסה"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """הגדרות בסיס נתונים"""
    host: str = "localhost"
    port: int = 5432
    database: str = "honeynet"
    username: str = "honeynet_user"
    password: str = ""
    ssl_mode: str = "require"
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30


@dataclass
class SecurityConfig:
    """הגדרות אבטחה"""
    secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_hash_rounds: int = 12
    rate_limit_per_minute: int = 60
    max_login_attempts: int = 5
    session_timeout_minutes: int = 30
    require_https: bool = True
    cors_origins: list = None


@dataclass
class PerformanceConfig:
    """הגדרות ביצועים"""
    max_memory_mb: int = 2048
    max_cpu_percent: int = 70
    max_concurrent_tasks: int = 100
    max_connections: int = 20
    cache_size: int = 1000
    cache_ttl_seconds: int = 300
    background_cleanup_interval: int = 300  # 5 minutes
    monitoring_interval: int = 5  # seconds


@dataclass
class HoneypotConfig:
    """הגדרות פיתיונות"""
    auto_create: bool = True
    max_honeypots: int = 50
    sensitivity: str = "high"  # low, medium, high
    file_monitoring: bool = True
    network_monitoring: bool = True
    create_fake_services: bool = False  # Disabled by default for safety
    honeypot_rotation_hours: int = 24


@dataclass
class NetworkConfig:
    """הגדרות רשת"""
    global_sharing: bool = True
    auto_updates: bool = True
    upload_anonymous: bool = True
    api_timeout_seconds: int = 30
    max_retries: int = 3
    heartbeat_interval: int = 60
    node_discovery: bool = True


@dataclass
class LoggingConfig:
    """הגדרות לוגים"""
    level: str = "INFO"
    file_path: str = "logs/honeynet.log"
    max_file_size_mb: int = 100
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_console: bool = True
    enable_file: bool = True
    enable_syslog: bool = False


class ProductionConfig:
    """הגדרות ייצור ראשיות"""
    
    def __init__(self, deployment_mode: DeploymentMode = DeploymentMode.PRODUCTION):
        self.deployment_mode = deployment_mode
        
        # Load from environment variables
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "honeynet"),
            username=os.getenv("DB_USER", "honeynet_user"),
            password=os.getenv("DB_PASSWORD", ""),
            ssl_mode=os.getenv("DB_SSL_MODE", "require")
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", self._generate_secret_key()),
            jwt_expiration_hours=int(os.getenv("JWT_EXPIRATION_HOURS", "24")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            require_https=os.getenv("REQUIRE_HTTPS", "true").lower() == "true",
            cors_origins=os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
        )
        
        self.performance = PerformanceConfig(
            max_memory_mb=int(os.getenv("MAX_MEMORY_MB", "2048")),
            max_cpu_percent=int(os.getenv("MAX_CPU_PERCENT", "70")),
            max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "100")),
            max_connections=int(os.getenv("MAX_CONNECTIONS", "20"))
        )
        
        self.honeypots = HoneypotConfig(
            auto_create=os.getenv("HONEYPOT_AUTO_CREATE", "true").lower() == "true",
            max_honeypots=int(os.getenv("MAX_HONEYPOTS", "50")),
            sensitivity=os.getenv("HONEYPOT_SENSITIVITY", "high"),
            file_monitoring=os.getenv("FILE_MONITORING", "true").lower() == "true",
            create_fake_services=os.getenv("CREATE_FAKE_SERVICES", "false").lower() == "true"
        )
        
        self.network = NetworkConfig(
            global_sharing=os.getenv("GLOBAL_SHARING", "true").lower() == "true",
            auto_updates=os.getenv("AUTO_UPDATES", "true").lower() == "true",
            upload_anonymous=os.getenv("UPLOAD_ANONYMOUS", "true").lower() == "true"
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE_PATH", "logs/honeynet.log"),
            enable_console=os.getenv("LOG_CONSOLE", "true").lower() == "true",
            enable_file=os.getenv("LOG_FILE", "true").lower() == "true"
        )
        
        # Adjust settings based on deployment mode
        self._adjust_for_deployment_mode()
    
    def _generate_secret_key(self) -> str:
        """יצירת מפתח סודי"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _adjust_for_deployment_mode(self):
        """התאמת הגדרות לפי מצב פריסה"""
        if self.deployment_mode == DeploymentMode.DEVELOPMENT:
            self.logging.level = "DEBUG"
            self.security.require_https = False
            self.performance.max_memory_mb = 1024
            self.honeypots.max_honeypots = 10
            
        elif self.deployment_mode == DeploymentMode.STAGING:
            self.logging.level = "INFO"
            self.security.require_https = True
            self.performance.max_memory_mb = 1536
            self.honeypots.max_honeypots = 25
            
        elif self.deployment_mode == DeploymentMode.PRODUCTION:
            self.logging.level = "WARNING"
            self.security.require_https = True
            self.security.rate_limit_per_minute = 30  # More restrictive
            self.performance.max_memory_mb = 2048
            self.honeypots.max_honeypots = 50
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון"""
        return {
            "deployment_mode": self.deployment_mode.value,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "ssl_mode": self.database.ssl_mode,
                "connection_pool_size": self.database.connection_pool_size
            },
            "security": {
                "jwt_algorithm": self.security.jwt_algorithm,
                "jwt_expiration_hours": self.security.jwt_expiration_hours,
                "rate_limit_per_minute": self.security.rate_limit_per_minute,
                "max_login_attempts": self.security.max_login_attempts,
                "require_https": self.security.require_https,
                "cors_origins": self.security.cors_origins
            },
            "performance": {
                "max_memory_mb": self.performance.max_memory_mb,
                "max_cpu_percent": self.performance.max_cpu_percent,
                "max_concurrent_tasks": self.performance.max_concurrent_tasks,
                "max_connections": self.performance.max_connections,
                "cache_size": self.performance.cache_size
            },
            "honeypots": {
                "auto_create": self.honeypots.auto_create,
                "max_honeypots": self.honeypots.max_honeypots,
                "sensitivity": self.honeypots.sensitivity,
                "file_monitoring": self.honeypots.file_monitoring,
                "network_monitoring": self.honeypots.network_monitoring
            },
            "network": {
                "global_sharing": self.network.global_sharing,
                "auto_updates": self.network.auto_updates,
                "upload_anonymous": self.network.upload_anonymous
            },
            "logging": {
                "level": self.logging.level,
                "file_path": self.logging.file_path,
                "enable_console": self.logging.enable_console,
                "enable_file": self.logging.enable_file
            }
        }
    
    def validate(self) -> Dict[str, str]:
        """אימות הגדרות"""
        errors = {}
        
        # Database validation
        if not self.database.password and self.deployment_mode == DeploymentMode.PRODUCTION:
            errors["database_password"] = "Database password is required in production"
        
        # Security validation
        if not self.security.secret_key:
            errors["secret_key"] = "Secret key is required"
        
        if len(self.security.secret_key) < 32:
            errors["secret_key_length"] = "Secret key must be at least 32 characters"
        
        # Performance validation
        if self.performance.max_memory_mb < 512:
            errors["memory"] = "Minimum memory requirement is 512MB"
        
        if self.performance.max_concurrent_tasks < 10:
            errors["concurrent_tasks"] = "Minimum concurrent tasks is 10"
        
        # Honeypot validation
        if self.honeypots.max_honeypots > 100:
            errors["max_honeypots"] = "Maximum honeypots cannot exceed 100"
        
        if self.honeypots.sensitivity not in ["low", "medium", "high"]:
            errors["honeypot_sensitivity"] = "Sensitivity must be low, medium, or high"
        
        return errors
    
    def get_health_check_config(self) -> Dict[str, Any]:
        """הגדרות בדיקת בריאות"""
        return {
            "enabled": True,
            "endpoint": "/health",
            "checks": {
                "database": True,
                "memory": True,
                "disk_space": True,
                "network": True,
                "honeypots": True
            },
            "thresholds": {
                "memory_usage_percent": 90,
                "disk_usage_percent": 85,
                "response_time_ms": 1000,
                "error_rate_percent": 5
            }
        }


# Global configuration instance
_config = None

def get_production_config(deployment_mode: DeploymentMode = None) -> ProductionConfig:
    """קבלת הגדרות ייצור"""
    global _config
    if _config is None:
        mode = deployment_mode or DeploymentMode(os.getenv("DEPLOYMENT_MODE", "production"))
        _config = ProductionConfig(mode)
    return _config

def reload_config():
    """טעינה מחדש של הגדרות"""
    global _config
    _config = None
    return get_production_config()
