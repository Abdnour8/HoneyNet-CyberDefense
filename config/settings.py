"""
HoneyNet Settings Configuration
הגדרות תצורה של HoneyNet
"""

import os
from typing import Optional, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for older versions
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

try:
    from pydantic import Field
except ImportError:
    def Field(default=None, **kwargs):
        return default
from functools import lru_cache


class Settings(BaseSettings):
    """הגדרות ראשיות של המערכת"""
    
    # Application Info
    app_name: str = "HoneyNet"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://honeynet:password@localhost/honeynet",
        env="DATABASE_URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Security Settings
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # HoneyNet Specific Settings
    honeypot_enabled: bool = True
    max_honeypots_per_client: int = 50
    threat_analysis_enabled: bool = True
    global_sharing_enabled: bool = True
    
    # AI/ML Configuration
    ai_model_path: str = "./models/"
    threat_detection_threshold: float = 0.75
    learning_rate: float = 0.001
    batch_size: int = 32
    
    # Network Configuration
    max_connections: int = 1000
    heartbeat_interval: int = 30  # seconds
    sync_interval: int = 300  # 5 minutes
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = "./logs/honeynet.log"
    
    # Client Configuration
    client_update_interval: int = 60  # seconds
    max_client_memory_mb: int = 512
    
    # Gamification
    points_per_threat_detected: int = 100
    points_per_honeypot_triggered: int = 50
    leaderboard_enabled: bool = True
    
    # Business Model Tiers
    free_tier_max_devices: int = 3
    pro_tier_max_devices: int = 50
    enterprise_tier_max_devices: int = -1  # unlimited
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """קבלת הגדרות המערכת (cached)"""
    return Settings()


# Global settings instance
settings = get_settings()
