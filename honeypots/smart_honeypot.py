"""
HoneyNet Smart Honeypot System
מערכת הפיתיונות החכמים של HoneyNet
"""

import asyncio
import logging
import os
import json
import hashlib
import secrets
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from pathlib import Path

from config.settings import get_settings
from config.security import SecurityConfig


class HoneypotType(Enum):
    """סוגי פיתיונות"""
    FILE = "file"
    CREDENTIAL = "credential"
    DATABASE = "database"
    NETWORK_SERVICE = "network_service"
    EMAIL = "email"
    DOCUMENT = "document"


class TriggerEvent(Enum):
    """אירועי הפעלת פיתיון"""
    FILE_ACCESS = "file_access"
    FILE_MODIFY = "file_modify"
    FILE_DELETE = "file_delete"
    CREDENTIAL_USE = "credential_use"
    NETWORK_SCAN = "network_scan"
    DATA_EXFILTRATION = "data_exfiltration"


@dataclass
class HoneypotTrigger:
    """אירוע הפעלת פיתיון"""
    honeypot_id: str
    trigger_type: TriggerEvent
    timestamp: datetime
    source_info: Dict
    attack_signature: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class SmartHoneypot:
    """פיתיון חכם"""
    id: str
    type: HoneypotType
    name: str
    path: str
    content: str
    created_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    is_active: bool = True
    decoy_level: float = 0.8  # רמת הסוואה (0-1)
    metadata: Dict = field(default_factory=dict)


class HoneypotManager:
    """מנהל הפיתיונות החכמים"""
    
    def __init__(self, base_path: str = "./honeypots_data"):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Active honeypots
        self.honeypots: Dict[str, SmartHoneypot] = {}
        self.file_watchers: Dict[str, threading.Thread] = {}
        self.trigger_callbacks: List[Callable[[HoneypotTrigger], None]] = []
        
        # Statistics
        self.stats = {
            "total_honeypots": 0,
            "active_honeypots": 0,
            "total_triggers": 0,
            "unique_attackers": set(),
            "last_trigger": None
        }
        
        self.logger.info("🍯 Smart Honeypot Manager initialized")
    
    async def initialize(self):
        """אתחול מנהל הפיתיונות"""
        self.logger.info("🚀 Initializing Smart Honeypot system...")
        
        # Create default honeypots
        await self._create_default_honeypots()
        
        # Start monitoring
        await self._start_monitoring()
        
        self.logger.info(f"✅ Honeypot system active with {len(self.honeypots)} honeypots")
    
    async def create_honeypot(
        self,
        honeypot_type: HoneypotType,
        name: str,
        content: str = None,
        metadata: Dict = None
    ) -> SmartHoneypot:
        """יצירת פיתיון חדש"""
        honeypot_id = self._generate_honeypot_id()
        honeypot_path = self.base_path / f"{honeypot_id}_{name}"
        
        if content is None:
            content = await self._generate_honeypot_content(honeypot_type, name)
        
        honeypot = SmartHoneypot(
            id=honeypot_id,
            type=honeypot_type,
            name=name,
            path=str(honeypot_path),
            content=content,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Create physical honeypot
        await self._deploy_honeypot(honeypot)
        
        # Add to active honeypots
        self.honeypots[honeypot_id] = honeypot
        self.stats["total_honeypots"] += 1
        self.stats["active_honeypots"] += 1
        
        # Start monitoring this honeypot
        await self._start_honeypot_monitoring(honeypot)
        
        self.logger.info(f"🍯 Created honeypot: {name} ({honeypot_type.value})")
        return honeypot
    
    async def _create_default_honeypots(self):
        """יצירת פיתיונות ברירת מחדל"""
        default_honeypots = [
            # Fake sensitive files
            {
                "honeypot_type": HoneypotType.FILE,
                "name": "passwords.txt",
                "content": await self._generate_fake_passwords()
            },
            {
                "honeypot_type": HoneypotType.FILE,
                "name": "id_rsa",
                "content": await self._generate_fake_ssh_key()
            },
            {
                "honeypot_type": HoneypotType.DOCUMENT,
                "name": "financial_report_2024.xlsx",
                "content": "fake_excel_data"
            },
            {
                "honeypot_type": HoneypotType.DATABASE,
                "name": "user_database.db",
                "content": await self._generate_fake_database()
            },
            {
                "honeypot_type": HoneypotType.CREDENTIAL,
                "name": "admin_credentials",
                "content": await self._generate_fake_credentials()
            }
        ]
        
        for honeypot_config in default_honeypots:
            await self.create_honeypot(**honeypot_config)
    
    async def _generate_honeypot_content(self, honeypot_type: HoneypotType, name: str) -> str:
        """יצירת תוכן פיתיון"""
        if honeypot_type == HoneypotType.FILE:
            return await self._generate_fake_file_content(name)
        elif honeypot_type == HoneypotType.CREDENTIAL:
            return await self._generate_fake_credentials()
        elif honeypot_type == HoneypotType.DATABASE:
            return await self._generate_fake_database()
        elif honeypot_type == HoneypotType.DOCUMENT:
            return await self._generate_fake_document()
        else:
            return f"Honeypot content for {name}"
    
    async def _generate_fake_passwords(self) -> str:
        """יצירת קובץ סיסמאות מזויף"""
        fake_passwords = [
            "admin:P@ssw0rd123!",
            "root:SuperSecret2024",
            "user:MyPassword456",
            "backup:BackupKey789",
            "service:ServiceAccount2024",
            "database:DbAdmin2024!",
            "ftp:FtpUser123",
            "email:EmailPass456"
        ]
        return "\n".join(fake_passwords)
    
    async def _generate_fake_ssh_key(self) -> str:
        """יצירת מפתח SSH מזויף"""
        return """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEA2K8Zv5H9kF3mN2pQ7xR4yS8wE6vL1nM9oP3qR5tU7wX2yA9bC1dE
fG3hI4jK5lM6nO7pQ8rS9tU0vW1xY2zA3bC4dE5fG6hI7jK8lM9nO0pQ1rS2tU3vW4xY
5zA6bC7dE8fG9hI0jK2lM3nO4pQ5rS6tU7vW8xY8zA9bC0dE1fG2hI3jK4lM5nO6pQ7r
S8tU9vW0xY1zA2bC3dE4fG5hI6jK7lM8nO9pQ0rS1tU2vW3xY4zA5bC6dE7fG8hI9jK0
lM2nO3pQ4rS5tU6vW7xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9xY0zA1bC2dE
3fG4hI5jK6lM7nO8pQ9rS0tU1vW2xY3zA4bC5dE6fG7hI8jK9lM1nO2pQ3rS4tU5vW6x
Y6zA7bC8dE9fG0hI1jK2lM0nO1pQ2rS3tU4vW5xY5zA6bC7dE8fG9hI0jK1lM3nO4pQ5
-----END OPENSSH PRIVATE KEY-----"""
    
    async def _generate_fake_database(self) -> str:
        """יצירת מסד נתונים מזויף"""
        fake_db_content = {
            "users": [
                {"id": 1, "username": "admin", "email": "admin@company.com", "role": "administrator"},
                {"id": 2, "username": "john_doe", "email": "john@company.com", "role": "user"},
                {"id": 3, "username": "jane_smith", "email": "jane@company.com", "role": "manager"}
            ],
            "sessions": [
                {"session_id": "sess_123456", "user_id": 1, "created_at": "2024-01-15T10:30:00Z"},
                {"session_id": "sess_789012", "user_id": 2, "created_at": "2024-01-15T11:45:00Z"}
            ]
        }
        return json.dumps(fake_db_content, indent=2)
    
    async def _generate_fake_credentials(self) -> str:
        """יצירת פרטי גישה מזויפים"""
        fake_creds = {
            "aws_access_key": "AKIA" + secrets.token_hex(8).upper(),
            "aws_secret_key": secrets.token_hex(20),
            "database_url": "postgresql://admin:secret123@db.company.com:5432/production",
            "api_key": "sk-" + secrets.token_hex(24),
            "jwt_secret": secrets.token_hex(32)
        }
        return json.dumps(fake_creds, indent=2)
    
    async def _generate_fake_document(self) -> str:
        """יצירת מסמך מזויף"""
        return """CONFIDENTIAL - FINANCIAL REPORT 2024
        
Company: HoneyNet Corp
Quarter: Q4 2024
Revenue: $50,000,000
Profit: $12,000,000
Expenses: $38,000,000

Key Metrics:
- Customer Growth: 25%
- Market Share: 15%
- Employee Count: 500

This document contains sensitive financial information.
Unauthorized access is strictly prohibited."""
    
    async def _deploy_honeypot(self, honeypot: SmartHoneypot):
        """פריסת פיתיון פיזית"""
        try:
            # Create honeypot file
            with open(honeypot.path, 'w', encoding='utf-8') as f:
                f.write(honeypot.content)
            
            # Set appropriate permissions to make it look legitimate
            os.chmod(honeypot.path, 0o600)  # Read/write for owner only
            
            self.logger.debug(f"📁 Deployed honeypot file: {honeypot.path}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy honeypot {honeypot.id}: {e}")
            raise
    
    async def _start_honeypot_monitoring(self, honeypot: SmartHoneypot):
        """התחלת ניטור פיתיון"""
        if honeypot.type == HoneypotType.FILE:
            # Start file monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_file_honeypot,
                args=(honeypot,),
                daemon=True
            )
            monitor_thread.start()
            self.file_watchers[honeypot.id] = monitor_thread
    
    def _monitor_file_honeypot(self, honeypot: SmartHoneypot):
        """ניטור פיתיון קובץ"""
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class HoneypotEventHandler(FileSystemEventHandler):
            def __init__(self, manager, honeypot):
                self.manager = manager
                self.honeypot = honeypot
            
            def on_any_event(self, event):
                if event.src_path == self.honeypot.path:
                    asyncio.run_coroutine_threadsafe(
                        self.manager._handle_honeypot_trigger(
                            self.honeypot,
                            TriggerEvent.FILE_ACCESS,
                            {"event_type": event.event_type, "path": event.src_path}
                        ),
                        asyncio.get_event_loop()
                    )
        
        observer = Observer()
        event_handler = HoneypotEventHandler(self, honeypot)
        observer.schedule(event_handler, os.path.dirname(honeypot.path), recursive=False)
        observer.start()
        
        try:
            while honeypot.is_active:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
    
    async def _handle_honeypot_trigger(
        self,
        honeypot: SmartHoneypot,
        trigger_type: TriggerEvent,
        source_info: Dict
    ):
        """טיפול בהפעלת פיתיון"""
        # Create trigger event
        trigger = HoneypotTrigger(
            honeypot_id=honeypot.id,
            trigger_type=trigger_type,
            timestamp=datetime.now(),
            source_info=source_info,
            attack_signature=self._generate_attack_signature(source_info)
        )
        
        # Update honeypot statistics
        honeypot.last_triggered = trigger.timestamp
        honeypot.trigger_count += 1
        
        # Update global statistics
        self.stats["total_triggers"] += 1
        self.stats["last_trigger"] = trigger.timestamp
        
        # Log the trigger
        self.logger.warning(
            f"🚨 HONEYPOT TRIGGERED! {honeypot.name} ({trigger_type.value}) - "
            f"Potential attacker detected!"
        )
        
        # Notify callbacks
        for callback in self.trigger_callbacks:
            try:
                callback(trigger)
            except Exception as e:
                self.logger.error(f"Error in trigger callback: {e}")
        
        # Rotate honeypot to maintain deception
        await self._rotate_honeypot(honeypot)
    
    def _generate_attack_signature(self, source_info: Dict) -> str:
        """יצירת חתימת התקפה"""
        signature_data = json.dumps(source_info, sort_keys=True)
        return hashlib.sha256(signature_data.encode()).hexdigest()[:16]
    
    async def _rotate_honeypot(self, honeypot: SmartHoneypot):
        """סיבוב פיתיון לשמירה על הסוואה"""
        try:
            # Generate new content
            new_content = await self._generate_honeypot_content(honeypot.type, honeypot.name)
            
            # Update honeypot
            honeypot.content = new_content
            
            # Redeploy
            await self._deploy_honeypot(honeypot)
            
            self.logger.info(f"🔄 Rotated honeypot: {honeypot.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to rotate honeypot {honeypot.id}: {e}")
    
    async def _start_monitoring(self):
        """התחלת ניטור כללי"""
        # Start background tasks for honeypot management
        asyncio.create_task(self._honeypot_maintenance_loop())
        asyncio.create_task(self._statistics_update_loop())
    
    async def _honeypot_maintenance_loop(self):
        """לולאת תחזוקת פיתיונות"""
        while True:
            try:
                # Rotate old honeypots
                for honeypot in self.honeypots.values():
                    if (honeypot.last_triggered and 
                        datetime.now() - honeypot.last_triggered > timedelta(hours=24)):
                        await self._rotate_honeypot(honeypot)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Error in maintenance loop: {e}")
                await asyncio.sleep(300)
    
    async def _statistics_update_loop(self):
        """לולאת עדכון סטטיסטיקות"""
        while True:
            try:
                active_count = sum(1 for h in self.honeypots.values() if h.is_active)
                self.stats["active_honeypots"] = active_count
                
                self.logger.info(
                    f"🍯 Honeypot Stats - Active: {active_count}, "
                    f"Total Triggers: {self.stats['total_triggers']}"
                )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error updating statistics: {e}")
                await asyncio.sleep(60)
    
    def add_trigger_callback(self, callback: Callable[[HoneypotTrigger], None]):
        """הוספת callback להפעלת פיתיון"""
        self.trigger_callbacks.append(callback)
    
    def _generate_honeypot_id(self) -> str:
        """יצירת ID ייחודי לפיתיון"""
        return f"hp_{secrets.token_hex(8)}"
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות פיתיונות"""
        return {
            **self.stats,
            "unique_attackers": len(self.stats["unique_attackers"]),
            "honeypots_by_type": {
                htype.value: sum(1 for h in self.honeypots.values() if h.type == htype)
                for htype in HoneypotType
            }
        }
    
    async def shutdown(self):
        """כיבוי מנהל הפיתיונות"""
        self.logger.info("🛑 Shutting down Honeypot Manager...")
        
        # Deactivate all honeypots
        for honeypot in self.honeypots.values():
            honeypot.is_active = False
        
        # Stop file watchers
        for watcher in self.file_watchers.values():
            if watcher.is_alive():
                watcher.join(timeout=5)
        
        self.logger.info("✅ Honeypot Manager shutdown complete")
