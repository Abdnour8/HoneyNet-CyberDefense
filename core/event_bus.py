"""
HoneyNet Event-Driven Architecture
מערכת אירועים מתקדמת לתיאום בין רכיבי המערכת
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import weakref
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

from .memory_manager import memory_manager


class EventPriority(Enum):
    """עדיפויות אירועים"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EventType(Enum):
    """סוגי אירועים במערכת"""
    # Threat events
    THREAT_DETECTED = "threat_detected"
    THREAT_BLOCKED = "threat_blocked"
    THREAT_ANALYZED = "threat_analyzed"
    
    # Honeypot events
    HONEYPOT_TRIGGERED = "honeypot_triggered"
    HONEYPOT_CREATED = "honeypot_created"
    HONEYPOT_UPDATED = "honeypot_updated"
    
    # System events
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    
    # User events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"
    
    # Analytics events
    ANALYTICS_DATA = "analytics_data"
    PERFORMANCE_METRIC = "performance_metric"
    
    # Swarm events
    SWARM_AGENT_CREATED = "swarm_agent_created"
    SWARM_AGENT_REMOVED = "swarm_agent_removed"
    SWARM_COORDINATION = "swarm_coordination"
    
    # Blockchain events
    BLOCKCHAIN_TRANSACTION = "blockchain_transaction"
    BLOCKCHAIN_BLOCK_MINED = "blockchain_block_mined"
    
    # Custom events
    CUSTOM = "custom"


@dataclass
class Event:
    """אירוע במערכת"""
    event_id: str
    event_type: EventType
    priority: EventPriority
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        """המרה למילון"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """יצירה ממילון"""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            priority=EventPriority(data["priority"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            data=data["data"],
            metadata=data.get("metadata", {}),
            correlation_id=data.get("correlation_id"),
            retry_count=data.get("retry_count", 0)
        )


@dataclass
class EventHandler:
    """מטפל באירועים"""
    handler_id: str
    event_types: Set[EventType]
    handler_func: Callable
    priority: int = 0
    async_handler: bool = True
    max_concurrent: int = 10
    timeout_seconds: float = 30.0
    
    # Statistics
    total_handled: int = 0
    total_errors: int = 0
    avg_processing_time: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)


class EventQueue:
    """תור אירועים מתקדם עם עדיפויות"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.queues = {
            EventPriority.EMERGENCY: deque(),
            EventPriority.CRITICAL: deque(),
            EventPriority.HIGH: deque(),
            EventPriority.NORMAL: deque(),
            EventPriority.LOW: deque()
        }
        self.lock = asyncio.Lock()
        self.not_empty = asyncio.Condition(self.lock)
        self.total_events = 0
        self.dropped_events = 0
    
    async def put(self, event: Event) -> bool:
        """הוספת אירוע לתור"""
        async with self.not_empty:
            if self.total_events >= self.max_size:
                # הסרת אירוע בעדיפות נמוכה אם התור מלא
                if self._remove_low_priority_event():
                    self.dropped_events += 1
                else:
                    return False  # התור מלא באירועים בעדיפות גבוהה
            
            self.queues[event.priority].append(event)
            self.total_events += 1
            self.not_empty.notify()
            return True
    
    async def get(self) -> Optional[Event]:
        """קבלת אירוע מהתור לפי עדיפות"""
        async with self.not_empty:
            while self.total_events == 0:
                await self.not_empty.wait()
            
            # חיפוש אירוע בעדיפות הגבוהה ביותר
            for priority in [EventPriority.EMERGENCY, EventPriority.CRITICAL, 
                           EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW]:
                if self.queues[priority]:
                    event = self.queues[priority].popleft()
                    self.total_events -= 1
                    return event
            
            return None
    
    def _remove_low_priority_event(self) -> bool:
        """הסרת אירוע בעדיפות נמוכה"""
        for priority in [EventPriority.LOW, EventPriority.NORMAL]:
            if self.queues[priority]:
                self.queues[priority].popleft()
                self.total_events -= 1
                return True
        return False
    
    def get_stats(self) -> Dict:
        """קבלת סטטיסטיקות התור"""
        return {
            "total_events": self.total_events,
            "dropped_events": self.dropped_events,
            "queue_sizes": {
                priority.name: len(queue) 
                for priority, queue in self.queues.items()
            },
            "utilization": self.total_events / self.max_size
        }


class EventBus:
    """מערכת אירועים מרכזית"""
    
    def __init__(self, max_queue_size: int = 10000, max_workers: int = 20):
        self.logger = logging.getLogger(__name__)
        
        # Event queue and processing
        self.event_queue = EventQueue(max_queue_size)
        self.max_workers = max_workers
        self.workers_active = 0
        
        # Event handlers
        self.handlers: Dict[str, EventHandler] = {}
        self.event_type_handlers: Dict[EventType, List[str]] = defaultdict(list)
        
        # Event processing
        self.processing_active = False
        self.worker_semaphore = asyncio.Semaphore(max_workers)
        
        # Statistics and monitoring
        self.stats = {
            "total_events_published": 0,
            "total_events_processed": 0,
            "total_events_failed": 0,
            "total_handlers_registered": 0,
            "avg_processing_time": 0.0,
            "events_per_second": 0.0
        }
        
        # Event history for debugging
        self.event_history: deque = deque(maxlen=1000)
        self.failed_events: deque = deque(maxlen=100)
        
        # Correlation tracking
        self.correlation_chains: Dict[str, List[str]] = defaultdict(list)
        
        self.logger.info("🚌 Event Bus initialized")
    
    async def start(self):
        """התחלת מערכת האירועים"""
        if self.processing_active:
            return
        
        self.processing_active = True
        
        # התחלת worker processes
        for i in range(self.max_workers):
            await memory_manager.task_manager.create_task(
                self._event_worker(f"worker_{i}"),
                f"event_worker_{i}"
            )
        
        # התחלת ניטור ביצועים
        await memory_manager.task_manager.create_task(
            self._performance_monitor(),
            "event_bus_monitor"
        )
        
        # פרסום אירוע התחלה
        await self.publish(Event(
            event_id=f"system_start_{int(time.time())}",
            event_type=EventType.SYSTEM_STARTED,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="event_bus",
            data={"message": "Event Bus started"}
        ))
        
        self.logger.info("🚀 Event Bus started with {} workers".format(self.max_workers))
    
    async def stop(self):
        """עצירת מערכת האירועים"""
        if not self.processing_active:
            return
        
        self.processing_active = False
        
        # פרסום אירוע עצירה
        await self.publish(Event(
            event_id=f"system_stop_{int(time.time())}",
            event_type=EventType.SYSTEM_STOPPED,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="event_bus",
            data={"message": "Event Bus stopping"}
        ))
        
        # המתנה לסיום עיבוד אירועים נוכחיים
        while self.workers_active > 0:
            await asyncio.sleep(0.1)
        
        self.logger.info("🛑 Event Bus stopped")
    
    def register_handler(self, 
                        handler_id: str,
                        event_types: List[EventType],
                        handler_func: Callable,
                        priority: int = 0,
                        async_handler: bool = True,
                        max_concurrent: int = 10,
                        timeout_seconds: float = 30.0) -> bool:
        """רישום מטפל אירועים"""
        
        if handler_id in self.handlers:
            self.logger.warning(f"Handler {handler_id} already registered")
            return False
        
        handler = EventHandler(
            handler_id=handler_id,
            event_types=set(event_types),
            handler_func=handler_func,
            priority=priority,
            async_handler=async_handler,
            max_concurrent=max_concurrent,
            timeout_seconds=timeout_seconds
        )
        
        self.handlers[handler_id] = handler
        
        # הוספה למפה של סוגי אירועים
        for event_type in event_types:
            self.event_type_handlers[event_type].append(handler_id)
            # מיון לפי עדיפות
            self.event_type_handlers[event_type].sort(
                key=lambda h_id: self.handlers[h_id].priority,
                reverse=True
            )
        
        self.stats["total_handlers_registered"] += 1
        
        self.logger.info(f"📝 Registered handler {handler_id} for {len(event_types)} event types")
        return True
    
    def unregister_handler(self, handler_id: str) -> bool:
        """ביטול רישום מטפל אירועים"""
        if handler_id not in self.handlers:
            return False
        
        handler = self.handlers[handler_id]
        
        # הסרה ממפת סוגי אירועים
        for event_type in handler.event_types:
            if handler_id in self.event_type_handlers[event_type]:
                self.event_type_handlers[event_type].remove(handler_id)
        
        del self.handlers[handler_id]
        self.stats["total_handlers_registered"] -= 1
        
        self.logger.info(f"🗑️ Unregistered handler {handler_id}")
        return True
    
    async def publish(self, event: Event) -> bool:
        """פרסום אירוע"""
        # הוספת metadata
        event.metadata.update({
            "published_at": datetime.now().isoformat(),
            "bus_instance": id(self)
        })
        
        # הוספה לתור
        success = await self.event_queue.put(event)
        
        if success:
            self.stats["total_events_published"] += 1
            self.event_history.append(event.to_dict())
            
            # מעקב אחר correlation chains
            if event.correlation_id:
                self.correlation_chains[event.correlation_id].append(event.event_id)
            
            self.logger.debug(f"📤 Published event {event.event_id} ({event.event_type.value})")
        else:
            self.logger.warning(f"❌ Failed to publish event {event.event_id} - queue full")
        
        return success
    
    async def publish_and_wait(self, event: Event, timeout: float = 30.0) -> List[Any]:
        """פרסום אירוע והמתנה לתוצאות"""
        # יצירת correlation ID ייחודי
        if not event.correlation_id:
            event.correlation_id = f"sync_{event.event_id}_{int(time.time())}"
        
        # יצירת Future לתוצאות
        result_future = asyncio.Future()
        correlation_id = event.correlation_id
        
        # רישום מטפל זמני לתוצאות
        async def result_handler(result_event: Event):
            if not result_future.done():
                result_future.set_result(result_event.data.get("results", []))
        
        temp_handler_id = f"temp_result_{correlation_id}"
        self.register_handler(
            temp_handler_id,
            [EventType.CUSTOM],  # מטפל כללי
            result_handler,
            priority=100  # עדיפות גבוהה
        )
        
        try:
            # פרסום האירוע
            await self.publish(event)
            
            # המתנה לתוצאות
            results = await asyncio.wait_for(result_future, timeout=timeout)
            return results
            
        except asyncio.TimeoutError:
            self.logger.warning(f"⏰ Timeout waiting for event {event.event_id} results")
            return []
        finally:
            # ניקוי המטפל הזמני
            self.unregister_handler(temp_handler_id)
    
    async def _event_worker(self, worker_id: str):
        """Worker לעיבוד אירועים"""
        self.logger.debug(f"🔧 Event worker {worker_id} started")
        
        while self.processing_active:
            try:
                # קבלת אירוע מהתור
                event = await self.event_queue.get()
                if not event:
                    await asyncio.sleep(0.1)
                    continue
                
                self.workers_active += 1
                
                # עיבוד האירוע
                await self._process_event(event, worker_id)
                
            except Exception as e:
                self.logger.error(f"Error in event worker {worker_id}: {e}")
            finally:
                self.workers_active -= 1
        
        self.logger.debug(f"🔧 Event worker {worker_id} stopped")
    
    async def _process_event(self, event: Event, worker_id: str):
        """עיבוד אירוע יחיד"""
        start_time = time.time()
        
        try:
            # חיפוש מטפלים מתאימים
            handler_ids = self.event_type_handlers.get(event.event_type, [])
            
            if not handler_ids:
                self.logger.debug(f"No handlers for event type {event.event_type.value}")
                return
            
            # עיבוד על ידי כל המטפלים
            tasks = []
            for handler_id in handler_ids:
                if handler_id in self.handlers:
                    handler = self.handlers[handler_id]
                    
                    # בדיקת מגבלת concurrency
                    async with asyncio.Semaphore(handler.max_concurrent):
                        task = self._execute_handler(handler, event, worker_id)
                        tasks.append(task)
            
            # המתנה לסיום כל המטפלים
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            processing_time = time.time() - start_time
            
            # עדכון סטטיסטיקות
            self.stats["total_events_processed"] += 1
            
            # עדכון זמן עיבוד ממוצע
            current_avg = self.stats["avg_processing_time"]
            total_processed = self.stats["total_events_processed"]
            self.stats["avg_processing_time"] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
            
            self.logger.debug(f"✅ Processed event {event.event_id} in {processing_time:.3f}s")
            
        except Exception as e:
            self.stats["total_events_failed"] += 1
            self.failed_events.append({
                "event": event.to_dict(),
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "worker_id": worker_id
            })
            
            self.logger.error(f"❌ Failed to process event {event.event_id}: {e}")
            
            # ניסיון חוזר אם מוגדר
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                await asyncio.sleep(2 ** event.retry_count)  # Exponential backoff
                await self.event_queue.put(event)
    
    async def _execute_handler(self, handler: EventHandler, event: Event, worker_id: str):
        """ביצוע מטפל אירועים"""
        start_time = time.time()
        
        try:
            if handler.async_handler:
                # מטפל אסינכרוני
                result = await asyncio.wait_for(
                    handler.handler_func(event),
                    timeout=handler.timeout_seconds
                )
            else:
                # מטפל סינכרוני - הרצה ב-thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    handler.handler_func,
                    event
                )
            
            # עדכון סטטיסטיקות המטפל
            handler.total_handled += 1
            processing_time = time.time() - start_time
            
            # עדכון זמן עיבוד ממוצע של המטפל
            current_avg = handler.avg_processing_time
            total_handled = handler.total_handled
            handler.avg_processing_time = (
                (current_avg * (total_handled - 1) + processing_time) / total_handled
            )
            handler.last_activity = datetime.now()
            
            self.logger.debug(f"Handler {handler.handler_id} processed event {event.event_id}")
            
        except asyncio.TimeoutError:
            handler.total_errors += 1
            self.logger.warning(f"Handler {handler.handler_id} timed out processing event {event.event_id}")
            
        except Exception as e:
            handler.total_errors += 1
            self.logger.error(f"Handler {handler.handler_id} failed processing event {event.event_id}: {e}")
    
    async def _performance_monitor(self):
        """ניטור ביצועי מערכת האירועים"""
        last_processed = 0
        
        while self.processing_active:
            try:
                await asyncio.sleep(60)  # כל דקה
                
                # חישוב אירועים לשנייה
                current_processed = self.stats["total_events_processed"]
                events_per_minute = current_processed - last_processed
                self.stats["events_per_second"] = events_per_minute / 60.0
                last_processed = current_processed
                
                # דיווח על ביצועים
                queue_stats = self.event_queue.get_stats()
                self.logger.info(
                    f"📊 Event Bus Performance: "
                    f"{self.stats['events_per_second']:.1f} events/sec, "
                    f"{queue_stats['total_events']} queued, "
                    f"{self.workers_active} active workers"
                )
                
                # ניקוי היסטוריה ישנה
                cutoff_time = datetime.now() - timedelta(hours=1)
                old_correlations = [
                    corr_id for corr_id, events in self.correlation_chains.items()
                    if len(events) == 0
                ]
                for corr_id in old_correlations:
                    del self.correlation_chains[corr_id]
                
            except Exception as e:
                self.logger.error(f"Performance monitor error: {e}")
    
    def get_stats(self) -> Dict:
        """קבלת סטטיסטיקות מערכת האירועים"""
        queue_stats = self.event_queue.get_stats()
        
        handler_stats = {}
        for handler_id, handler in self.handlers.items():
            handler_stats[handler_id] = {
                "total_handled": handler.total_handled,
                "total_errors": handler.total_errors,
                "avg_processing_time": handler.avg_processing_time,
                "error_rate": handler.total_errors / max(handler.total_handled, 1),
                "last_activity": handler.last_activity.isoformat() if handler.last_activity else None
            }
        
        return {
            "general_stats": self.stats,
            "queue_stats": queue_stats,
            "handler_stats": handler_stats,
            "active_workers": self.workers_active,
            "processing_active": self.processing_active,
            "correlation_chains": len(self.correlation_chains),
            "recent_failures": len(self.failed_events)
        }
    
    async def get_event_history(self, limit: int = 100) -> List[Dict]:
        """קבלת היסטוריית אירועים"""
        return list(self.event_history)[-limit:]
    
    async def get_failed_events(self, limit: int = 50) -> List[Dict]:
        """קבלת אירועים שנכשלו"""
        return list(self.failed_events)[-limit:]


# Global event bus instance
event_bus = EventBus()
