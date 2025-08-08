"""
HoneyNet Health Monitor
מוניטור בריאות המערכת למשתמשים אמיתיים
"""

import asyncio
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json


class HealthStatus(Enum):
    """סטטוס בריאות"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """בדיקת בריאות"""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any] = None


class SystemHealthMonitor:
    """מוניטור בריאות המערכת"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.checks_history: List[HealthCheck] = []
        self.max_history = 1000
        
        # Health thresholds
        self.thresholds = {
            "memory_usage_percent": 85,
            "disk_usage_percent": 90,
            "cpu_usage_percent": 80,
            "response_time_ms": 1000,
            "error_rate_percent": 5
        }
    
    async def check_memory_health(self) -> HealthCheck:
        """בדיקת בריאות זיכרון"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            system_usage = memory.percent
            process_usage_mb = process.memory_info().rss // (1024 * 1024)
            
            details = {
                "system_usage_percent": system_usage,
                "process_usage_mb": process_usage_mb,
                "available_mb": memory.available // (1024 * 1024),
                "total_mb": memory.total // (1024 * 1024)
            }
            
            if system_usage > self.thresholds["memory_usage_percent"]:
                status = HealthStatus.CRITICAL
                message = f"High memory usage: {system_usage:.1f}%"
            elif system_usage > self.thresholds["memory_usage_percent"] * 0.8:
                status = HealthStatus.WARNING
                message = f"Moderate memory usage: {system_usage:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {system_usage:.1f}%"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="memory",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="memory",
                status=HealthStatus.CRITICAL,
                message=f"Memory check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )
    
    async def check_disk_health(self) -> HealthCheck:
        """בדיקת בריאות דיסק"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('.')
            usage_percent = (disk.used / disk.total) * 100
            
            details = {
                "usage_percent": usage_percent,
                "used_gb": disk.used // (1024**3),
                "free_gb": disk.free // (1024**3),
                "total_gb": disk.total // (1024**3)
            }
            
            if usage_percent > self.thresholds["disk_usage_percent"]:
                status = HealthStatus.CRITICAL
                message = f"Low disk space: {usage_percent:.1f}% used"
            elif usage_percent > self.thresholds["disk_usage_percent"] * 0.8:
                status = HealthStatus.WARNING
                message = f"Moderate disk usage: {usage_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space normal: {usage_percent:.1f}% used"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="disk",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk",
                status=HealthStatus.CRITICAL,
                message=f"Disk check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )
    
    async def check_cpu_health(self) -> HealthCheck:
        """בדיקת בריאות מעבד"""
        start_time = time.time()
        
        try:
            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            details = {
                "usage_percent": cpu_percent,
                "cpu_count": cpu_count,
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
            
            if cpu_percent > self.thresholds["cpu_usage_percent"]:
                status = HealthStatus.CRITICAL
                message = f"High CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > self.thresholds["cpu_usage_percent"] * 0.8:
                status = HealthStatus.WARNING
                message = f"Moderate CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="cpu",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="cpu",
                status=HealthStatus.CRITICAL,
                message=f"CPU check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )
    
    async def check_network_health(self) -> HealthCheck:
        """בדיקת בריאות רשת"""
        start_time = time.time()
        
        try:
            # Test local connectivity
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get('http://localhost:8000/health') as response:
                        local_status = response.status == 200
                except:
                    local_status = False
                
                # Test internet connectivity
                try:
                    async with session.get('https://httpbin.org/status/200') as response:
                        internet_status = response.status == 200
                except:
                    internet_status = False
            
            details = {
                "local_server": local_status,
                "internet_connectivity": internet_status,
                "network_interfaces": len(psutil.net_if_addrs())
            }
            
            if not local_status and not internet_status:
                status = HealthStatus.CRITICAL
                message = "No network connectivity"
            elif not local_status:
                status = HealthStatus.WARNING
                message = "Local server not accessible"
            elif not internet_status:
                status = HealthStatus.WARNING
                message = "No internet connectivity"
            else:
                status = HealthStatus.HEALTHY
                message = "Network connectivity normal"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="network",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="network",
                status=HealthStatus.CRITICAL,
                message=f"Network check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )
    
    async def check_honeypots_health(self) -> HealthCheck:
        """בדיקת בריאות פיתיונות"""
        start_time = time.time()
        
        try:
            # This would integrate with the actual honeypot manager
            # For now, we'll simulate the check
            
            active_honeypots = 5  # This would come from HoneypotManager
            total_honeypots = 5
            recent_triggers = 0  # This would come from actual data
            
            details = {
                "active_honeypots": active_honeypots,
                "total_honeypots": total_honeypots,
                "recent_triggers": recent_triggers,
                "health_ratio": active_honeypots / max(1, total_honeypots)
            }
            
            health_ratio = active_honeypots / max(1, total_honeypots)
            
            if health_ratio < 0.5:
                status = HealthStatus.CRITICAL
                message = f"Many honeypots inactive: {active_honeypots}/{total_honeypots}"
            elif health_ratio < 0.8:
                status = HealthStatus.WARNING
                message = f"Some honeypots inactive: {active_honeypots}/{total_honeypots}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Honeypots healthy: {active_honeypots}/{total_honeypots} active"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="honeypots",
                status=status,
                message=message,
                response_time_ms=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthCheck(
                name="honeypots",
                status=HealthStatus.CRITICAL,
                message=f"Honeypots check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """הרצת כל בדיקות הבריאות"""
        self.logger.info("🏥 Running system health checks...")
        
        checks = await asyncio.gather(
            self.check_memory_health(),
            self.check_disk_health(),
            self.check_cpu_health(),
            self.check_network_health(),
            self.check_honeypots_health(),
            return_exceptions=True
        )
        
        results = {}
        for check in checks:
            if isinstance(check, HealthCheck):
                results[check.name] = check
                self.checks_history.append(check)
            else:
                # Handle exceptions
                self.logger.error(f"Health check failed: {check}")
        
        # Limit history size
        if len(self.checks_history) > self.max_history:
            self.checks_history = self.checks_history[-self.max_history:]
        
        return results
    
    def get_overall_status(self, checks: Dict[str, HealthCheck]) -> HealthStatus:
        """קבלת סטטוס כללי"""
        if not checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in checks.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """קבלת סיכום בריאות"""
        if not self.checks_history:
            return {"status": "unknown", "message": "No health checks performed yet"}
        
        # Get latest checks for each component
        latest_checks = {}
        for check in reversed(self.checks_history):
            if check.name not in latest_checks:
                latest_checks[check.name] = check
        
        overall_status = self.get_overall_status(latest_checks)
        
        # Calculate average response time
        avg_response_time = sum(check.response_time_ms for check in latest_checks.values()) / len(latest_checks)
        
        # Count issues
        critical_count = sum(1 for check in latest_checks.values() if check.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for check in latest_checks.values() if check.status == HealthStatus.WARNING)
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks_count": len(latest_checks),
            "critical_issues": critical_count,
            "warnings": warning_count,
            "average_response_time_ms": avg_response_time,
            "checks": {
                name: {
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms
                }
                for name, check in latest_checks.items()
            }
        }
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """התחלת ניטור רציף"""
        self.logger.info(f"🔄 Starting health monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                checks = await self.run_all_checks()
                overall_status = self.get_overall_status(checks)
                
                if overall_status == HealthStatus.CRITICAL:
                    self.logger.error("🚨 CRITICAL: System health issues detected!")
                elif overall_status == HealthStatus.WARNING:
                    self.logger.warning("⚠️ WARNING: System health warnings detected")
                else:
                    self.logger.info("✅ System health check completed - all systems healthy")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(interval_seconds)


# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> SystemHealthMonitor:
    """קבלת instance של מוניטור הבריאות"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor()
    return _health_monitor
