"""
HoneyNet Trap Detector
גלאי מלכודות ופיתיונות
"""

import os
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import logging


@dataclass
class TrapEvent:
    """אירוע הפעלת מלכודת"""
    timestamp: datetime
    trap_type: str
    file_path: str
    access_type: str  # read, write, delete, modify
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    process_name: Optional[str] = None
    threat_level: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "trap_type": self.trap_type,
            "file_path": self.file_path,
            "access_type": self.access_type,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "process_name": self.process_name,
            "threat_level": self.threat_level
        }


class TrapDetector:
    """גלאי מלכודות לזיהוי גישה לפיתיונות"""
    
    def __init__(self):
        self.monitored_files = {}  # file_path -> file_info
        self.trap_events = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def add_trap_file(self, file_path: str, trap_type: str, sensitivity: str = "high") -> bool:
        """הוספת קובץ פיתיון לניטור"""
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"Trap file does not exist: {file_path}")
                return False
            
            # Get initial file stats
            stat = os.stat(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            self.monitored_files[file_path] = {
                "trap_type": trap_type,
                "sensitivity": sensitivity,
                "initial_mtime": stat.st_mtime,
                "initial_size": stat.st_size,
                "initial_hash": file_hash,
                "last_check": time.time(),
                "access_count": 0,
                "created": datetime.now().isoformat()
            }
            
            self.logger.info(f"Added trap file: {file_path} (type: {trap_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding trap file {file_path}: {e}")
            return False
    
    def remove_trap_file(self, file_path: str) -> bool:
        """הסרת קובץ פיתיון מהניטור"""
        if file_path in self.monitored_files:
            del self.monitored_files[file_path]
            self.logger.info(f"Removed trap file: {file_path}")
            return True
        return False
    
    def start_monitoring(self, check_interval: float = 1.0):
        """התחלת ניטור הפיתיונות"""
        if self.is_monitoring:
            self.logger.warning("Monitoring is already active")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(check_interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Started trap monitoring")
    
    def stop_monitoring(self):
        """עצירת ניטור הפיתיונות"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Stopped trap monitoring")
    
    def _monitor_loop(self, check_interval: float):
        """לולאת ניטור רציפה"""
        while self.is_monitoring:
            try:
                self._check_all_traps()
                time.sleep(check_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)
    
    def _check_all_traps(self):
        """בדיקת כל הפיתיונות"""
        current_time = time.time()
        
        for file_path, file_info in self.monitored_files.items():
            try:
                if not os.path.exists(file_path):
                    # File was deleted - this is suspicious!
                    event = TrapEvent(
                        timestamp=datetime.now(),
                        trap_type=file_info["trap_type"],
                        file_path=file_path,
                        access_type="delete",
                        threat_level="high"
                    )
                    self._trigger_trap(event)
                    continue
                
                # Check file modifications
                stat = os.stat(file_path)
                
                # Check if file was modified
                if stat.st_mtime > file_info["initial_mtime"]:
                    # File was modified
                    new_hash = self._calculate_file_hash(file_path)
                    
                    if new_hash != file_info["initial_hash"]:
                        event = TrapEvent(
                            timestamp=datetime.now(),
                            trap_type=file_info["trap_type"],
                            file_path=file_path,
                            access_type="modify",
                            threat_level="high"
                        )
                        self._trigger_trap(event)
                        
                        # Update file info
                        file_info["initial_mtime"] = stat.st_mtime
                        file_info["initial_hash"] = new_hash
                
                # Check if file size changed
                if stat.st_size != file_info["initial_size"]:
                    event = TrapEvent(
                        timestamp=datetime.now(),
                        trap_type=file_info["trap_type"],
                        file_path=file_path,
                        access_type="resize",
                        threat_level="medium"
                    )
                    self._trigger_trap(event)
                    file_info["initial_size"] = stat.st_size
                
                # Check access time (if supported by filesystem)
                if hasattr(stat, 'st_atime'):
                    if stat.st_atime > file_info["last_check"]:
                        event = TrapEvent(
                            timestamp=datetime.now(),
                            trap_type=file_info["trap_type"],
                            file_path=file_path,
                            access_type="read",
                            threat_level="medium"
                        )
                        self._trigger_trap(event)
                        file_info["access_count"] += 1
                
                file_info["last_check"] = current_time
                
            except Exception as e:
                self.logger.error(f"Error checking trap {file_path}: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """חישוב hash של קובץ"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _trigger_trap(self, event: TrapEvent):
        """הפעלת מלכודת כאשר מזוהה גישה חשודה"""
        self.trap_events.append(event)
        
        # Log the event
        self.logger.warning(
            f"TRAP TRIGGERED! Type: {event.trap_type}, "
            f"File: {event.file_path}, Action: {event.access_type}, "
            f"Threat Level: {event.threat_level}"
        )
        
        # Call registered callbacks
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Error in trap callback: {e}")
    
    def add_callback(self, callback_func):
        """הוספת callback שיופעל כאשר מלכודת מופעלת"""
        self.callbacks.append(callback_func)
    
    def get_trap_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """קבלת רשימת אירועי מלכודות"""
        events = self.trap_events[-limit:] if limit else self.trap_events
        return [event.to_dict() for event in events]
    
    def get_trap_statistics(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות מלכודות"""
        total_events = len(self.trap_events)
        
        # Count events by type
        event_types = {}
        threat_levels = {}
        
        for event in self.trap_events:
            event_types[event.access_type] = event_types.get(event.access_type, 0) + 1
            threat_levels[event.threat_level] = threat_levels.get(event.threat_level, 0) + 1
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_events = [
            event for event in self.trap_events 
            if event.timestamp > recent_cutoff
        ]
        
        return {
            "total_monitored_files": len(self.monitored_files),
            "total_events": total_events,
            "recent_events_24h": len(recent_events),
            "event_types": event_types,
            "threat_levels": threat_levels,
            "monitoring_active": self.is_monitoring,
            "last_check": datetime.now().isoformat()
        }
    
    def simulate_trap_trigger(self, file_path: str, access_type: str = "read") -> bool:
        """סימולציה של הפעלת מלכודת (לצורכי בדיקה)"""
        if file_path not in self.monitored_files:
            return False
        
        file_info = self.monitored_files[file_path]
        event = TrapEvent(
            timestamp=datetime.now(),
            trap_type=file_info["trap_type"],
            file_path=file_path,
            access_type=access_type,
            threat_level="medium",
            source_ip="192.168.1.100",  # Simulated IP
            process_name="suspicious_process.exe"
        )
        
        self._trigger_trap(event)
        return True
    
    def export_events_to_json(self, file_path: str) -> bool:
        """יצוא אירועי מלכודות לקובץ JSON"""
        try:
            events_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_events": len(self.trap_events),
                "events": self.get_trap_events(),
                "statistics": self.get_trap_statistics()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(self.trap_events)} events to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting events: {e}")
            return False
    
    def clear_events(self):
        """ניקוי כל אירועי המלכודות"""
        cleared_count = len(self.trap_events)
        self.trap_events.clear()
        self.logger.info(f"Cleared {cleared_count} trap events")
        return cleared_count


# Factory function for easy import
def create_trap_detector() -> TrapDetector:
    """יצירת גלאי מלכודות"""
    return TrapDetector()
