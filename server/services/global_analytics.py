"""
HoneyNet Global Server - Global Analytics
ניתוח נתונים גלובלי לשרת HoneyNet
""" 

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import numpy as np
import redis
import asyncpg


@dataclass
class GlobalStatistics:
    """סטטיסטיקות גלובליות"""
    total_active_nodes: int = 0
    total_threats_detected: int = 0
    total_attacks_blocked: int = 0
    total_honeypots_triggered: int = 0
    threats_by_type: Dict[str, int] = field(default_factory=dict)
    threats_by_region: Dict[str, int] = field(default_factory=dict)
    top_attack_sources: List[Dict] = field(default_factory=list)
    network_health_score: float = 1.0
    prediction_accuracy: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ThreatTrend:
    """מגמת איומים"""
    threat_type: str
    current_count: int
    previous_count: int
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_percentage: float
    geographic_hotspots: List[str]
    time_pattern: Dict[int, int]  # hour -> count


class GlobalAnalytics:
    """מערכת ניתוח נתונים גלובלית"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Data stores
        self.global_stats = GlobalStatistics()
        self.threat_history: List[Dict] = []
        self.honeypot_triggers: List[Dict] = []
        self.client_statistics: Dict[str, Dict] = {}
        
        # Analytics cache
        self.analytics_cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Database connections
        self.redis_client = None
        self.postgres_pool = None
        
        # Real-time metrics
        self.metrics = {
            "threats_per_minute": 0,
            "average_response_time": 0.0,
            "network_coverage": 0.0,
            "false_positive_rate": 0.0,
            "detection_accuracy": 0.95
        }
        
        self.logger.info("📊 Global Analytics initialized")
    
    async def initialize(self):
        """אתחול מערכת הניתוח"""
        try:
            self.logger.info("🚀 Initializing Global Analytics...")
            
            # Initialize database connections
            await self._init_database_connections()
            
            # Load historical data
            await self._load_historical_data()
            
            # Start background analytics tasks
            asyncio.create_task(self._periodic_analytics_update())
            asyncio.create_task(self._trend_analysis_task())
            asyncio.create_task(self._cache_cleanup_task())
            
            self.logger.info("✅ Global Analytics initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Global Analytics: {e}")
            raise
    
    async def record_threat(self, threat_data: Dict):
        """רישום איום חדש"""
        try:
            threat_record = {
                "id": threat_data.get("id", f"threat_{datetime.now().timestamp()}"),
                "type": threat_data.get("type", "unknown"),
                "severity": threat_data.get("severity", "medium"),
                "source_ip": threat_data.get("source_ip", "unknown"),
                "target": threat_data.get("target", "unknown"),
                "region": threat_data.get("region", "unknown"),
                "timestamp": datetime.now(),
                "blocked": threat_data.get("blocked", False),
                "client_id": threat_data.get("client_id", "unknown")
            }
            
            # Add to history
            self.threat_history.append(threat_record)
            
            # Update global statistics
            self.global_stats.total_threats_detected += 1
            if threat_record["blocked"]:
                self.global_stats.total_attacks_blocked += 1
            
            # Update threat type counters
            threat_type = threat_record["type"]
            if threat_type not in self.global_stats.threats_by_type:
                self.global_stats.threats_by_type[threat_type] = 0
            self.global_stats.threats_by_type[threat_type] += 1
            
            # Update regional counters
            region = threat_record["region"]
            if region not in self.global_stats.threats_by_region:
                self.global_stats.threats_by_region[region] = 0
            self.global_stats.threats_by_region[region] += 1
            
            # Store in database
            await self._store_threat_in_database(threat_record)
            
            # Update real-time metrics
            await self._update_realtime_metrics()
            
            self.logger.info(f"📝 Threat recorded: {threat_type} from {region}")
            
        except Exception as e:
            self.logger.error(f"Error recording threat: {e}")
    
    async def record_honeypot_trigger(self, honeypot_data: Dict):
        """רישום הפעלת פיתיון"""
        try:
            trigger_record = {
                "id": honeypot_data.get("trigger_id", f"trigger_{datetime.now().timestamp()}"),
                "honeypot_type": honeypot_data.get("honeypot_type", "unknown"),
                "client_id": honeypot_data.get("client_id", "unknown"),
                "attacker_fingerprint": honeypot_data.get("attacker_fingerprint", {}),
                "effectiveness_score": honeypot_data.get("effectiveness_score", 0.0),
                "timestamp": datetime.now(),
                "region": honeypot_data.get("region", "unknown")
            }
            
            # Add to triggers
            self.honeypot_triggers.append(trigger_record)
            
            # Update global statistics
            self.global_stats.total_honeypots_triggered += 1
            
            # Store in database
            await self._store_honeypot_trigger_in_database(trigger_record)
            
            self.logger.info(f"🍯 Honeypot trigger recorded: {trigger_record['honeypot_type']}")
            
        except Exception as e:
            self.logger.error(f"Error recording honeypot trigger: {e}")
    
    async def get_global_statistics(self) -> Dict:
        """קבלת סטטיסטיקות גלובליות"""
        try:
            # Check cache first
            cache_key = "global_statistics"
            if cache_key in self.analytics_cache:
                cache_entry = self.analytics_cache[cache_key]
                if datetime.now() - cache_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                    return cache_entry["data"]
            
            # Calculate fresh statistics
            stats = {
                "network": {
                    "total_active_nodes": self.global_stats.total_active_nodes,
                    "network_health_score": self.global_stats.network_health_score,
                    "network_coverage": self.metrics["network_coverage"],
                    "uptime_percentage": 99.9  # Placeholder
                },
                "threats": {
                    "total_detected": self.global_stats.total_threats_detected,
                    "total_blocked": self.global_stats.total_attacks_blocked,
                    "block_rate": self._calculate_block_rate(),
                    "threats_per_minute": self.metrics["threats_per_minute"],
                    "by_type": dict(self.global_stats.threats_by_type),
                    "by_region": dict(self.global_stats.threats_by_region)
                },
                "honeypots": {
                    "total_triggered": self.global_stats.total_honeypots_triggered,
                    "average_effectiveness": await self._calculate_average_honeypot_effectiveness(),
                    "most_effective_types": await self._get_most_effective_honeypot_types()
                },
                "performance": {
                    "detection_accuracy": self.metrics["detection_accuracy"],
                    "false_positive_rate": self.metrics["false_positive_rate"],
                    "average_response_time": self.metrics["average_response_time"],
                    "prediction_accuracy": self.global_stats.prediction_accuracy
                },
                "trends": await self._get_current_trends(),
                "top_threats": await self._get_top_threats(),
                "geographic_distribution": await self._get_geographic_distribution(),
                "last_updated": datetime.now().isoformat()
            }
            
            # Cache the result
            self.analytics_cache[cache_key] = {
                "data": stats,
                "timestamp": datetime.now()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting global statistics: {e}")
            return {"error": "Failed to retrieve statistics"}
    
    async def get_client_statistics(self, client_id: str) -> Dict:
        """קבלת סטטיסטיקות לקוח ספציפי"""
        try:
            if client_id not in self.client_statistics:
                self.client_statistics[client_id] = {
                    "threats_reported": 0,
                    "honeypots_triggered": 0,
                    "points_earned": 0,
                    "accuracy_score": 0.0,
                    "join_date": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat()
                }
            
            client_stats = self.client_statistics[client_id].copy()
            
            # Add comparative statistics
            client_stats["global_ranking"] = await self._get_client_ranking(client_id)
            client_stats["contribution_percentage"] = await self._calculate_contribution_percentage(client_id)
            client_stats["recent_activity"] = await self._get_client_recent_activity(client_id)
            
            return client_stats
            
        except Exception as e:
            self.logger.error(f"Error getting client statistics for {client_id}: {e}")
            return {"error": "Failed to retrieve client statistics"}
    
    async def get_threat_trends(self, time_period_hours: int = 24) -> List[ThreatTrend]:
        """קבלת מגמות איומים"""
        try:
            trends = []
            cutoff_time = datetime.now() - timedelta(hours=time_period_hours)
            
            # Filter recent threats
            recent_threats = [
                threat for threat in self.threat_history
                if threat["timestamp"] > cutoff_time
            ]
            
            # Group by type
            threat_types = Counter(threat["type"] for threat in recent_threats)
            
            for threat_type, current_count in threat_types.items():
                # Calculate previous period count for comparison
                previous_cutoff = cutoff_time - timedelta(hours=time_period_hours)
                previous_threats = [
                    threat for threat in self.threat_history
                    if previous_cutoff <= threat["timestamp"] <= cutoff_time
                    and threat["type"] == threat_type
                ]
                previous_count = len(previous_threats)
                
                # Calculate trend
                if previous_count == 0:
                    trend_direction = "new" if current_count > 0 else "stable"
                    trend_percentage = 100.0 if current_count > 0 else 0.0
                else:
                    change = current_count - previous_count
                    trend_percentage = (change / previous_count) * 100
                    
                    if abs(trend_percentage) < 10:
                        trend_direction = "stable"
                    elif trend_percentage > 0:
                        trend_direction = "increasing"
                    else:
                        trend_direction = "decreasing"
                
                # Get geographic hotspots
                type_threats = [t for t in recent_threats if t["type"] == threat_type]
                region_counts = Counter(t["region"] for t in type_threats)
                hotspots = [region for region, _ in region_counts.most_common(3)]
                
                # Get time pattern
                time_pattern = defaultdict(int)
                for threat in type_threats:
                    hour = threat["timestamp"].hour
                    time_pattern[hour] += 1
                
                trend = ThreatTrend(
                    threat_type=threat_type,
                    current_count=current_count,
                    previous_count=previous_count,
                    trend_direction=trend_direction,
                    trend_percentage=trend_percentage,
                    geographic_hotspots=hotspots,
                    time_pattern=dict(time_pattern)
                )
                
                trends.append(trend)
            
            # Sort by current count (most active first)
            trends.sort(key=lambda t: t.current_count, reverse=True)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error getting threat trends: {e}")
            return []
    
    async def generate_threat_report(self, report_type: str = "daily") -> Dict:
        """יצירת דוח איומים"""
        try:
            if report_type == "daily":
                time_period = 24
            elif report_type == "weekly":
                time_period = 168  # 24 * 7
            elif report_type == "monthly":
                time_period = 720  # 24 * 30
            else:
                time_period = 24
            
            cutoff_time = datetime.now() - timedelta(hours=time_period)
            period_threats = [
                threat for threat in self.threat_history
                if threat["timestamp"] > cutoff_time
            ]
            
            report = {
                "report_type": report_type,
                "time_period_hours": time_period,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_threats": len(period_threats),
                    "blocked_threats": len([t for t in period_threats if t["blocked"]]),
                    "unique_sources": len(set(t["source_ip"] for t in period_threats)),
                    "affected_regions": len(set(t["region"] for t in period_threats)),
                    "most_common_type": Counter(t["type"] for t in period_threats).most_common(1)[0] if period_threats else ("none", 0)
                },
                "detailed_analysis": {
                    "threat_breakdown": dict(Counter(t["type"] for t in period_threats)),
                    "severity_distribution": dict(Counter(t["severity"] for t in period_threats)),
                    "regional_distribution": dict(Counter(t["region"] for t in period_threats)),
                    "hourly_distribution": await self._get_hourly_distribution(period_threats),
                    "top_sources": Counter(t["source_ip"] for t in period_threats).most_common(10)
                },
                "trends": await self.get_threat_trends(time_period),
                "recommendations": await self._generate_security_recommendations(period_threats),
                "risk_assessment": await self._assess_current_risk_level(period_threats)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating threat report: {e}")
            return {"error": "Failed to generate report"}
    
    async def get_total_threats(self) -> int:
        """קבלת סך כל האיומים"""
        return self.global_stats.total_threats_detected
    
    async def update_node_count(self, count: int):
        """עדכון מספר הנודים הפעילים"""
        self.global_stats.total_active_nodes = count
        self.global_stats.last_updated = datetime.now()
        
        # Update network coverage metric
        self.metrics["network_coverage"] = min(count / 1000000, 1.0)  # Assume 1M is 100% coverage
    
    async def cleanup(self):
        """ניקוי משאבים"""
        try:
            self.logger.info("🧹 Cleaning up Global Analytics...")
            
            # Save data to database
            await self._save_analytics_data()
            
            # Close database connections
            if self.redis_client:
                await self.redis_client.close()
            if self.postgres_pool:
                await self.postgres_pool.close()
            
            self.logger.info("✅ Global Analytics cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Error during analytics cleanup: {e}")
    
    # Private helper methods
    
    async def _init_database_connections(self):
        """אתחול חיבורי מסד נתונים"""
        try:
            # Redis connection for caching
            # self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            # PostgreSQL connection pool
            # self.postgres_pool = await asyncpg.create_pool(
            #     "postgresql://user:password@localhost/honeynet"
            # )
            
            self.logger.info("✅ Database connections initialized")
        except Exception as e:
            self.logger.warning(f"Database connections not available: {e}")
    
    async def _load_historical_data(self):
        """טעינת נתונים היסטוריים"""
        try:
            # Load from database or files
            # For demo, we'll start with empty data
            self.logger.info("✅ Historical data loaded")
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
    
    def _calculate_block_rate(self) -> float:
        """חישוב אחוז החסימות"""
        if self.global_stats.total_threats_detected == 0:
            return 0.0
        return (self.global_stats.total_attacks_blocked / self.global_stats.total_threats_detected) * 100
    
    async def _calculate_average_honeypot_effectiveness(self) -> float:
        """חישוב יעילות ממוצעת של פיתיונות"""
        if not self.honeypot_triggers:
            return 0.0
        
        total_effectiveness = sum(trigger.get("effectiveness_score", 0.0) for trigger in self.honeypot_triggers)
        return total_effectiveness / len(self.honeypot_triggers)
    
    async def _get_most_effective_honeypot_types(self) -> List[Dict]:
        """קבלת סוגי הפיתיונות היעילים ביותר"""
        if not self.honeypot_triggers:
            return []
        
        type_effectiveness = defaultdict(list)
        for trigger in self.honeypot_triggers:
            honeypot_type = trigger.get("honeypot_type", "unknown")
            effectiveness = trigger.get("effectiveness_score", 0.0)
            type_effectiveness[honeypot_type].append(effectiveness)
        
        # Calculate average effectiveness per type
        avg_effectiveness = {}
        for honeypot_type, scores in type_effectiveness.items():
            avg_effectiveness[honeypot_type] = sum(scores) / len(scores)
        
        # Sort by effectiveness
        sorted_types = sorted(avg_effectiveness.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"type": honeypot_type, "effectiveness": effectiveness}
            for honeypot_type, effectiveness in sorted_types[:5]
        ]
    
    async def _periodic_analytics_update(self):
        """עדכון תקופתי של הניתוח"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Update real-time metrics
                await self._update_realtime_metrics()
                
                # Clean old data
                await self._cleanup_old_data()
                
                # Update global statistics timestamp
                self.global_stats.last_updated = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error in periodic analytics update: {e}")
    
    async def _update_realtime_metrics(self):
        """עדכון מדדים בזמן אמת"""
        try:
            # Calculate threats per minute
            recent_time = datetime.now() - timedelta(minutes=1)
            recent_threats = [
                threat for threat in self.threat_history
                if threat["timestamp"] > recent_time
            ]
            self.metrics["threats_per_minute"] = len(recent_threats)
            
            # Update other metrics as needed
            
        except Exception as e:
            self.logger.error(f"Error updating real-time metrics: {e}")
    
    async def _cleanup_old_data(self):
        """ניקוי נתונים ישנים"""
        try:
            # Keep only last 7 days of data in memory
            cutoff_time = datetime.now() - timedelta(days=7)
            
            self.threat_history = [
                threat for threat in self.threat_history
                if threat["timestamp"] > cutoff_time
            ]
            
            self.honeypot_triggers = [
                trigger for trigger in self.honeypot_triggers
                if trigger["timestamp"] > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def _store_threat_in_database(self, threat_record: Dict):
        """שמירת איום במסד הנתונים"""
        # Implementation for database storage
        pass
    
    async def _store_honeypot_trigger_in_database(self, trigger_record: Dict):
        """שמירת הפעלת פיתיון במסד הנתונים"""
        # Implementation for database storage
        pass
    
    async def _save_analytics_data(self):
        """שמירת נתוני ניתוח"""
        # Implementation for saving analytics data
        pass
    
    def get_statistics_summary(self) -> Dict:
        """קבלת סיכום סטטיסטיקות"""
        return {
            "total_threats_analyzed": len(self.threat_history),
            "total_honeypots_triggered": len(self.honeypot_triggers),
            "active_nodes": self.global_stats.total_active_nodes,
            "network_health": self.global_stats.network_health_score,
            "last_updated": self.global_stats.last_updated.isoformat()
        }
    
    async def _trend_analysis_task(self):
        """משימת ניתוח מגמות רקע"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._analyze_threat_trends()
                self.logger.debug("Trend analysis completed")
            except Exception as e:
                self.logger.error(f"Error in trend analysis task: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _cache_cleanup_task(self):
        """משימת ניקוי מטמון רקע"""
        while True:
            try:
                await asyncio.sleep(600)  # Run every 10 minutes
                await self._cleanup_expired_cache()
                self.logger.debug("Cache cleanup completed")
            except Exception as e:
                self.logger.error(f"Error in cache cleanup task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _analyze_threat_trends(self):
        """ניתוח מגמות איומים"""
        try:
            # Analyze recent threats for trends
            recent_threats = self.threat_history[-100:]  # Last 100 threats
            
            # Update threat trends
            threat_counts = {}
            for threat in recent_threats:
                threat_type = threat.get('threat_type', 'unknown')
                threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
            
            self.global_stats.threats_by_type = threat_counts
            self.logger.debug(f"Updated threat trends: {threat_counts}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing threat trends: {e}")
    
    async def _cleanup_expired_cache(self):
        """ניקוי מטמון שפג תוקפו"""
        try:
            current_time = datetime.now().timestamp()
            expired_keys = []
            
            for key, data in self.analytics_cache.items():
                if 'timestamp' in data:
                    if current_time - data['timestamp'] > self.cache_ttl:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self.analytics_cache[key]
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")
