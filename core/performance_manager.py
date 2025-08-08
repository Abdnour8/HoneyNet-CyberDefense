"""
HoneyNet Performance Manager
מנהל ביצועים ואופטימיזציה של המערכת
"""

import psutil
import asyncio
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import gc
import weakref


class MemoryManager:
    """מנהל זיכרון חכם"""
    
    def __init__(self, max_memory_mb: int = 2048):
        self.max_memory_mb = max_memory_mb
        self.logger = logging.getLogger(__name__)
        self.memory_threshold = 0.8  # 80% of max memory
        
    def get_available_memory_mb(self) -> int:
        """קבלת זיכרון זמין במערכת"""
        memory = psutil.virtual_memory()
        available_mb = memory.available // (1024 * 1024)
        return min(available_mb, self.max_memory_mb)
    
    def get_current_usage_mb(self) -> int:
        """קבלת צריכת זיכרון נוכחית של התהליך"""
        process = psutil.Process()
        return process.memory_info().rss // (1024 * 1024)
    
    def should_limit_resources(self) -> bool:
        """בדיקה האם צריך להגביל משאבים"""
        current_usage = self.get_current_usage_mb()
        return current_usage > (self.max_memory_mb * self.memory_threshold)
    
    def calculate_max_agents(self) -> int:
        """חישוב מספר מקסימלי של agents לפי זיכרון זמין"""
        available_memory = self.get_available_memory_mb()
        # הערכה: כל agent צורך בערך 1MB
        estimated_agents = available_memory // 1
        
        # הגבלה בין 100 ל-10,000
        return max(100, min(10000, estimated_agents))
    
    def cleanup_memory(self):
        """ניקוי זיכרון"""
        gc.collect()
        self.logger.info(f"🧹 Memory cleanup completed. Current usage: {self.get_current_usage_mb()}MB")


class ConnectionPool:
    """מאגר חיבורים לבסיס נתונים"""
    
    def __init__(self, max_connections: int = 20):
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_semaphore = asyncio.Semaphore(max_connections)
        self.logger = logging.getLogger(__name__)
        
    async def acquire_connection(self):
        """השגת חיבור מהמאגר"""
        await self.connection_semaphore.acquire()
        self.active_connections += 1
        self.logger.debug(f"Connection acquired. Active: {self.active_connections}")
        
    def release_connection(self):
        """שחרור חיבור למאגר"""
        self.connection_semaphore.release()
        self.active_connections = max(0, self.active_connections - 1)
        self.logger.debug(f"Connection released. Active: {self.active_connections}")
        
    def get_stats(self) -> Dict[str, int]:
        """קבלת סטטיסטיקות חיבורים"""
        return {
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "available_connections": self.max_connections - self.active_connections
        }


class TaskScheduler:
    """מתזמן משימות מתקדם"""
    
    def __init__(self, max_concurrent_tasks: int = 100):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.active_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.logger = logging.getLogger(__name__)
        
    async def execute_task(self, task_func, *args, **kwargs):
        """ביצוע משימה עם הגבלת concurrency"""
        async with self.task_semaphore:
            self.active_tasks += 1
            try:
                result = await task_func(*args, **kwargs)
                self.completed_tasks += 1
                return result
            except Exception as e:
                self.failed_tasks += 1
                self.logger.error(f"Task failed: {e}")
                raise
            finally:
                self.active_tasks = max(0, self.active_tasks - 1)
    
    def get_stats(self) -> Dict[str, int]:
        """קבלת סטטיסטיקות משימות"""
        return {
            "max_concurrent": self.max_concurrent_tasks,
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": (self.completed_tasks / max(1, self.completed_tasks + self.failed_tasks)) * 100
        }


class CacheManager:
    """מנהל cache מתקדם"""
    
    def __init__(self, max_cache_size: int = 1000, ttl_seconds: int = 300):
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.logger = logging.getLogger(__name__)
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_entries())
        
    def get(self, key: str) -> Optional[Any]:
        """קבלת ערך מהcache"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                self.access_times[key] = datetime.now()
                return entry["value"]
            else:
                # Expired entry
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        return None
    
    def set(self, key: str, value: Any):
        """שמירת ערך בcache"""
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_cache_size:
            self._evict_oldest()
        
        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now()
        }
        self.access_times[key] = datetime.now()
    
    def _evict_oldest(self):
        """הסרת הערכים הישנים ביותר"""
        if not self.access_times:
            return
        
        # Find oldest accessed key
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        if oldest_key in self.cache:
            del self.cache[oldest_key]
        del self.access_times[oldest_key]
        
        self.logger.debug(f"Evicted cache entry: {oldest_key}")
    
    async def _cleanup_expired_entries(self):
        """ניקוי ערכים שפג תוקפם"""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                for key, entry in self.cache.items():
                    if current_time - entry["timestamp"] > timedelta(seconds=self.ttl_seconds):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]
                
                if expired_keys:
                    self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(60)  # Cleanup every minute
                
            except Exception as e:
                self.logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(60)
    
    def get_stats(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות cache"""
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "cache_usage_percent": (len(self.cache) / self.max_cache_size) * 100,
            "ttl_seconds": self.ttl_seconds
        }


class PerformanceMonitor:
    """מוניטור ביצועים"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "requests_per_second": 0,
            "average_response_time": 0.0,
            "memory_usage_mb": 0,
            "cpu_usage_percent": 0.0,
            "active_connections": 0,
            "cache_hit_rate": 0.0
        }
        self.request_times = []
        self.start_time = datetime.now()
        
        # Start monitoring task
        asyncio.create_task(self._monitor_system_resources())
    
    def record_request(self, response_time: float):
        """רישום זמן תגובה של בקשה"""
        self.request_times.append({
            "timestamp": datetime.now(),
            "response_time": response_time
        })
        
        # Keep only last 1000 requests
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    async def _monitor_system_resources(self):
        """ניטור משאבי מערכת"""
        while True:
            try:
                # CPU usage
                self.metrics["cpu_usage_percent"] = psutil.cpu_percent(interval=1)
                
                # Memory usage
                process = psutil.Process()
                self.metrics["memory_usage_mb"] = process.memory_info().rss // (1024 * 1024)
                
                # Calculate requests per second
                recent_requests = [
                    r for r in self.request_times 
                    if datetime.now() - r["timestamp"] < timedelta(seconds=60)
                ]
                self.metrics["requests_per_second"] = len(recent_requests) / 60
                
                # Calculate average response time
                if recent_requests:
                    self.metrics["average_response_time"] = sum(
                        r["response_time"] for r in recent_requests
                    ) / len(recent_requests)
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(5)
    
    def get_metrics(self) -> Dict[str, Any]:
        """קבלת מדדי ביצועים"""
        uptime = datetime.now() - self.start_time
        
        return {
            **self.metrics,
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": len(self.request_times)
        }
    
    def should_alert(self) -> Dict[str, bool]:
        """בדיקת תנאי התראה"""
        alerts = {}
        
        # Memory alert (>90% of 2GB)
        alerts["high_memory"] = self.metrics["memory_usage_mb"] > 1843  # 90% of 2GB
        
        # CPU alert (>80%)
        alerts["high_cpu"] = self.metrics["cpu_usage_percent"] > 80
        
        # Slow response time alert (>500ms)
        alerts["slow_response"] = self.metrics["average_response_time"] > 0.5
        
        # Low requests per second (might indicate issues)
        alerts["low_throughput"] = self.metrics["requests_per_second"] < 1
        
        return alerts


class PerformanceManager:
    """מנהל ביצועים ראשי"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.memory_manager = MemoryManager(
            max_memory_mb=self.config.get("max_memory_mb", 2048)
        )
        self.connection_pool = ConnectionPool(
            max_connections=self.config.get("max_connections", 20)
        )
        self.task_scheduler = TaskScheduler(
            max_concurrent_tasks=self.config.get("max_concurrent_tasks", 100)
        )
        self.cache_manager = CacheManager(
            max_cache_size=self.config.get("max_cache_size", 1000),
            ttl_seconds=self.config.get("cache_ttl_seconds", 300)
        )
        self.performance_monitor = PerformanceMonitor()
        
        self.logger.info("🚀 Performance Manager initialized")
    
    async def optimize_system(self):
        """אופטימיזציה כללית של המערכת"""
        self.logger.info("🔧 Starting system optimization...")
        
        # Memory optimization
        if self.memory_manager.should_limit_resources():
            self.memory_manager.cleanup_memory()
        
        # Check for alerts
        alerts = self.performance_monitor.should_alert()
        active_alerts = [alert for alert, active in alerts.items() if active]
        
        if active_alerts:
            self.logger.warning(f"⚠️ Performance alerts: {', '.join(active_alerts)}")
        
        self.logger.info("✅ System optimization completed")
    
    def get_system_status(self) -> Dict[str, Any]:
        """קבלת סטטוס מערכת מלא"""
        return {
            "memory": {
                "current_usage_mb": self.memory_manager.get_current_usage_mb(),
                "max_memory_mb": self.memory_manager.max_memory_mb,
                "available_mb": self.memory_manager.get_available_memory_mb(),
                "max_agents": self.memory_manager.calculate_max_agents()
            },
            "connections": self.connection_pool.get_stats(),
            "tasks": self.task_scheduler.get_stats(),
            "cache": self.cache_manager.get_stats(),
            "performance": self.performance_monitor.get_metrics(),
            "alerts": self.performance_monitor.should_alert()
        }


# Global performance manager instance
_performance_manager = None

def get_performance_manager(config: Dict[str, Any] = None) -> PerformanceManager:
    """קבלת instance של מנהל הביצועים"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = PerformanceManager(config)
    return _performance_manager
