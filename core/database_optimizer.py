"""
HoneyNet Database Optimizer
מנהל בסיס נתונים מתקדם עם אופטימיזציה של ביצועים
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import sqlite3
import aiosqlite
from contextlib import asynccontextmanager
import threading
from concurrent.futures import ThreadPoolExecutor
import weakref
from collections import defaultdict

from .memory_manager import memory_manager


@dataclass
class QueryStats:
    """סטטיסטיקות שאילתות"""
    query_hash: str
    execution_count: int
    total_time: float
    avg_time: float
    last_executed: datetime
    query_text: str


@dataclass
class ConnectionStats:
    """סטטיסטיקות חיבורים"""
    total_connections: int
    active_connections: int
    idle_connections: int
    failed_connections: int
    avg_connection_time: float


class QueryCache:
    """מטמון שאילתות חכם"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.lock = threading.Lock()
    
    def get(self, query_hash: str) -> Optional[Any]:
        """קבלת תוצאה מהמטמון"""
        with self.lock:
            if query_hash in self.cache:
                result, timestamp = self.cache[query_hash]
                
                # בדיקת תוקף
                if (datetime.now() - timestamp).total_seconds() < self.ttl_seconds:
                    self.access_times[query_hash] = datetime.now()
                    return result
                else:
                    # הסרת תוצאה שפגה תוקפה
                    del self.cache[query_hash]
                    if query_hash in self.access_times:
                        del self.access_times[query_hash]
        
        return None
    
    def set(self, query_hash: str, result: Any):
        """שמירת תוצאה במטמון"""
        with self.lock:
            current_time = datetime.now()
            
            # הסרת פריטים ישנים אם המטמון מלא
            if len(self.cache) >= self.max_size:
                self._evict_old_entries()
            
            self.cache[query_hash] = (result, current_time)
            self.access_times[query_hash] = current_time
    
    def _evict_old_entries(self):
        """הסרת פריטים ישנים מהמטמון"""
        # הסרת 25% מהפריטים הישנים ביותר
        evict_count = self.max_size // 4
        
        # מיון לפי זמן גישה אחרון
        sorted_items = sorted(
            self.access_times.items(),
            key=lambda x: x[1]
        )
        
        for query_hash, _ in sorted_items[:evict_count]:
            if query_hash in self.cache:
                del self.cache[query_hash]
            if query_hash in self.access_times:
                del self.access_times[query_hash]
    
    def clear(self):
        """ניקוי המטמון"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_stats(self) -> Dict:
        """קבלת סטטיסטיקות המטמון"""
        with self.lock:
            return {
                "cache_size": len(self.cache),
                "max_size": self.max_size,
                "hit_ratio": 0.0,  # יחושב בדרגה גבוהה יותר
                "oldest_entry": min(self.access_times.values()) if self.access_times else None,
                "newest_entry": max(self.access_times.values()) if self.access_times else None
            }


class ConnectionPool:
    """מאגר חיבורים לבסיס נתונים"""
    
    def __init__(self, database_path: str, min_connections: int = 5, max_connections: int = 20):
        self.database_path = database_path
        self.min_connections = min_connections
        self.max_connections = max_connections
        
        self.available_connections: List[aiosqlite.Connection] = []
        self.active_connections: weakref.WeakSet = weakref.WeakSet()
        self.connection_stats = ConnectionStats(0, 0, 0, 0, 0.0)
        
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        
        # סטטיסטיקות ביצועים
        self.total_requests = 0
        self.total_wait_time = 0.0
    
    async def initialize(self):
        """אתחול מאגר החיבורים"""
        async with self.lock:
            for _ in range(self.min_connections):
                try:
                    conn = await aiosqlite.connect(self.database_path)
                    await conn.execute("PRAGMA journal_mode=WAL")  # אופטימיזציה לביצועים
                    await conn.execute("PRAGMA synchronous=NORMAL")
                    await conn.execute("PRAGMA cache_size=10000")
                    await conn.execute("PRAGMA temp_store=MEMORY")
                    
                    self.available_connections.append(conn)
                    self.connection_stats.total_connections += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to create database connection: {e}")
                    self.connection_stats.failed_connections += 1
        
        self.logger.info(f"Database connection pool initialized with {len(self.available_connections)} connections")
    
    @asynccontextmanager
    async def get_connection(self):
        """קבלת חיבור מהמאגר"""
        start_time = time.time()
        connection = None
        
        try:
            async with self.lock:
                self.total_requests += 1
                
                # נסיון לקבל חיבור זמין
                if self.available_connections:
                    connection = self.available_connections.pop()
                    self.connection_stats.idle_connections = len(self.available_connections)
                
                # יצירת חיבור חדש אם אין זמינים ולא הגענו למקסימום
                elif len(self.active_connections) < self.max_connections:
                    try:
                        connection = await aiosqlite.connect(self.database_path)
                        await connection.execute("PRAGMA journal_mode=WAL")
                        await connection.execute("PRAGMA synchronous=NORMAL")
                        
                        self.connection_stats.total_connections += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to create new connection: {e}")
                        self.connection_stats.failed_connections += 1
                        raise
            
            # אם אין חיבור זמין, נחכה
            if connection is None:
                await asyncio.sleep(0.1)  # המתנה קצרה
                async with self.lock:
                    if self.available_connections:
                        connection = self.available_connections.pop()
                    else:
                        raise Exception("No database connections available")
            
            # הוספה לחיבורים פעילים
            self.active_connections.add(connection)
            self.connection_stats.active_connections = len(self.active_connections)
            
            wait_time = time.time() - start_time
            self.total_wait_time += wait_time
            
            yield connection
            
        finally:
            if connection:
                # החזרת החיבור למאגר
                async with self.lock:
                    if len(self.available_connections) < self.max_connections:
                        self.available_connections.append(connection)
                    else:
                        await connection.close()
                        self.connection_stats.total_connections -= 1
                    
                    self.connection_stats.idle_connections = len(self.available_connections)
                    self.connection_stats.active_connections = len(self.active_connections)
    
    async def close_all(self):
        """סגירת כל החיבורים"""
        async with self.lock:
            for conn in self.available_connections:
                await conn.close()
            
            self.available_connections.clear()
            self.connection_stats = ConnectionStats(0, 0, 0, 0, 0.0)
            
        self.logger.info("All database connections closed")
    
    def get_stats(self) -> ConnectionStats:
        """קבלת סטטיסטיקות החיבורים"""
        avg_wait_time = self.total_wait_time / self.total_requests if self.total_requests > 0 else 0.0
        
        return ConnectionStats(
            total_connections=self.connection_stats.total_connections,
            active_connections=len(self.active_connections),
            idle_connections=len(self.available_connections),
            failed_connections=self.connection_stats.failed_connections,
            avg_connection_time=avg_wait_time
        )


class DatabaseOptimizer:
    """מנהל בסיס נתונים מתקדם עם אופטימיזציות"""
    
    def __init__(self, database_path: str = "honeynet.db"):
        self.database_path = database_path
        self.logger = logging.getLogger(__name__)
        
        # מאגר חיבורים
        self.connection_pool = ConnectionPool(database_path, min_connections=5, max_connections=20)
        
        # מטמון שאילתות
        self.query_cache = QueryCache(max_size=1000, ttl_seconds=300)
        
        # סטטיסטיקות שאילתות
        self.query_stats: Dict[str, QueryStats] = {}
        self.slow_queries: List[Tuple[str, float]] = []
        
        # אופטימיזציות
        self.prepared_statements: Dict[str, str] = {}
        self.index_recommendations: List[str] = []
        
        # ביצועים
        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        self.logger.info("🗄️ Database Optimizer initialized")
    
    async def initialize(self):
        """אתחול מנהל בסיס הנתונים"""
        await self.connection_pool.initialize()
        await self._create_indexes()
        await self._analyze_database()
        
        # התחלת ניטור ביצועים
        await memory_manager.task_manager.create_task(
            self._performance_monitoring_loop(),
            "db_performance_monitor"
        )
        
        self.logger.info("Database optimizer fully initialized")
    
    async def execute_query(self, query: str, params: tuple = (), cache_key: Optional[str] = None) -> List[Dict]:
        """ביצוע שאילתה עם אופטימיזציות"""
        start_time = time.time()
        query_hash = self._hash_query(query, params)
        
        # בדיקת מטמון
        if cache_key:
            cached_result = self.query_cache.get(cache_key)
            if cached_result is not None:
                self.cache_hits += 1
                self._update_query_stats(query_hash, query, time.time() - start_time)
                return cached_result
            else:
                self.cache_misses += 1
        
        # ביצוע השאילתה
        async with self.connection_pool.get_connection() as conn:
            try:
                cursor = await conn.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    rows = await cursor.fetchall()
                    # המרה לרשימת מילונים
                    columns = [description[0] for description in cursor.description]
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    await conn.commit()
                    result = [{"affected_rows": cursor.rowcount}]
                
                # שמירה במטמון אם נדרש
                if cache_key and query.strip().upper().startswith('SELECT'):
                    self.query_cache.set(cache_key, result)
                
                execution_time = time.time() - start_time
                self._update_query_stats(query_hash, query, execution_time)
                
                # זיהוי שאילתות איטיות
                if execution_time > 1.0:  # יותר משנייה
                    self.slow_queries.append((query, execution_time))
                    if len(self.slow_queries) > 100:
                        self.slow_queries = self.slow_queries[-50:]
                
                self.total_queries += 1
                return result
                
            except Exception as e:
                self.logger.error(f"Database query failed: {e}")
                self.logger.error(f"Query: {query}")
                self.logger.error(f"Params: {params}")
                raise
    
    async def execute_batch(self, queries: List[Tuple[str, tuple]]) -> List[Any]:
        """ביצוע מספר שאילתות בבאצ'"""
        results = []
        
        async with self.connection_pool.get_connection() as conn:
            try:
                for query, params in queries:
                    cursor = await conn.execute(query, params)
                    
                    if query.strip().upper().startswith('SELECT'):
                        rows = await cursor.fetchall()
                        columns = [description[0] for description in cursor.description]
                        result = [dict(zip(columns, row)) for row in rows]
                    else:
                        result = {"affected_rows": cursor.rowcount}
                    
                    results.append(result)
                
                await conn.commit()
                return results
                
            except Exception as e:
                self.logger.error(f"Batch execution failed: {e}")
                raise
    
    async def _create_indexes(self):
        """יצירת אינדקסים לאופטימיזציה"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_threats_source_ip ON threats(source_ip)",
            "CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(attack_type)",
            "CREATE INDEX IF NOT EXISTS idx_honeypots_triggered ON honeypots(triggered_at)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_session_id ON analytics_events(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity)",
            "CREATE INDEX IF NOT EXISTS idx_blockchain_timestamp ON blockchain_ledger(timestamp)"
        ]
        
        for index_query in indexes:
            try:
                await self.execute_query(index_query)
                self.logger.debug(f"Created index: {index_query}")
            except Exception as e:
                self.logger.warning(f"Failed to create index: {e}")
    
    async def _analyze_database(self):
        """ניתוח בסיס הנתונים לאופטימיזציות"""
        try:
            # ניתוח גודל טבלאות
            table_stats = await self.execute_query("""
                SELECT name, 
                       (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as row_count
                FROM sqlite_master m WHERE type='table'
            """)
            
            for table in table_stats:
                if table['row_count'] > 10000:
                    self.index_recommendations.append(f"Consider partitioning table {table['name']}")
            
            # בדיקת שאילתות איטיות פוטנציאליות
            await self.execute_query("ANALYZE")
            
            self.logger.info("Database analysis completed")
            
        except Exception as e:
            self.logger.error(f"Database analysis failed: {e}")
    
    def _hash_query(self, query: str, params: tuple) -> str:
        """יצירת hash לשאילתה"""
        import hashlib
        query_string = f"{query}:{str(params)}"
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def _update_query_stats(self, query_hash: str, query: str, execution_time: float):
        """עדכון סטטיסטיקות שאילתה"""
        if query_hash in self.query_stats:
            stats = self.query_stats[query_hash]
            stats.execution_count += 1
            stats.total_time += execution_time
            stats.avg_time = stats.total_time / stats.execution_count
            stats.last_executed = datetime.now()
        else:
            self.query_stats[query_hash] = QueryStats(
                query_hash=query_hash,
                execution_count=1,
                total_time=execution_time,
                avg_time=execution_time,
                last_executed=datetime.now(),
                query_text=query[:200]  # שמירת 200 תווים ראשונים
            )
    
    async def _performance_monitoring_loop(self):
        """לולאת ניטור ביצועים"""
        while True:
            try:
                # ניקוי סטטיסטיקות ישנות
                cutoff_time = datetime.now() - timedelta(hours=24)
                old_stats = [
                    query_hash for query_hash, stats in self.query_stats.items()
                    if stats.last_executed < cutoff_time
                ]
                
                for query_hash in old_stats:
                    del self.query_stats[query_hash]
                
                # ניקוי מטמון
                if len(self.query_cache.cache) > self.query_cache.max_size * 0.8:
                    self.query_cache._evict_old_entries()
                
                # דיווח על ביצועים
                if self.total_queries > 0:
                    cache_hit_ratio = self.cache_hits / (self.cache_hits + self.cache_misses)
                    self.logger.info(f"DB Performance: {self.total_queries} queries, {cache_hit_ratio:.2%} cache hit ratio")
                
                await asyncio.sleep(300)  # כל 5 דקות
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def get_performance_stats(self) -> Dict:
        """קבלת סטטיסטיקות ביצועים"""
        connection_stats = self.connection_pool.get_stats()
        cache_stats = self.query_cache.get_stats()
        
        # חישוב cache hit ratio
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_ratio = self.cache_hits / total_cache_requests if total_cache_requests > 0 else 0.0
        cache_stats["hit_ratio"] = cache_hit_ratio
        
        # שאילתות איטיות ביותר
        slowest_queries = sorted(
            [(stats.query_text, stats.avg_time) for stats in self.query_stats.values()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_queries": self.total_queries,
            "cache_stats": cache_stats,
            "connection_stats": {
                "total_connections": connection_stats.total_connections,
                "active_connections": connection_stats.active_connections,
                "idle_connections": connection_stats.idle_connections,
                "failed_connections": connection_stats.failed_connections,
                "avg_connection_time": connection_stats.avg_connection_time
            },
            "query_stats": {
                "total_unique_queries": len(self.query_stats),
                "slowest_queries": slowest_queries,
                "slow_query_count": len(self.slow_queries)
            },
            "optimization_recommendations": self.index_recommendations
        }
    
    async def cleanup(self):
        """ניקוי משאבים"""
        await self.connection_pool.close_all()
        self.query_cache.clear()
        self.logger.info("Database optimizer cleaned up")


# Global database optimizer instance
db_optimizer = DatabaseOptimizer()
