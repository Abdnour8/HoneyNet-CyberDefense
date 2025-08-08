"""
HoneyNet API Monetization System
מערכת מונטיזציה מתקדמת עבור API
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import secrets
from collections import defaultdict, deque

from .memory_manager import memory_manager
from .event_bus import event_bus, Event, EventType, EventPriority
from .database_optimizer import db_optimizer


class SubscriptionTier(Enum):
    """רמות מנוי"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class APIEndpointType(Enum):
    """סוגי נקודות קצה של API"""
    THREAT_DETECTION = "threat_detection"
    HONEYPOT_MANAGEMENT = "honeypot_management"
    ANALYTICS = "analytics"
    REPORTING = "reporting"
    REAL_TIME_MONITORING = "real_time_monitoring"
    THREAT_INTELLIGENCE = "threat_intelligence"
    CUSTOM_INTEGRATION = "custom_integration"


@dataclass
class APIQuota:
    """מכסת API"""
    requests_per_hour: int
    requests_per_day: int
    requests_per_month: int
    concurrent_connections: int
    data_retention_days: int
    premium_features: List[str] = field(default_factory=list)
    rate_limit_burst: int = 10


@dataclass
class SubscriptionPlan:
    """תוכנית מנוי"""
    tier: SubscriptionTier
    name: str
    description: str
    monthly_price: float
    annual_price: float
    quotas: APIQuota
    features: List[str]
    support_level: str
    sla_uptime: float  # Percentage
    custom_integrations: bool = False
    white_label: bool = False
    dedicated_support: bool = False


@dataclass
class APIUsage:
    """שימוש ב-API"""
    user_id: str
    endpoint: str
    endpoint_type: APIEndpointType
    timestamp: datetime
    response_time_ms: float
    status_code: int
    request_size_bytes: int
    response_size_bytes: int
    ip_address: str
    user_agent: str


@dataclass
class UserSubscription:
    """מנוי משתמש"""
    user_id: str
    subscription_id: str
    tier: SubscriptionTier
    plan: SubscriptionPlan
    start_date: datetime
    end_date: datetime
    is_active: bool
    auto_renew: bool
    payment_method: str
    current_usage: Dict[str, int] = field(default_factory=dict)
    overage_charges: float = 0.0


class RateLimiter:
    """מגביל קצב בקשות מתקדם"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_buckets: Dict[str, Dict] = defaultdict(dict)
        self.cleanup_interval = 300  # 5 minutes
        
    async def check_rate_limit(self, user_id: str, quota: APIQuota, endpoint_type: str) -> Tuple[bool, Dict]:
        """בדיקת מגבלת קצב"""
        current_time = time.time()
        
        # Initialize user bucket if not exists
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = {
                'hourly': {'count': 0, 'reset_time': current_time + 3600},
                'daily': {'count': 0, 'reset_time': current_time + 86400},
                'monthly': {'count': 0, 'reset_time': current_time + 2592000},
                'burst': {'count': 0, 'reset_time': current_time + 60}  # 1 minute burst window
            }
        
        bucket = self.user_buckets[user_id]
        
        # Reset counters if time windows have passed
        for period in ['hourly', 'daily', 'monthly', 'burst']:
            if current_time >= bucket[period]['reset_time']:
                if period == 'hourly':
                    bucket[period] = {'count': 0, 'reset_time': current_time + 3600}
                elif period == 'daily':
                    bucket[period] = {'count': 0, 'reset_time': current_time + 86400}
                elif period == 'monthly':
                    bucket[period] = {'count': 0, 'reset_time': current_time + 2592000}
                elif period == 'burst':
                    bucket[period] = {'count': 0, 'reset_time': current_time + 60}
        
        # Check limits
        limits_info = {
            'hourly_remaining': max(0, quota.requests_per_hour - bucket['hourly']['count']),
            'daily_remaining': max(0, quota.requests_per_day - bucket['daily']['count']),
            'monthly_remaining': max(0, quota.requests_per_month - bucket['monthly']['count']),
            'burst_remaining': max(0, quota.rate_limit_burst - bucket['burst']['count']),
            'reset_times': {
                'hourly': bucket['hourly']['reset_time'],
                'daily': bucket['daily']['reset_time'],
                'monthly': bucket['monthly']['reset_time'],
                'burst': bucket['burst']['reset_time']
            }
        }
        
        # Check if any limit is exceeded
        if (bucket['hourly']['count'] >= quota.requests_per_hour or
            bucket['daily']['count'] >= quota.requests_per_day or
            bucket['monthly']['count'] >= quota.requests_per_month or
            bucket['burst']['count'] >= quota.rate_limit_burst):
            
            return False, limits_info
        
        # Increment counters
        for period in ['hourly', 'daily', 'monthly', 'burst']:
            bucket[period]['count'] += 1
        
        return True, limits_info
    
    async def cleanup_old_buckets(self):
        """ניקוי buckets ישנים"""
        current_time = time.time()
        users_to_remove = []
        
        for user_id, bucket in self.user_buckets.items():
            # Remove users who haven't made requests in the last 24 hours
            latest_reset = max(
                bucket['hourly']['reset_time'],
                bucket['daily']['reset_time'],
                bucket['monthly']['reset_time']
            )
            
            if current_time > latest_reset + 86400:  # 24 hours after last reset
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.user_buckets[user_id]
        
        if users_to_remove:
            self.logger.debug(f"Cleaned up {len(users_to_remove)} old rate limit buckets")


class UsageTracker:
    """מעקב אחר שימוש ב-API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.usage_buffer: deque = deque(maxlen=10000)
        self.user_usage: Dict[str, Dict] = defaultdict(lambda: defaultdict(int))
        self.flush_interval = 60  # Flush to DB every minute
        
    async def track_usage(self, usage: APIUsage):
        """מעקב אחר שימוש"""
        # Add to buffer
        self.usage_buffer.append(usage)
        
        # Update in-memory counters
        user_id = usage.user_id
        today = datetime.now().date().isoformat()
        hour = datetime.now().hour
        
        self.user_usage[user_id][f"daily_{today}"] += 1
        self.user_usage[user_id][f"hourly_{today}_{hour}"] += 1
        self.user_usage[user_id][f"monthly_{datetime.now().strftime('%Y-%m')}"] += 1
        self.user_usage[user_id]["total"] += 1
        
        # Track by endpoint type
        endpoint_key = f"endpoint_{usage.endpoint_type.value}"
        self.user_usage[user_id][endpoint_key] += 1
    
    async def get_user_usage(self, user_id: str, period: str = "current_month") -> Dict:
        """קבלת נתוני שימוש למשתמש"""
        if period == "current_month":
            month_key = f"monthly_{datetime.now().strftime('%Y-%m')}"
            return {
                "requests_this_month": self.user_usage[user_id].get(month_key, 0),
                "total_requests": self.user_usage[user_id].get("total", 0)
            }
        elif period == "today":
            today_key = f"daily_{datetime.now().date().isoformat()}"
            return {
                "requests_today": self.user_usage[user_id].get(today_key, 0)
            }
        
        return self.user_usage[user_id]
    
    async def flush_to_database(self):
        """שמירת נתוני שימוש לבסיס נתונים"""
        if not self.usage_buffer:
            return
        
        usage_records = []
        while self.usage_buffer:
            usage = self.usage_buffer.popleft()
            usage_records.append((
                usage.user_id,
                usage.endpoint,
                usage.endpoint_type.value,
                usage.timestamp.isoformat(),
                usage.response_time_ms,
                usage.status_code,
                usage.request_size_bytes,
                usage.response_size_bytes,
                usage.ip_address,
                usage.user_agent
            ))
        
        if usage_records:
            try:
                # Batch insert to database
                query = """
                INSERT INTO api_usage 
                (user_id, endpoint, endpoint_type, timestamp, response_time_ms, 
                 status_code, request_size_bytes, response_size_bytes, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                batch_queries = [(query, record) for record in usage_records]
                await db_optimizer.execute_batch(batch_queries)
                
                self.logger.debug(f"Flushed {len(usage_records)} usage records to database")
                
            except Exception as e:
                self.logger.error(f"Failed to flush usage data: {e}")


class APIMonetizationManager:
    """מנהל מונטיזציה של API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.rate_limiter = RateLimiter()
        self.usage_tracker = UsageTracker()
        
        # Subscription plans
        self.subscription_plans = self._initialize_subscription_plans()
        
        # Active subscriptions
        self.active_subscriptions: Dict[str, UserSubscription] = {}
        
        # Pricing and billing
        self.overage_rates = {
            APIEndpointType.THREAT_DETECTION: 0.001,  # $0.001 per request
            APIEndpointType.ANALYTICS: 0.0005,
            APIEndpointType.REAL_TIME_MONITORING: 0.002,
            APIEndpointType.THREAT_INTELLIGENCE: 0.003,
        }
        
        # Statistics
        self.monetization_stats = {
            "total_api_calls": 0,
            "revenue_this_month": 0.0,
            "active_subscriptions": 0,
            "overage_charges": 0.0,
            "top_endpoints": defaultdict(int)
        }
        
        self.logger.info("💰 API Monetization Manager initialized")
    
    def _initialize_subscription_plans(self) -> Dict[SubscriptionTier, SubscriptionPlan]:
        """אתחול תוכניות מנוי"""
        plans = {
            SubscriptionTier.FREE: SubscriptionPlan(
                tier=SubscriptionTier.FREE,
                name="Free Tier",
                description="Basic threat detection for personal use",
                monthly_price=0.0,
                annual_price=0.0,
                quotas=APIQuota(
                    requests_per_hour=100,
                    requests_per_day=1000,
                    requests_per_month=10000,
                    concurrent_connections=2,
                    data_retention_days=7,
                    premium_features=[],
                    rate_limit_burst=5
                ),
                features=["Basic threat detection", "Community support", "7-day data retention"],
                support_level="Community",
                sla_uptime=95.0
            ),
            
            SubscriptionTier.BASIC: SubscriptionPlan(
                tier=SubscriptionTier.BASIC,
                name="Basic Plan",
                description="Enhanced security for small businesses",
                monthly_price=29.99,
                annual_price=299.99,
                quotas=APIQuota(
                    requests_per_hour=1000,
                    requests_per_day=10000,
                    requests_per_month=200000,
                    concurrent_connections=5,
                    data_retention_days=30,
                    premium_features=["advanced_analytics"],
                    rate_limit_burst=20
                ),
                features=["Advanced threat detection", "Email support", "30-day data retention", "Basic analytics"],
                support_level="Email",
                sla_uptime=99.0
            ),
            
            SubscriptionTier.PRO: SubscriptionPlan(
                tier=SubscriptionTier.PRO,
                name="Professional Plan",
                description="Comprehensive security for growing companies",
                monthly_price=99.99,
                annual_price=999.99,
                quotas=APIQuota(
                    requests_per_hour=5000,
                    requests_per_day=50000,
                    requests_per_month=1000000,
                    concurrent_connections=20,
                    data_retention_days=90,
                    premium_features=["advanced_analytics", "real_time_monitoring", "custom_reports"],
                    rate_limit_burst=50
                ),
                features=[
                    "Real-time monitoring", "Priority support", "90-day data retention",
                    "Advanced analytics", "Custom reports", "API webhooks"
                ],
                support_level="Priority",
                sla_uptime=99.5
            ),
            
            SubscriptionTier.ENTERPRISE: SubscriptionPlan(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise Plan",
                description="Enterprise-grade security with unlimited scale",
                monthly_price=499.99,
                annual_price=4999.99,
                quotas=APIQuota(
                    requests_per_hour=50000,
                    requests_per_day=500000,
                    requests_per_month=10000000,
                    concurrent_connections=100,
                    data_retention_days=365,
                    premium_features=[
                        "advanced_analytics", "real_time_monitoring", "custom_reports",
                        "threat_intelligence", "custom_integrations", "white_label"
                    ],
                    rate_limit_burst=200
                ),
                features=[
                    "Unlimited threat intelligence", "24/7 dedicated support", "1-year data retention",
                    "Custom integrations", "White-label options", "SLA guarantees",
                    "On-premise deployment", "Custom training"
                ],
                support_level="Dedicated",
                sla_uptime=99.9,
                custom_integrations=True,
                white_label=True,
                dedicated_support=True
            )
        }
        
        return plans
    
    async def initialize(self):
        """אתחול מנהל המונטיזציה"""
        # Load active subscriptions from database
        await self._load_active_subscriptions()
        
        # Start background tasks
        await memory_manager.task_manager.create_task(
            self._usage_flush_loop(),
            "usage_flush"
        )
        
        await memory_manager.task_manager.create_task(
            self._rate_limit_cleanup_loop(),
            "rate_limit_cleanup"
        )
        
        await memory_manager.task_manager.create_task(
            self._billing_cycle_loop(),
            "billing_cycle"
        )
        
        self.logger.info("API Monetization Manager fully initialized")
    
    async def validate_api_request(self, user_id: str, endpoint: str, endpoint_type: APIEndpointType) -> Tuple[bool, Dict]:
        """אימות בקשת API"""
        # Get user subscription
        if user_id not in self.active_subscriptions:
            return False, {"error": "No active subscription found"}
        
        subscription = self.active_subscriptions[user_id]
        
        # Check if subscription is active
        if not subscription.is_active or datetime.now() > subscription.end_date:
            return False, {"error": "Subscription expired"}
        
        # Check rate limits
        allowed, limits_info = await self.rate_limiter.check_rate_limit(
            user_id, subscription.plan.quotas, endpoint_type.value
        )
        
        if not allowed:
            return False, {
                "error": "Rate limit exceeded",
                "limits": limits_info,
                "upgrade_url": f"/upgrade?from={subscription.tier.value}"
            }
        
        # Check feature access
        if endpoint_type.value in subscription.plan.quotas.premium_features:
            if endpoint_type.value not in subscription.plan.quotas.premium_features:
                return False, {
                    "error": "Feature not available in current plan",
                    "required_tier": "pro",
                    "upgrade_url": f"/upgrade?feature={endpoint_type.value}"
                }
        
        return True, {
            "allowed": True,
            "subscription_tier": subscription.tier.value,
            "limits": limits_info
        }
    
    async def track_api_usage(self, user_id: str, endpoint: str, endpoint_type: APIEndpointType, 
                            response_time_ms: float, status_code: int,
                            request_size: int, response_size: int,
                            ip_address: str, user_agent: str):
        """מעקב אחר שימוש ב-API"""
        
        usage = APIUsage(
            user_id=user_id,
            endpoint=endpoint,
            endpoint_type=endpoint_type,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            status_code=status_code,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        await self.usage_tracker.track_usage(usage)
        
        # Update statistics
        self.monetization_stats["total_api_calls"] += 1
        self.monetization_stats["top_endpoints"][endpoint] += 1
        
        # Check for overage charges
        if user_id in self.active_subscriptions:
            await self._check_overage_charges(user_id, endpoint_type)
    
    async def _check_overage_charges(self, user_id: str, endpoint_type: APIEndpointType):
        """בדיקת חיובים נוספים"""
        subscription = self.active_subscriptions[user_id]
        usage = await self.usage_tracker.get_user_usage(user_id, "current_month")
        
        monthly_requests = usage.get("requests_this_month", 0)
        quota_limit = subscription.plan.quotas.requests_per_month
        
        if monthly_requests > quota_limit:
            overage_requests = monthly_requests - quota_limit
            overage_rate = self.overage_rates.get(endpoint_type, 0.001)
            overage_charge = overage_requests * overage_rate
            
            subscription.overage_charges += overage_charge
            self.monetization_stats["overage_charges"] += overage_charge
            
            # Send overage notification
            await self._send_overage_notification(user_id, overage_charge, overage_requests)
    
    async def _send_overage_notification(self, user_id: str, charge: float, requests: int):
        """שליחת התראה על חיובים נוספים"""
        await event_bus.publish(Event(
            event_id=f"overage_{user_id}_{int(time.time())}",
            event_type=EventType.CUSTOM,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="api_monetization",
            data={
                "type": "overage_notification",
                "user_id": user_id,
                "overage_charge": charge,
                "overage_requests": requests,
                "message": f"You have exceeded your monthly API quota by {requests} requests, resulting in ${charge:.2f} in overage charges."
            }
        ))
    
    async def _load_active_subscriptions(self):
        """טעינת מנויים פעילים מבסיס הנתונים"""
        try:
            query = """
            SELECT user_id, subscription_id, tier, start_date, end_date, 
                   is_active, auto_renew, payment_method, overage_charges
            FROM user_subscriptions 
            WHERE is_active = 1 AND end_date > ?
            """
            
            subscriptions = await db_optimizer.execute_query(
                query, 
                (datetime.now().isoformat(),),
                cache_key="active_subscriptions"
            )
            
            for sub_data in subscriptions:
                tier = SubscriptionTier(sub_data["tier"])
                plan = self.subscription_plans[tier]
                
                subscription = UserSubscription(
                    user_id=sub_data["user_id"],
                    subscription_id=sub_data["subscription_id"],
                    tier=tier,
                    plan=plan,
                    start_date=datetime.fromisoformat(sub_data["start_date"]),
                    end_date=datetime.fromisoformat(sub_data["end_date"]),
                    is_active=bool(sub_data["is_active"]),
                    auto_renew=bool(sub_data["auto_renew"]),
                    payment_method=sub_data["payment_method"],
                    overage_charges=sub_data["overage_charges"]
                )
                
                self.active_subscriptions[sub_data["user_id"]] = subscription
            
            self.monetization_stats["active_subscriptions"] = len(self.active_subscriptions)
            self.logger.info(f"Loaded {len(self.active_subscriptions)} active subscriptions")
            
        except Exception as e:
            self.logger.error(f"Failed to load subscriptions: {e}")
    
    async def _usage_flush_loop(self):
        """לולאת שמירת נתוני שימוש"""
        while True:
            try:
                await self.usage_tracker.flush_to_database()
                await asyncio.sleep(self.usage_tracker.flush_interval)
            except Exception as e:
                self.logger.error(f"Usage flush error: {e}")
                await asyncio.sleep(60)
    
    async def _rate_limit_cleanup_loop(self):
        """לולאת ניקוי מגבלות קצב"""
        while True:
            try:
                await self.rate_limiter.cleanup_old_buckets()
                await asyncio.sleep(self.rate_limiter.cleanup_interval)
            except Exception as e:
                self.logger.error(f"Rate limit cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _billing_cycle_loop(self):
        """לולאת מחזור חיוב"""
        while True:
            try:
                # Process monthly billing
                await self._process_monthly_billing()
                
                # Sleep until next day
                await asyncio.sleep(86400)  # 24 hours
                
            except Exception as e:
                self.logger.error(f"Billing cycle error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _process_monthly_billing(self):
        """עיבוד חיוב חודשי"""
        current_date = datetime.now()
        
        for user_id, subscription in self.active_subscriptions.items():
            # Check if it's billing day
            if (subscription.start_date.day == current_date.day and 
                subscription.auto_renew and 
                subscription.is_active):
                
                # Calculate total charges
                base_charge = subscription.plan.monthly_price
                total_charge = base_charge + subscription.overage_charges
                
                # Process payment (simplified)
                payment_success = await self._process_payment(user_id, total_charge)
                
                if payment_success:
                    # Extend subscription
                    subscription.end_date = subscription.end_date + timedelta(days=30)
                    subscription.overage_charges = 0.0
                    
                    # Update revenue stats
                    self.monetization_stats["revenue_this_month"] += total_charge
                    
                    self.logger.info(f"Processed billing for user {user_id}: ${total_charge}")
                else:
                    # Handle payment failure
                    await self._handle_payment_failure(user_id, subscription)
    
    async def _process_payment(self, user_id: str, amount: float) -> bool:
        """עיבוד תשלום (מופשט)"""
        # In real implementation, would integrate with payment processor
        # For demo, assume success for amounts under $1000
        return amount < 1000.0
    
    async def _handle_payment_failure(self, user_id: str, subscription: UserSubscription):
        """טיפול בכשל תשלום"""
        # Downgrade to free tier
        subscription.tier = SubscriptionTier.FREE
        subscription.plan = self.subscription_plans[SubscriptionTier.FREE]
        subscription.is_active = False
        
        # Send notification
        await event_bus.publish(Event(
            event_id=f"payment_failed_{user_id}_{int(time.time())}",
            event_type=EventType.SYSTEM_WARNING,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="api_monetization",
            data={
                "type": "payment_failure",
                "user_id": user_id,
                "message": "Payment failed. Account downgraded to free tier."
            }
        ))
    
    def get_monetization_stats(self) -> Dict:
        """קבלת סטטיסטיקות מונטיזציה"""
        return {
            "stats": self.monetization_stats,
            "subscription_breakdown": {
                tier.value: len([s for s in self.active_subscriptions.values() if s.tier == tier])
                for tier in SubscriptionTier
            },
            "top_endpoints": dict(self.monetization_stats["top_endpoints"]),
            "average_revenue_per_user": (
                self.monetization_stats["revenue_this_month"] / 
                max(self.monetization_stats["active_subscriptions"], 1)
            )
        }


# Global API monetization manager instance
api_monetization = APIMonetizationManager()
