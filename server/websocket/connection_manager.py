"""
HoneyNet Global Server - Connection Manager
מנהל חיבורים לשרת HoneyNet הגלובלי
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from fastapi import WebSocket
import uuid
from dataclasses import dataclass, field


@dataclass
class ClientConnection:
    """מידע על חיבור לקוח"""
    client_id: str
    websocket: WebSocket
    platform: str  # 'desktop', 'mobile', 'server'
    device_info: Dict
    connected_at: datetime
    last_heartbeat: datetime
    threat_reports: int = 0
    honeypot_triggers: int = 0
    points: int = 0
    location: Optional[str] = None
    version: Optional[str] = None


class ConnectionManager:
    """מנהל חיבורי WebSocket לרשת הגלובלית"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Active connections
        self.connections: Dict[str, ClientConnection] = {}
        self.websockets: Dict[WebSocket, str] = {}  # Reverse lookup
        
        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0
        
        # Connection groups for targeted broadcasting
        self.mobile_clients: Set[str] = set()
        self.desktop_clients: Set[str] = set()
        self.server_clients: Set[str] = set()
        
        self.logger.info("🔌 Connection Manager initialized")
    
    async def register_client(self, websocket: WebSocket, registration_data: Dict) -> str:
        """רישום לקוח חדש"""
        client_id = f"{registration_data.get('platform', 'unknown')}_{uuid.uuid4().hex[:8]}"
        
        # Create client connection
        connection = ClientConnection(
            client_id=client_id,
            websocket=websocket,
            platform=registration_data.get('platform', 'unknown'),
            device_info=registration_data.get('device_info', {}),
            connected_at=datetime.now(),
            last_heartbeat=datetime.now(),
            location=registration_data.get('location'),
            version=registration_data.get('version')
        )
        
        # Store connection
        self.connections[client_id] = connection
        self.websockets[websocket] = client_id
        
        # Add to platform-specific groups
        if connection.platform == 'mobile':
            self.mobile_clients.add(client_id)
        elif connection.platform == 'desktop':
            self.desktop_clients.add(client_id)
        elif connection.platform == 'server':
            self.server_clients.add(client_id)
        
        self.total_connections += 1
        
        self.logger.info(
            f"📱 Client registered: {client_id} "
            f"({connection.platform}) - "
            f"Total: {len(self.connections)}"
        )
        
        # Broadcast new node joined to network
        await self.broadcast_network_update({
            "type": "node_joined",
            "client_id": client_id,
            "platform": connection.platform,
            "total_nodes": len(self.connections)
        }, exclude_client=client_id)
        
        return client_id
    
    async def unregister_client(self, client_id: str):
        """ביטול רישום לקוח"""
        if client_id not in self.connections:
            return
        
        connection = self.connections[client_id]
        
        # Remove from platform groups
        self.mobile_clients.discard(client_id)
        self.desktop_clients.discard(client_id)
        self.server_clients.discard(client_id)
        
        # Remove from connections
        if connection.websocket in self.websockets:
            del self.websockets[connection.websocket]
        del self.connections[client_id]
        
        self.logger.info(
            f"🔌 Client unregistered: {client_id} "
            f"- Remaining: {len(self.connections)}"
        )
        
        # Broadcast node left to network
        await self.broadcast_network_update({
            "type": "node_left",
            "client_id": client_id,
            "total_nodes": len(self.connections)
        })
    
    async def send_to_client(self, client_id: str, message: Dict):
        """שליחת הודעה ללקוח ספציפי"""
        if client_id not in self.connections:
            self.logger.warning(f"Attempted to send to non-existent client: {client_id}")
            return False
        
        connection = self.connections[client_id]
        
        try:
            message_json = json.dumps(message, ensure_ascii=False, default=str)
            await connection.websocket.send_text(message_json)
            
            self.total_messages_sent += 1
            self.logger.debug(f"📤 Message sent to {client_id}: {message.get('type', 'unknown')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {client_id}: {e}")
            # Remove broken connection
            await self.unregister_client(client_id)
            return False
    
    async def send_error(self, client_id: str, error_message: str):
        """שליחת הודעת שגיאה ללקוח"""
        await self.send_to_client(client_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_to_all(self, message: Dict, exclude_client: Optional[str] = None):
        """שידור הודעה לכל הלקוחות"""
        if not self.connections:
            return
        
        message["broadcast"] = True
        message["timestamp"] = datetime.now().isoformat()
        
        successful_sends = 0
        failed_clients = []
        
        for client_id in list(self.connections.keys()):
            if exclude_client and client_id == exclude_client:
                continue
            
            success = await self.send_to_client(client_id, message)
            if success:
                successful_sends += 1
            else:
                failed_clients.append(client_id)
        
        self.logger.info(
            f"📡 Broadcast sent to {successful_sends}/{len(self.connections)} clients "
            f"(type: {message.get('type', 'unknown')})"
        )
        
        # Clean up failed clients
        for client_id in failed_clients:
            await self.unregister_client(client_id)
    
    async def broadcast_to_platform(self, platform: str, message: Dict):
        """שידור הודעה לפלטפורמה ספציפית"""
        if platform == 'mobile':
            target_clients = self.mobile_clients
        elif platform == 'desktop':
            target_clients = self.desktop_clients
        elif platform == 'server':
            target_clients = self.server_clients
        else:
            self.logger.warning(f"Unknown platform for broadcast: {platform}")
            return
        
        if not target_clients:
            return
        
        message["platform_broadcast"] = platform
        message["timestamp"] = datetime.now().isoformat()
        
        successful_sends = 0
        
        for client_id in list(target_clients):
            success = await self.send_to_client(client_id, message)
            if success:
                successful_sends += 1
        
        self.logger.info(
            f"📱 Platform broadcast ({platform}) sent to {successful_sends} clients"
        )
    
    async def broadcast_threat_alert(self, threat_data: Dict):
        """שידור התרעת איום גלובלית"""
        alert_message = {
            "type": "global_threat_alert",
            "severity": threat_data.get("severity", "medium"),
            "threat_type": threat_data.get("type", "unknown"),
            "description": threat_data.get("description", ""),
            "source_region": threat_data.get("source_region", "unknown"),
            "mitigation_advice": threat_data.get("mitigation", ""),
            "threat_id": threat_data.get("id"),
            "priority": "high" if threat_data.get("severity") == "critical" else "normal"
        }
        
        await self.broadcast_to_all(alert_message)
        
        self.logger.warning(
            f"🚨 GLOBAL THREAT ALERT broadcasted: "
            f"{threat_data.get('type', 'unknown')} - "
            f"{threat_data.get('severity', 'unknown')}"
        )
    
    async def broadcast_honeypot_update(self, honeypot_data: Dict):
        """שידור עדכון פיתיונות"""
        update_message = {
            "type": "honeypot_network_update",
            "update_type": honeypot_data.get("update_type", "signature"),
            "honeypot_type": honeypot_data.get("honeypot_type"),
            "new_signatures": honeypot_data.get("signatures", []),
            "recommended_actions": honeypot_data.get("actions", []),
            "priority": honeypot_data.get("priority", "normal")
        }
        
        await self.broadcast_to_all(update_message)
        
        self.logger.info(
            f"🍯 Honeypot update broadcasted: "
            f"{honeypot_data.get('update_type', 'unknown')}"
        )
    
    async def broadcast_statistics_update(self, stats_data: Dict):
        """שידור עדכון סטטיסטיקות"""
        stats_message = {
            "type": "global_statistics_update",
            "data": stats_data,
            "network_size": len(self.connections)
        }
        
        await self.broadcast_to_all(stats_message)
        
        self.logger.debug(f"📊 Statistics update broadcasted to network")
    
    async def broadcast_network_update(self, network_data: Dict, exclude_client: Optional[str] = None):
        """שידור עדכון רשת"""
        network_message = {
            "type": "network_status_update",
            **network_data
        }
        
        await self.broadcast_to_all(network_message, exclude_client=exclude_client)
    
    async def update_client_heartbeat(self, client_id: str):
        """עדכון heartbeat של לקוח"""
        if client_id in self.connections:
            self.connections[client_id].last_heartbeat = datetime.now()
    
    async def update_client_stats(self, client_id: str, stat_type: str, increment: int = 1):
        """עדכון סטטיסטיקות לקוח"""
        if client_id not in self.connections:
            return
        
        connection = self.connections[client_id]
        
        if stat_type == "threat_reports":
            connection.threat_reports += increment
        elif stat_type == "honeypot_triggers":
            connection.honeypot_triggers += increment
            connection.points += increment * 50  # 50 points per trigger
        elif stat_type == "points":
            connection.points += increment
    
    async def get_client_info(self, client_id: str) -> Optional[Dict]:
        """קבלת מידע על לקוח"""
        if client_id not in self.connections:
            return None
        
        connection = self.connections[client_id]
        
        return {
            "client_id": client_id,
            "platform": connection.platform,
            "connected_at": connection.connected_at.isoformat(),
            "last_heartbeat": connection.last_heartbeat.isoformat(),
            "threat_reports": connection.threat_reports,
            "honeypot_triggers": connection.honeypot_triggers,
            "points": connection.points,
            "location": connection.location,
            "version": connection.version,
            "uptime_seconds": (datetime.now() - connection.connected_at).total_seconds()
        }
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 10) -> int:
        """ניקוי חיבורים לא פעילים"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        inactive_clients = []
        
        for client_id, connection in self.connections.items():
            if connection.last_heartbeat < cutoff_time:
                inactive_clients.append(client_id)
        
        # Remove inactive clients
        for client_id in inactive_clients:
            await self.unregister_client(client_id)
        
        if inactive_clients:
            self.logger.info(f"🧹 Cleaned up {len(inactive_clients)} inactive connections")
        
        return len(inactive_clients)
    
    async def disconnect_all(self):
        """ניתוק כל הלקוחות"""
        self.logger.info(f"🔌 Disconnecting all {len(self.connections)} clients...")
        
        disconnect_tasks = []
        for client_id, connection in list(self.connections.items()):
            try:
                await connection.websocket.close()
            except Exception as e:
                self.logger.error(f"Error closing connection {client_id}: {e}")
        
        # Clear all connections
        self.connections.clear()
        self.websockets.clear()
        self.mobile_clients.clear()
        self.desktop_clients.clear()
        self.server_clients.clear()
        
        self.logger.info("✅ All clients disconnected")
    
    def get_connection_count(self) -> int:
        """קבלת מספר החיבורים הפעילים"""
        return len(self.connections)
    
    def get_platform_stats(self) -> Dict:
        """קבלת סטטיסטיקות לפי פלטפורמה"""
        return {
            "total_connections": len(self.connections),
            "mobile_clients": len(self.mobile_clients),
            "desktop_clients": len(self.desktop_clients),
            "server_clients": len(self.server_clients),
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "total_lifetime_connections": self.total_connections
        }
    
    def get_top_contributors(self, limit: int = 10) -> List[Dict]:
        """קבלת התורמים המובילים"""
        sorted_clients = sorted(
            self.connections.values(),
            key=lambda c: c.points,
            reverse=True
        )
        
        return [
            {
                "client_id": client.client_id,
                "platform": client.platform,
                "points": client.points,
                "threat_reports": client.threat_reports,
                "honeypot_triggers": client.honeypot_triggers,
                "connected_at": client.connected_at.isoformat()
            }
            for client in sorted_clients[:limit]
        ]
