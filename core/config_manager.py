"""
HoneyNet Configuration Manager
מנהל התצורה של HoneyNet
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import configparser

logger = logging.getLogger(__name__)


class ConfigManager:
    """מנהל התצורה של HoneyNet"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "honeynet.json"
        self.user_config_file = self.config_dir / "user_settings.json"
        
        # Default configuration
        self.default_config = {
            "server": {
                "host": "localhost",
                "port": 8000,
                "debug": False,
                "log_level": "INFO"
            },
            "security": {
                "enable_encryption": True,
                "max_login_attempts": 3,
                "session_timeout": 3600,
                "enable_2fa": False
            },
            "honeypots": {
                "auto_create": True,
                "max_honeypots": 100,
                "cleanup_interval": 86400,
                "default_types": ["file", "network", "credential"]
            },
            "monitoring": {
                "enable_file_monitoring": True,
                "enable_network_monitoring": True,
                "alert_threshold": 5,
                "log_retention_days": 30
            },
            "ai": {
                "enable_threat_analysis": True,
                "learning_mode": "adaptive",
                "confidence_threshold": 0.7,
                "model_update_interval": 3600
            },
            "notifications": {
                "enable_email": False,
                "enable_sms": False,
                "enable_desktop": True,
                "email_server": "",
                "email_port": 587
            },
            "performance": {
                "max_memory_usage": 1024,  # MB
                "max_cpu_usage": 80,  # %
                "enable_caching": True,
                "cache_size": 256  # MB
            }
        }
        
        self.config = self.default_config.copy()
        self.user_settings = {}
        
        self.load_config()
        logger.info("Configuration Manager initialized")
    
    def load_config(self):
        """טעינת התצורה מהקובץ"""
        try:
            # Load main config
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(self.config, loaded_config)
                logger.info("Main configuration loaded successfully")
            else:
                self.save_config()  # Create default config file
            
            # Load user settings
            if self.user_config_file.exists():
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    self.user_settings = json.load(f)
                logger.info("User settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """שמירת התצורה לקובץ"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, indent=4, ensure_ascii=False)
            
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """קבלת ערך מהתצורה"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get config value for key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """הגדרת ערך בתצורה"""
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            logger.info(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set config value for key '{key}': {e}")
            return False
    
    def get_user_setting(self, key: str, default: Any = None) -> Any:
        """קבלת הגדרת משתמש"""
        return self.user_settings.get(key, default)
    
    def set_user_setting(self, key: str, value: Any) -> bool:
        """הגדרת הגדרת משתמש"""
        try:
            self.user_settings[key] = value
            logger.info(f"User setting updated: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set user setting '{key}': {e}")
            return False
    
    def reset_to_defaults(self):
        """איפוס התצורה לברירות המחדל"""
        self.config = self.default_config.copy()
        self.user_settings = {}
        logger.info("Configuration reset to defaults")
    
    def export_config(self, filepath: str) -> bool:
        """ייצוא התצורה לקובץ"""
        try:
            export_data = {
                'config': self.config,
                'user_settings': self.user_settings,
                'export_timestamp': str(Path(filepath).stat().st_mtime)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuration exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, filepath: str) -> bool:
        """ייבוא התצורה מקובץ"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'config' in import_data:
                self.config = import_data['config']
            
            if 'user_settings' in import_data:
                self.user_settings = import_data['user_settings']
            
            logger.info(f"Configuration imported from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """בדיקת תקינות התצורה"""
        issues = []
        warnings = []
        
        try:
            # Check server configuration
            if not isinstance(self.get('server.port'), int) or not (1 <= self.get('server.port') <= 65535):
                issues.append("Invalid server port")
            
            # Check security settings
            if self.get('security.max_login_attempts', 0) < 1:
                warnings.append("Max login attempts should be at least 1")
            
            # Check honeypot settings
            if self.get('honeypots.max_honeypots', 0) < 1:
                issues.append("Max honeypots must be at least 1")
            
            # Check performance settings
            memory_limit = self.get('performance.max_memory_usage', 0)
            if memory_limit < 128:
                warnings.append("Memory limit might be too low (recommended: 512MB+)")
            
            # Check AI settings
            confidence = self.get('ai.confidence_threshold', 0)
            if not (0.0 <= confidence <= 1.0):
                issues.append("AI confidence threshold must be between 0.0 and 1.0")
            
        except Exception as e:
            issues.append(f"Configuration validation error: {e}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _merge_config(self, base: Dict, update: Dict):
        """מיזוג תצורות"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_all_settings(self) -> Dict[str, Any]:
        """קבלת כל ההגדרות"""
        return {
            'config': self.config,
            'user_settings': self.user_settings
        }
    
    def get_security_settings(self) -> Dict[str, Any]:
        """קבלת הגדרות אבטחה"""
        return self.get('security', {})
    
    def get_honeypot_settings(self) -> Dict[str, Any]:
        """קבלת הגדרות פחים"""
        return self.get('honeypots', {})
    
    def get_monitoring_settings(self) -> Dict[str, Any]:
        """קבלת הגדרות ניטור"""
        return self.get('monitoring', {})
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """קבלת הגדרות AI"""
        return self.get('ai', {})
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """קבלת הגדרות התראות"""
        return self.get('notifications', {})
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """קבלת הגדרות ביצועים"""
        return self.get('performance', {})
    
    def is_debug_mode(self) -> bool:
        """בדיקה אם מצב debug פעיל"""
        return self.get('server.debug', False)
    
    def get_log_level(self) -> str:
        """קבלת רמת הלוגים"""
        return self.get('server.log_level', 'INFO')
    
    def cleanup(self):
        """ניקוי המנהל"""
        try:
            self.save_config()
            logger.info("Configuration manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
