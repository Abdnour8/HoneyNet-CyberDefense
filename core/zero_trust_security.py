"""
HoneyNet Zero-Trust Security Architecture
מערכת אבטחה מתקדמת מבוססת Zero-Trust
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import ipaddress
from collections import defaultdict, deque

from .memory_manager import memory_manager
from .event_bus import event_bus, Event, EventType, EventPriority


class TrustLevel(Enum):
    """רמות אמון במערכת"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    TRUSTED = 4


class SecurityRisk(Enum):
    """רמות סיכון אבטחה"""
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class SecurityContext:
    """הקשר אבטחה למשתמש/מכשיר"""
    entity_id: str
    entity_type: str
    trust_level: TrustLevel
    risk_score: float
    last_verification: datetime
    ip_address: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)


class ZeroTrustManager:
    """מנהל אבטחה מבוסס Zero-Trust"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_contexts: Dict[str, SecurityContext] = {}
        self.blocked_entities: Set[str] = set()
        self.security_events: deque = deque(maxlen=10000)
        
        # Generate encryption key
        self.master_key = Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        
        self.security_metrics = {
            "total_requests": 0,
            "blocked_requests": 0,
            "security_events": 0,
            "trust_violations": 0
        }
        
        self.logger.info("🛡️ Zero-Trust Security Manager initialized")
    
    async def authenticate_entity(self, entity_id: str, credentials: Dict) -> Tuple[bool, SecurityContext]:
        """אימות ישות במערכת"""
        # Create security context
        context = SecurityContext(
            entity_id=entity_id,
            entity_type=credentials.get("type", "user"),
            trust_level=TrustLevel.LOW,
            risk_score=0.5,
            last_verification=datetime.now(),
            ip_address=credentials.get("ip_address")
        )
        
        # Verify credentials (simplified)
        if self._verify_credentials(credentials):
            self.security_contexts[entity_id] = context
            await self._log_security_event(entity_id, "authentication_success", SecurityRisk.LOW, {})
            return True, context
        
        await self._log_security_event(entity_id, "authentication_failed", SecurityRisk.HIGH, {})
        return False, context
    
    async def authorize_access(self, entity_id: str, resource: str, action: str) -> Tuple[bool, str]:
        """אישור גישה למשאב"""
        self.security_metrics["total_requests"] += 1
        
        if entity_id not in self.security_contexts:
            self.security_metrics["blocked_requests"] += 1
            return False, "Entity not authenticated"
        
        if entity_id in self.blocked_entities:
            self.security_metrics["blocked_requests"] += 1
            return False, "Entity is blocked"
        
        context = self.security_contexts[entity_id]
        
        # Risk analysis
        risk_score = await self._calculate_risk(context, resource, action)
        
        if risk_score > 0.8:
            self.security_metrics["blocked_requests"] += 1
            self.security_metrics["trust_violations"] += 1
            await self._log_security_event(entity_id, "access_denied_high_risk", SecurityRisk.HIGH, 
                                         {"resource": resource, "risk_score": risk_score})
            return False, "High risk access denied"
        
        # Update context
        context.last_verification = datetime.now()
        
        await self._log_security_event(entity_id, "access_granted", SecurityRisk.LOW,
                                     {"resource": resource, "action": action})
        return True, "Access granted"
    
    def _verify_credentials(self, credentials: Dict) -> bool:
        """אימות פרטי כניסה"""
        # Simplified credential verification
        return credentials.get("username") and credentials.get("password")
    
    async def _calculate_risk(self, context: SecurityContext, resource: str, action: str) -> float:
        """חישוב רמת סיכון"""
        risk = 0.0
        
        # Time-based risk
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            risk += 0.2
        
        # IP-based risk (simplified)
        if context.ip_address:
            try:
                ip = ipaddress.ip_address(context.ip_address)
                if not ip.is_private:
                    risk += 0.3
            except:
                risk += 0.5
        
        # Trust level impact
        trust_factor = (TrustLevel.TRUSTED.value - context.trust_level.value) / TrustLevel.TRUSTED.value
        risk += trust_factor * 0.4
        
        return min(risk, 1.0)
    
    async def _log_security_event(self, entity_id: str, event_type: str, risk_level: SecurityRisk, details: Dict):
        """רישום אירוע אבטחה"""
        event = {
            "event_id": f"sec_{int(time.time())}_{secrets.token_hex(4)}",
            "timestamp": datetime.now(),
            "entity_id": entity_id,
            "event_type": event_type,
            "risk_level": risk_level.name,
            "details": details
        }
        
        self.security_events.append(event)
        self.security_metrics["security_events"] += 1
        
        # Publish to event bus
        await event_bus.publish(Event(
            event_id=event["event_id"],
            event_type=EventType.SYSTEM_WARNING if risk_level.value >= 3 else EventType.CUSTOM,
            priority=EventPriority.HIGH if risk_level.value >= 4 else EventPriority.NORMAL,
            timestamp=event["timestamp"],
            source="zero_trust_security",
            data={"security_event": event}
        ))
        
        self.logger.info(f"🚨 Security event: {event_type} for {entity_id}")
    
    def encrypt_data(self, data: str) -> str:
        """הצפנת נתונים"""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """פענוח נתונים"""
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(decoded)
        return decrypted.decode()
    
    def get_security_stats(self) -> Dict:
        """קבלת סטטיסטיקות אבטחה"""
        return {
            "metrics": self.security_metrics,
            "active_contexts": len(self.security_contexts),
            "blocked_entities": len(self.blocked_entities),
            "recent_events": len([e for e in self.security_events 
                                if (datetime.now() - e["timestamp"]).total_seconds() < 3600])
        }


# Global zero-trust manager instance
zero_trust_manager = ZeroTrustManager()
