"""
HoneyNet Memory Manager
מנהל זיכרון מתקדם לאופטימיזציה של ביצועים
"""

import asyncio
import psutil
import logging
import gc
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import weakref
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor


@dataclass
class MemoryStats:
    """סטטיסטיקות זיכרון"""
    total_memory: int
    available_memory: int
    used_memory: int
    memory_percent: float
    swap_memory: int
    timestamp: datetime


@dataclass
class ResourceLimit:
    """הגבלות משאבים"""
    max_memory_mb: int
    max_cpu_percent: float
    max_threads: int
    max_async_tasks: int


class MemoryPool:
    """מאגר זיכרון לאובייקטים נפוצים"""
    
    def __init__(self, object_factory: Callable, initial_size: int = 10, max_size: int = 100):
        self.object_factory = object_factory
        self.pool = []
        self.max_size = max_size
        self.lock = threading.Lock()
        
        # יצירת אובייקטים ראשוניים
        for _ in range(initial_size):
            self.pool.append(object_factory())
    
    def get_object(self):
        """קבלת אובייקט מהמאגר"""
        with self.lock:
            if self.pool:
                return self.pool.pop()
            else:
                return self.object_factory()
    
    def return_object(self, obj):
        """החזרת אובייקט למאגר"""
        with self.lock:
            if len(self.pool) < self.max_size:
                # איפוס האובייקט לפני החזרה למאגר
                if hasattr(obj, 'reset'):
                    obj.reset()
                self.pool.append(obj)


class AsyncTaskManager:
    """מנהל משימות אסינכרוניות מתקדם"""
    
    def __init__(self, max_concurrent_tasks: int = 100):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_stats = {
            'total_created': 0,
            'total_completed': 0,
            'total_failed': 0,
            'currently_running': 0
        }
        self.logger = logging.getLogger(__name__)
    
    async def create_task(self, coro, task_id: Optional[str] = None, priority: int = 0):
        """יצירת משימה עם ניהול משאבים"""
        if task_id is None:
            task_id = f"task_{self.task_stats['total_created']}"
        
        async def managed_task():
            async with self.semaphore:
                self.task_stats['currently_running'] += 1
                try:
                    result = await coro
                    self.task_stats['total_completed'] += 1
                    return result
                except Exception as e:
                    self.task_stats['total_failed'] += 1
                    self.logger.error(f"Task {task_id} failed: {e}")
                    raise
                finally:
                    self.task_stats['currently_running'] -= 1
                    if task_id in self.active_tasks:
                        del self.active_tasks[task_id]
        
        task = asyncio.create_task(managed_task())
        self.active_tasks[task_id] = task
        self.task_stats['total_created'] += 1
        
        return task
    
    async def cancel_all_tasks(self):
        """ביטול כל המשימות הפעילות"""
        for task_id, task in list(self.active_tasks.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.active_tasks.clear()
    
    def get_stats(self) -> Dict:
        """קבלת סטטיסטיקות משימות"""
        return {
            **self.task_stats,
            'active_tasks': list(self.active_tasks.keys())
        }


class MemoryManager:
    """מנהל זיכרון מרכזי למערכת HoneyNet"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_pools: Dict[str, MemoryPool] = {}
        self.task_manager = AsyncTaskManager()
        self.resource_limits = ResourceLimit(
            max_memory_mb=2048,  # 2GB מקסימום
            max_cpu_percent=80.0,
            max_threads=50,
            max_async_tasks=100
        )
        
        # ניטור זיכרון
        self.memory_history: List[MemoryStats] = []
        self.monitoring_active = False
        self.cleanup_interval = 300  # 5 דקות
        
        # Thread pool לעיבוד כבד
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
        self.logger.info("🧠 Memory Manager initialized")
    
    def get_memory_stats(self) -> MemoryStats:
        """קבלת סטטיסטיקות זיכרון נוכחיות"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return MemoryStats(
            total_memory=memory.total,
            available_memory=memory.available,
            used_memory=memory.used,
            memory_percent=memory.percent,
            swap_memory=swap.used,
            timestamp=datetime.now()
        )
    
    def calculate_dynamic_limits(self) -> ResourceLimit:
        """חישוב הגבלות דינמיות לפי זיכרון זמין"""
        stats = self.get_memory_stats()
        available_mb = stats.available_memory // (1024 * 1024)
        
        # התאמת הגבלות לפי זיכרון זמין
        max_memory = min(self.resource_limits.max_memory_mb, available_mb * 0.7)
        max_tasks = int(max_memory / 10)  # 10MB לכל משימה בממוצע
        
        return ResourceLimit(
            max_memory_mb=int(max_memory),
            max_cpu_percent=self.resource_limits.max_cpu_percent,
            max_threads=min(self.resource_limits.max_threads, max_tasks // 2),
            max_async_tasks=min(self.resource_limits.max_async_tasks, max_tasks)
        )
    
    def create_memory_pool(self, name: str, factory: Callable, initial_size: int = 10, max_size: int = 100):
        """יצירת מאגר זיכרון חדש"""
        self.memory_pools[name] = MemoryPool(factory, initial_size, max_size)
        self.logger.info(f"Created memory pool '{name}' with {initial_size} initial objects")
    
    def get_from_pool(self, pool_name: str):
        """קבלת אובייקט ממאגר זיכרון"""
        if pool_name in self.memory_pools:
            return self.memory_pools[pool_name].get_object()
        else:
            raise ValueError(f"Memory pool '{pool_name}' not found")
    
    def return_to_pool(self, pool_name: str, obj):
        """החזרת אובייקט למאגר זיכרון"""
        if pool_name in self.memory_pools:
            self.memory_pools[pool_name].return_object(obj)
    
    async def start_monitoring(self):
        """התחלת ניטור זיכרון"""
        self.monitoring_active = True
        
        async def monitor_loop():
            while self.monitoring_active:
                try:
                    # איסוף סטטיסטיקות
                    stats = self.get_memory_stats()
                    self.memory_history.append(stats)
                    
                    # שמירה על היסטוריה מוגבלת
                    if len(self.memory_history) > 1000:
                        self.memory_history = self.memory_history[-500:]
                    
                    # בדיקת צורך בניקוי זיכרון
                    if stats.memory_percent > 85:
                        await self.emergency_cleanup()
                    
                    # ניקוי רגיל
                    if len(self.memory_history) % 10 == 0:
                        await self.routine_cleanup()
                    
                    await asyncio.sleep(30)  # בדיקה כל 30 שניות
                    
                except Exception as e:
                    self.logger.error(f"Memory monitoring error: {e}")
                    await asyncio.sleep(60)
        
        await self.task_manager.create_task(monitor_loop(), "memory_monitor")
        self.logger.info("🔍 Memory monitoring started")
    
    async def stop_monitoring(self):
        """עצירת ניטור זיכרון"""
        self.monitoring_active = False
        await self.task_manager.cancel_all_tasks()
        self.thread_pool.shutdown(wait=True)
        self.logger.info("🛑 Memory monitoring stopped")
    
    async def routine_cleanup(self):
        """ניקוי זיכרון שגרתי"""
        try:
            # הרצת garbage collector
            collected = gc.collect()
            
            # ניקוי היסטוריה ישנה
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.memory_history = [
                stats for stats in self.memory_history 
                if stats.timestamp > cutoff_time
            ]
            
            self.logger.debug(f"Routine cleanup: collected {collected} objects")
            
        except Exception as e:
            self.logger.error(f"Routine cleanup error: {e}")
    
    async def emergency_cleanup(self):
        """ניקוי זיכרון חירום"""
        try:
            self.logger.warning("🚨 Emergency memory cleanup triggered")
            
            # ביטול משימות לא קריטיות
            stats = self.task_manager.get_stats()
            if stats['currently_running'] > 50:
                # ביטול 50% מהמשימות
                tasks_to_cancel = list(self.task_manager.active_tasks.items())[:len(self.task_manager.active_tasks)//2]
                for task_id, task in tasks_to_cancel:
                    task.cancel()
            
            # ניקוי אגרסיבי
            for _ in range(3):
                collected = gc.collect()
                self.logger.info(f"Emergency cleanup collected {collected} objects")
            
            # הפחתת גודל מאגרי זיכרון
            for pool in self.memory_pools.values():
                with pool.lock:
                    if len(pool.pool) > 10:
                        pool.pool = pool.pool[:10]
            
        except Exception as e:
            self.logger.error(f"Emergency cleanup error: {e}")
    
    def get_system_health(self) -> Dict:
        """קבלת מצב בריאות המערכת"""
        stats = self.get_memory_stats()
        limits = self.calculate_dynamic_limits()
        task_stats = self.task_manager.get_stats()
        
        return {
            'memory': {
                'used_percent': stats.memory_percent,
                'available_mb': stats.available_memory // (1024 * 1024),
                'status': 'critical' if stats.memory_percent > 90 else 
                         'warning' if stats.memory_percent > 80 else 'healthy'
            },
            'tasks': {
                'active': task_stats['currently_running'],
                'max_allowed': limits.max_async_tasks,
                'total_completed': task_stats['total_completed'],
                'total_failed': task_stats['total_failed']
            },
            'pools': {
                name: len(pool.pool) for name, pool in self.memory_pools.items()
            },
            'limits': {
                'max_memory_mb': limits.max_memory_mb,
                'max_tasks': limits.max_async_tasks
            }
        }


# Global memory manager instance
memory_manager = MemoryManager()
