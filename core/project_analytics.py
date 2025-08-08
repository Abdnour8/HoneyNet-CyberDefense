"""
Project Analytics System for HoneyNet
Comprehensive analytics for project managers to track usage, locations, performance, and user behavior
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import sqlite3
import aiosqlite
import geoip2.database
import geoip2.errors
from user_agents import parse
import hashlib

@dataclass
class UserSession:
    """User session data"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    country: str
    city: str
    start_time: datetime
    last_activity: datetime
    pages_visited: int
    actions_performed: int
    honeypots_triggered: int
    threats_detected: int

@dataclass
class UsageMetrics:
    """Usage metrics for analytics"""
    total_users: int
    active_users_24h: int
    active_users_7d: int
    active_users_30d: int
    total_sessions: int
    avg_session_duration: float
    total_page_views: int
    total_actions: int
    total_honeypots_triggered: int
    total_threats_detected: int
    top_countries: List[Tuple[str, int]]
    top_cities: List[Tuple[str, int]]
    device_breakdown: Dict[str, int]
    browser_breakdown: Dict[str, int]

class ProjectAnalytics:
    """Main analytics system for project management"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.sessions = {}  # Active sessions
        self.geoip_reader = None
        self._setup_database()
        self._setup_geoip()
    
    def _setup_database(self):
        """Setup analytics database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    total_sessions INTEGER DEFAULT 0,
                    total_actions INTEGER DEFAULT 0,
                    country TEXT,
                    city TEXT,
                    device_type TEXT,
                    browser TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    country TEXT,
                    city TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration INTEGER,
                    pages_visited INTEGER DEFAULT 0,
                    actions_performed INTEGER DEFAULT 0,
                    honeypots_triggered INTEGER DEFAULT 0,
                    threats_detected INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    event_type TEXT,
                    event_name TEXT,
                    properties TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Page views table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS page_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_id TEXT,
                    page_path TEXT,
                    page_title TEXT,
                    referrer TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    metric_value REAL,
                    metric_unit TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Analytics database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database setup error: {e}")
    
    def _setup_geoip(self):
        """Setup GeoIP database for location tracking"""
        try:
            # Try to load GeoLite2 database (free from MaxMind)
            # Download from: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
            geoip_paths = [
                'GeoLite2-City.mmdb',
                '/usr/share/GeoIP/GeoLite2-City.mmdb',
                '/opt/GeoIP/GeoLite2-City.mmdb'
            ]
            
            for path in geoip_paths:
                try:
                    self.geoip_reader = geoip2.database.Reader(path)
                    self.logger.info(f"GeoIP database loaded from {path}")
                    break
                except FileNotFoundError:
                    continue
            
            if not self.geoip_reader:
                self.logger.warning("GeoIP database not found. Location tracking will be limited.")
                
        except Exception as e:
            self.logger.error(f"GeoIP setup error: {e}")
    
    def _get_location_from_ip(self, ip_address: str) -> Tuple[str, str]:
        """Get country and city from IP address"""
        try:
            if self.geoip_reader and ip_address != '127.0.0.1':
                response = self.geoip_reader.city(ip_address)
                country = response.country.name or 'Unknown'
                city = response.city.name or 'Unknown'
                return country, city
        except (geoip2.errors.AddressNotFoundError, Exception) as e:
            self.logger.debug(f"GeoIP lookup failed for {ip_address}: {e}")
        
        return 'Unknown', 'Unknown'
    
    def _parse_user_agent(self, user_agent: str) -> Tuple[str, str]:
        """Parse user agent to get device and browser info"""
        try:
            parsed = parse(user_agent)
            device_type = 'Mobile' if parsed.is_mobile else 'Desktop'
            browser = f"{parsed.browser.family} {parsed.browser.version_string}"
            return device_type, browser
        except Exception as e:
            self.logger.debug(f"User agent parsing failed: {e}")
            return 'Unknown', 'Unknown'
    
    async def start_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Start a new user session"""
        try:
            # Generate session ID
            session_data = f"{user_id}_{ip_address}_{datetime.now().isoformat()}"
            session_id = hashlib.md5(session_data.encode()).hexdigest()
            
            # Get location and device info
            country, city = self._get_location_from_ip(ip_address)
            device_type, browser = self._parse_user_agent(user_agent)
            
            # Create session object
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                country=country,
                city=city,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                pages_visited=0,
                actions_performed=0,
                honeypots_triggered=0,
                threats_detected=0
            )
            
            self.sessions[session_id] = session
            
            # Store in database
            async with aiosqlite.connect(self.db_path) as db:
                # Update or create user
                await db.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, first_seen, last_seen, total_sessions, country, city, device_type, browser)
                    VALUES (?, ?, ?, 
                           COALESCE((SELECT total_sessions FROM users WHERE user_id = ?), 0) + 1,
                           ?, ?, ?, ?)
                ''', (user_id, datetime.now(), datetime.now(), user_id, country, city, device_type, browser))
                
                # Create session
                await db.execute('''
                    INSERT INTO sessions 
                    (session_id, user_id, ip_address, user_agent, country, city, start_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, user_id, ip_address, user_agent, country, city, datetime.now()))
                
                await db.commit()
            
            self.logger.info(f"Session started: {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Session start error: {e}")
            return None
    
    async def track_page_view(self, session_id: str, page_path: str, page_title: str = None, referrer: str = None):
        """Track a page view"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.pages_visited += 1
                session.last_activity = datetime.now()
                
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('''
                        INSERT INTO page_views (session_id, user_id, page_path, page_title, referrer)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (session_id, session.user_id, page_path, page_title, referrer))
                    
                    await db.execute('''
                        UPDATE sessions SET pages_visited = pages_visited + 1 
                        WHERE session_id = ?
                    ''', (session_id,))
                    
                    await db.commit()
                
                self.logger.debug(f"Page view tracked: {page_path} for session {session_id}")
                
        except Exception as e:
            self.logger.error(f"Page view tracking error: {e}")
    
    async def track_event(self, session_id: str, event_type: str, event_name: str, properties: Dict[str, Any] = None):
        """Track a custom event"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.actions_performed += 1
                session.last_activity = datetime.now()
                
                # Special event handling
                if event_type == 'honeypot':
                    session.honeypots_triggered += 1
                elif event_type == 'threat':
                    session.threats_detected += 1
                
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('''
                        INSERT INTO events (session_id, user_id, event_type, event_name, properties)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (session_id, session.user_id, event_type, event_name, json.dumps(properties or {})))
                    
                    await db.execute('''
                        UPDATE sessions SET 
                        actions_performed = actions_performed + 1,
                        honeypots_triggered = CASE WHEN ? = 'honeypot' THEN honeypots_triggered + 1 ELSE honeypots_triggered END,
                        threats_detected = CASE WHEN ? = 'threat' THEN threats_detected + 1 ELSE threats_detected END
                        WHERE session_id = ?
                    ''', (event_type, event_type, session_id))
                    
                    await db.commit()
                
                self.logger.debug(f"Event tracked: {event_type}.{event_name} for session {session_id}")
                
        except Exception as e:
            self.logger.error(f"Event tracking error: {e}")
    
    async def end_session(self, session_id: str):
        """End a user session"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                duration = (datetime.now() - session.start_time).total_seconds()
                
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute('''
                        UPDATE sessions SET 
                        end_time = ?, 
                        duration = ?
                        WHERE session_id = ?
                    ''', (datetime.now(), duration, session_id))
                    
                    await db.execute('''
                        UPDATE users SET 
                        last_seen = ?,
                        total_actions = total_actions + ?
                        WHERE user_id = ?
                    ''', (datetime.now(), session.actions_performed, session.user_id))
                    
                    await db.commit()
                
                del self.sessions[session_id]
                self.logger.info(f"Session ended: {session_id}, duration: {duration:.1f}s")
                
        except Exception as e:
            self.logger.error(f"Session end error: {e}")
    
    async def get_usage_metrics(self, days: int = 30) -> UsageMetrics:
        """Get comprehensive usage metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total users
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                total_users = (await cursor.fetchone())[0]
                
                # Active users by period
                now = datetime.now()
                day_ago = now - timedelta(days=1)
                week_ago = now - timedelta(days=7)
                month_ago = now - timedelta(days=30)
                
                cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM sessions WHERE start_time > ?", (day_ago,))
                active_24h = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM sessions WHERE start_time > ?", (week_ago,))
                active_7d = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM sessions WHERE start_time > ?", (month_ago,))
                active_30d = (await cursor.fetchone())[0]
                
                # Session metrics
                cursor = await db.execute("SELECT COUNT(*), AVG(duration) FROM sessions WHERE start_time > ?", (month_ago,))
                session_data = await cursor.fetchone()
                total_sessions = session_data[0]
                avg_duration = session_data[1] or 0
                
                # Activity metrics
                cursor = await db.execute("SELECT SUM(pages_visited), SUM(actions_performed), SUM(honeypots_triggered), SUM(threats_detected) FROM sessions WHERE start_time > ?", (month_ago,))
                activity_data = await cursor.fetchone()
                total_pages = activity_data[0] or 0
                total_actions = activity_data[1] or 0
                total_honeypots = activity_data[2] or 0
                total_threats = activity_data[3] or 0
                
                # Geographic data
                cursor = await db.execute("SELECT country, COUNT(*) FROM sessions WHERE start_time > ? GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10", (month_ago,))
                top_countries = await cursor.fetchall()
                
                cursor = await db.execute("SELECT city, COUNT(*) FROM sessions WHERE start_time > ? GROUP BY city ORDER BY COUNT(*) DESC LIMIT 10", (month_ago,))
                top_cities = await cursor.fetchall()
                
                # Device breakdown
                cursor = await db.execute("SELECT device_type, COUNT(*) FROM users GROUP BY device_type")
                device_data = await cursor.fetchall()
                device_breakdown = dict(device_data)
                
                # Browser breakdown
                cursor = await db.execute("SELECT browser, COUNT(*) FROM users GROUP BY browser ORDER BY COUNT(*) DESC LIMIT 10")
                browser_data = await cursor.fetchall()
                browser_breakdown = dict(browser_data)
                
                return UsageMetrics(
                    total_users=total_users,
                    active_users_24h=active_24h,
                    active_users_7d=active_7d,
                    active_users_30d=active_30d,
                    total_sessions=total_sessions,
                    avg_session_duration=avg_duration,
                    total_page_views=total_pages,
                    total_actions=total_actions,
                    total_honeypots_triggered=total_honeypots,
                    total_threats_detected=total_threats,
                    top_countries=top_countries,
                    top_cities=top_cities,
                    device_breakdown=device_breakdown,
                    browser_breakdown=browser_breakdown
                )
                
        except Exception as e:
            self.logger.error(f"Metrics calculation error: {e}")
            return UsageMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [], [], {}, {})
    
    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics"""
        try:
            active_sessions = len(self.sessions)
            
            # Calculate current activity
            current_countries = Counter()
            current_devices = Counter()
            total_actions_now = 0
            
            for session in self.sessions.values():
                current_countries[session.country] += 1
                device_type, _ = self._parse_user_agent(session.user_agent)
                current_devices[device_type] += 1
                total_actions_now += session.actions_performed
            
            return {
                'active_sessions': active_sessions,
                'active_countries': dict(current_countries.most_common(5)),
                'active_devices': dict(current_devices),
                'actions_in_progress': total_actions_now,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Real-time stats error: {e}")
            return {}
    
    async def generate_analytics_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            metrics = await self.get_usage_metrics(days)
            real_time = await self.get_real_time_stats()
            
            return {
                'report_generated': datetime.now().isoformat(),
                'period_days': days,
                'usage_metrics': asdict(metrics),
                'real_time_stats': real_time,
                'summary': {
                    'growth_rate': f"{(metrics.active_users_30d / max(metrics.total_users, 1)) * 100:.1f}%",
                    'engagement_rate': f"{(metrics.total_actions / max(metrics.total_sessions, 1)):.1f} actions/session",
                    'security_activity': f"{metrics.total_honeypots_triggered + metrics.total_threats_detected} security events",
                    'avg_session_minutes': f"{metrics.avg_session_duration / 60:.1f} minutes"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return {'error': str(e)}

# Global analytics instance
analytics = ProjectAnalytics()

# Helper functions for easy integration
async def track_user_login(user_id: str, ip_address: str, user_agent: str) -> str:
    """Track user login and start session"""
    return await analytics.start_session(user_id, ip_address, user_agent)

async def track_honeypot_trigger(session_id: str, honeypot_type: str, attacker_ip: str):
    """Track honeypot trigger event"""
    await analytics.track_event(session_id, 'honeypot', 'trigger', {
        'honeypot_type': honeypot_type,
        'attacker_ip': attacker_ip
    })

async def track_threat_detection(session_id: str, threat_type: str, severity: str):
    """Track threat detection event"""
    await analytics.track_event(session_id, 'threat', 'detection', {
        'threat_type': threat_type,
        'severity': severity
    })

async def get_admin_dashboard_data() -> Dict[str, Any]:
    """Get data for admin dashboard"""
    return await analytics.generate_analytics_report()
