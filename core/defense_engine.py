"""
HoneyNet Defense Engine
מנוע ההגנה המרכזי של HoneyNet
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta

from config.settings import get_settings
from config.security import SecurityConfig


class ThreatLevel(Enum):
    """רמות איום"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(Enum):
    """סוגי התקפות"""
    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    DATA_BREACH = "data_breach"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    UNKNOWN = "unknown"


@dataclass
class ThreatEvent:
    """אירוע איום"""
    id: str
    timestamp: datetime
    source_ip: str
    target_device: str
    attack_type: AttackType
    threat_level: ThreatLevel
    description: str
    honeypot_triggered: bool = False
    attack_signature: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class DefenseAction:
    """פעולת הגנה"""
    action_type: str
    target: str
    parameters: Dict
    timestamp: datetime
    success: bool = False


class DefenseEngine:
    """מנוע ההגנה המרכזי - לב המערכת"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Active threats tracking
        self.active_threats: Dict[str, ThreatEvent] = {}
        self.blocked_ips: Set[str] = set()
        self.defense_actions: List[DefenseAction] = []
        
        # Statistics
        self.stats = {
            "threats_detected": 0,
            "attacks_blocked": 0,
            "honeypots_triggered": 0,
            "false_positives": 0,
            "uptime_start": datetime.now()
        }
        
        # Defense mechanisms
        self.is_active = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        self.logger.info("🛡️ Defense Engine initialized")
    
    async def start(self):
        """הפעלת מנוע ההגנה"""
        if self.is_active:
            self.logger.warning("Defense Engine already active")
            return
        
        self.is_active = True
        self.logger.info("🚀 Starting HoneyNet Defense Engine...")
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._threat_monitoring_loop()),
            asyncio.create_task(self._cleanup_old_threats()),
            asyncio.create_task(self._update_defense_statistics())
        ]
        
        self.logger.info("✅ Defense Engine is now ACTIVE and protecting the network!")
    
    async def stop(self):
        """עצירת מנוע ההגנה"""
        self.is_active = False
        self.logger.info("🛑 Stopping Defense Engine...")
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()
        
        self.logger.info("⏹️ Defense Engine stopped")
    
    async def process_threat(self, threat: ThreatEvent) -> bool:
        """עיבוד איום חדש"""
        self.logger.info(f"🚨 Processing threat: {threat.id} - {threat.attack_type.value}")
        
        # Add to active threats
        self.active_threats[threat.id] = threat
        self.stats["threats_detected"] += 1
        
        # Determine defense actions based on threat level
        actions = await self._determine_defense_actions(threat)
        
        # Execute defense actions
        success = True
        for action in actions:
            action_success = await self._execute_defense_action(action)
            if not action_success:
                success = False
            self.defense_actions.append(action)
        
        # Update statistics
        if success:
            self.stats["attacks_blocked"] += 1
            self.logger.info(f"✅ Threat {threat.id} successfully mitigated")
        else:
            self.logger.error(f"❌ Failed to fully mitigate threat {threat.id}")
        
        # Notify network about the threat
        await self._broadcast_threat_to_network(threat)
        
        return success
    
    async def _determine_defense_actions(self, threat: ThreatEvent) -> List[DefenseAction]:
        """קביעת פעולות הגנה נדרשות"""
        actions = []
        now = datetime.now()
        
        # Always block the source IP for high/critical threats
        if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            actions.append(DefenseAction(
                action_type="block_ip",
                target=threat.source_ip,
                parameters={"duration_hours": 24},
                timestamp=now
            ))
        
        # Isolate device for critical threats
        if threat.threat_level == ThreatLevel.CRITICAL:
            actions.append(DefenseAction(
                action_type="isolate_device",
                target=threat.target_device,
                parameters={"quarantine": True},
                timestamp=now
            ))
        
        # Update honeypots based on attack type
        if threat.attack_type in [AttackType.MALWARE, AttackType.RANSOMWARE]:
            actions.append(DefenseAction(
                action_type="update_honeypots",
                target="all_devices",
                parameters={"attack_signature": threat.attack_signature},
                timestamp=now
            ))
        
        # Alert user for medium+ threats
        if threat.threat_level != ThreatLevel.LOW:
            actions.append(DefenseAction(
                action_type="alert_user",
                target=threat.target_device,
                parameters={
                    "message": f"Threat detected: {threat.description}",
                    "urgency": threat.threat_level.value
                },
                timestamp=now
            ))
        
        return actions
    
    async def _execute_defense_action(self, action: DefenseAction) -> bool:
        """ביצוע פעולת הגנה"""
        try:
            self.logger.info(f"🔧 Executing defense action: {action.action_type}")
            
            if action.action_type == "block_ip":
                return await self._block_ip(action.target, action.parameters)
            elif action.action_type == "isolate_device":
                return await self._isolate_device(action.target, action.parameters)
            elif action.action_type == "update_honeypots":
                return await self._update_honeypots(action.parameters)
            elif action.action_type == "alert_user":
                return await self._alert_user(action.target, action.parameters)
            else:
                self.logger.warning(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to execute action {action.action_type}: {e}")
            return False
    
    async def _block_ip(self, ip: str, parameters: Dict) -> bool:
        """חסימת IP"""
        self.blocked_ips.add(ip)
        duration = parameters.get("duration_hours", 1)
        self.logger.info(f"🚫 Blocked IP {ip} for {duration} hours")
        
        # Schedule unblock (in real implementation, this would be persistent)
        asyncio.create_task(self._schedule_ip_unblock(ip, duration))
        return True
    
    async def _isolate_device(self, device: str, parameters: Dict) -> bool:
        """בידוד מכשיר"""
        self.logger.info(f"🔒 Isolating device {device}")
        # In real implementation, this would disconnect the device from network
        return True
    
    async def _update_honeypots(self, parameters: Dict) -> bool:
        """עדכון פיתיונות"""
        signature = parameters.get("attack_signature")
        self.logger.info(f"🍯 Updating honeypots with new attack signature: {signature}")
        # In real implementation, this would update honeypot configurations
        return True
    
    async def _alert_user(self, device: str, parameters: Dict) -> bool:
        """התרעה למשתמש"""
        message = parameters.get("message", "Threat detected")
        urgency = parameters.get("urgency", "medium")
        self.logger.info(f"📢 Alerting user on {device}: {message} (urgency: {urgency})")
        # In real implementation, this would send notification to user
        return True
    
    async def _schedule_ip_unblock(self, ip: str, hours: int):
        """תזמון ביטול חסימת IP"""
        await asyncio.sleep(hours * 3600)  # Convert hours to seconds
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            self.logger.info(f"🔓 Unblocked IP {ip} after {hours} hours")
    
    async def _broadcast_threat_to_network(self, threat: ThreatEvent):
        """שידור איום לרשת הגלובלית"""
        # Create threat broadcast message
        broadcast_data = {
            "threat_id": threat.id,
            "attack_type": threat.attack_type.value,
            "threat_level": threat.threat_level.value,
            "source_ip": threat.source_ip,
            "attack_signature": threat.attack_signature,
            "timestamp": threat.timestamp.isoformat(),
            "description": threat.description
        }
        
        self.logger.info(f"📡 Broadcasting threat {threat.id} to global network")
        # In real implementation, this would send to network coordinator
        return True
    
    async def _threat_monitoring_loop(self):
        """לולאת ניטור איומים"""
        while self.is_active:
            try:
                # Monitor system resources, network traffic, etc.
                await self._check_system_health()
                await asyncio.sleep(self.settings.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Error in threat monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_old_threats(self):
        """ניקוי איומים ישנים"""
        while self.is_active:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                old_threats = [
                    threat_id for threat_id, threat in self.active_threats.items()
                    if threat.timestamp < cutoff_time
                ]
                
                for threat_id in old_threats:
                    del self.active_threats[threat_id]
                
                if old_threats:
                    self.logger.info(f"🧹 Cleaned up {len(old_threats)} old threats")
                
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def _update_defense_statistics(self):
        """עדכון סטטיסטיקות הגנה"""
        while self.is_active:
            try:
                uptime = datetime.now() - self.stats["uptime_start"]
                self.logger.info(
                    f"📊 Defense Stats - Threats: {self.stats['threats_detected']}, "
                    f"Blocked: {self.stats['attacks_blocked']}, "
                    f"Uptime: {uptime}"
                )
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                self.logger.error(f"Error updating statistics: {e}")
                await asyncio.sleep(60)
    
    async def _check_system_health(self):
        """בדיקת בריאות המערכת"""
        # Check CPU, memory, network usage
        # In real implementation, this would monitor actual system metrics
        pass
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות המערכת"""
        uptime = datetime.now() - self.stats["uptime_start"]
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "active_threats_count": len(self.active_threats),
            "blocked_ips_count": len(self.blocked_ips),
            "is_active": self.is_active
        }
    
    def is_ip_blocked(self, ip: str) -> bool:
        """בדיקה האם IP חסום"""
        return ip in self.blocked_ips
