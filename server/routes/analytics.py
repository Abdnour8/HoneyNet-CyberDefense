"""
HoneyNet Analytics API Routes
נתיבי API לאנלטיקס של HoneyNet
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import sqlite3
import os
from pathlib import Path
import geoip2.database
import geoip2.errors
from user_agents import parse

# Create router
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Data models
class AnalyticsEvent(BaseModel):
    type: str  # 'pageview', 'event', 'download'
    data: Dict[str, Any]
    timestamp: str

class SessionData(BaseModel):
    session_id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    start_time: datetime
    last_activity: datetime
    pages_visited: int = 0
    actions_performed: int = 0
    downloads: int = 0

class DownloadData(BaseModel):
    filename: str
    file_type: str
    file_size: Optional[int] = None
    user_id: str
    session_id: str
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timestamp: datetime

# Database setup
def get_analytics_db():
    """Get analytics database connection"""
    db_path = Path(__file__).parent.parent / "data" / "analytics.db"
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    # Create tables if they don't exist
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            country TEXT,
            city TEXT,
            start_time TIMESTAMP,
            last_activity TIMESTAMP,
            pages_visited INTEGER DEFAULT 0,
            actions_performed INTEGER DEFAULT 0,
            downloads INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id TEXT,
            page TEXT,
            title TEXT,
            url TEXT,
            referrer TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        );
        
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id TEXT,
            category TEXT,
            action TEXT,
            properties TEXT,
            page TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        );
        
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id TEXT,
            filename TEXT,
            file_type TEXT,
            file_size INTEGER,
            ip_address TEXT,
            country TEXT,
            city TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON sessions(start_time);
        CREATE INDEX IF NOT EXISTS idx_page_views_timestamp ON page_views(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_downloads_timestamp ON downloads(timestamp);
    """)
    
    conn.commit()
    return conn

def get_location_from_ip(ip_address: str) -> tuple:
    """Get country and city from IP address using GeoIP"""
    try:
        # Try to find GeoIP database
        geoip_paths = [
            "/usr/share/GeoIP/GeoLite2-City.mmdb",
            "/opt/GeoIP/GeoLite2-City.mmdb",
            "./GeoLite2-City.mmdb",
            "../data/GeoLite2-City.mmdb"
        ]
        
        geoip_db = None
        for path in geoip_paths:
            if os.path.exists(path):
                geoip_db = path
                break
        
        if not geoip_db:
            return "Unknown", "Unknown"
        
        with geoip2.database.Reader(geoip_db) as reader:
            response = reader.city(ip_address)
            country = response.country.name or "Unknown"
            city = response.city.name or "Unknown"
            return country, city
            
    except (geoip2.errors.AddressNotFoundError, FileNotFoundError, Exception):
        return "Unknown", "Unknown"

def parse_user_agent(user_agent: str) -> dict:
    """Parse user agent string"""
    try:
        ua = parse(user_agent)
        return {
            "browser": f"{ua.browser.family} {ua.browser.version_string}",
            "os": f"{ua.os.family} {ua.os.version_string}",
            "device": ua.device.family,
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_pc": ua.is_pc
        }
    except Exception:
        return {
            "browser": "Unknown",
            "os": "Unknown",
            "device": "Unknown",
            "is_mobile": False,
            "is_tablet": False,
            "is_pc": True
        }

@router.post("/")
async def track_analytics(event: AnalyticsEvent, request: Request):
    """Track analytics event"""
    try:
        conn = get_analytics_db()
        client_ip = request.client.host
        
        # Get location from IP
        country, city = get_location_from_ip(client_ip)
        
        if event.type == "pageview":
            data = event.data
            
            # Update or create session
            session_id = data.get("sessionId")
            user_id = data.get("userId")
            user_agent = request.headers.get("user-agent", "")
            
            # Upsert session
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, user_id, ip_address, user_agent, country, city, start_time, last_activity, pages_visited)
                VALUES (?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT start_time FROM sessions WHERE session_id = ?), ?),
                    ?, 
                    COALESCE((SELECT pages_visited FROM sessions WHERE session_id = ?), 0) + 1)
            """, (session_id, user_id, client_ip, user_agent, country, city, 
                  session_id, datetime.now(), datetime.now(), session_id))
            
            # Insert page view
            conn.execute("""
                INSERT INTO page_views (session_id, user_id, page, title, url, referrer, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, data.get("page"), data.get("title"), 
                  data.get("url"), data.get("referrer"), datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))))
        
        elif event.type == "event":
            data = event.data
            session_id = data.get("sessionId")
            user_id = data.get("userId")
            
            # Update session activity
            conn.execute("""
                UPDATE sessions 
                SET last_activity = ?, actions_performed = actions_performed + 1
                WHERE session_id = ?
            """, (datetime.now(), session_id))
            
            # Insert event
            conn.execute("""
                INSERT INTO events (session_id, user_id, category, action, properties, page, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, data.get("category"), data.get("action"),
                  json.dumps(data.get("properties", {})), data.get("page"),
                  datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))))
        
        elif event.type == "download":
            data = event.data
            session_id = data.get("sessionId")
            user_id = data.get("userId")
            
            # Update session downloads
            conn.execute("""
                UPDATE sessions 
                SET last_activity = ?, downloads = downloads + 1
                WHERE session_id = ?
            """, (datetime.now(), session_id))
            
            # Insert download
            conn.execute("""
                INSERT INTO downloads (session_id, user_id, filename, file_type, file_size, 
                                     ip_address, country, city, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, data.get("filename"), data.get("fileType"),
                  data.get("fileSize"), client_ip, country, city,
                  datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))))
        
        conn.commit()
        conn.close()
        
        return JSONResponse({"status": "success", "message": "Analytics event tracked"})
        
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"Failed to track analytics: {str(e)}"},
            status_code=500
        )

@router.get("/dashboard")
async def get_dashboard_data():
    """Get analytics dashboard data"""
    try:
        conn = get_analytics_db()
        
        # Get basic stats
        stats = {}
        
        # Total users (unique user_ids)
        result = conn.execute("SELECT COUNT(DISTINCT user_id) as count FROM sessions").fetchone()
        stats["totalUsers"] = result["count"]
        
        # Total downloads
        result = conn.execute("SELECT COUNT(*) as count FROM downloads").fetchone()
        stats["totalDownloads"] = result["count"]
        
        # Active sessions (last activity within 30 minutes)
        cutoff = datetime.now() - timedelta(minutes=30)
        result = conn.execute(
            "SELECT COUNT(*) as count FROM sessions WHERE last_activity > ?", 
            (cutoff,)
        ).fetchone()
        stats["activeSessions"] = result["count"]
        
        # Total countries
        result = conn.execute("SELECT COUNT(DISTINCT country) as count FROM sessions WHERE country != 'Unknown'").fetchone()
        stats["totalCountries"] = result["count"]
        
        # Recent downloads (last 50)
        downloads = conn.execute("""
            SELECT d.filename, d.file_type, d.timestamp, d.country, s.user_id
            FROM downloads d
            JOIN sessions s ON d.session_id = s.session_id
            ORDER BY d.timestamp DESC
            LIMIT 50
        """).fetchall()
        
        downloads_list = []
        for download in downloads:
            downloads_list.append({
                "filename": download["filename"],
                "type": download["file_type"],
                "timestamp": download["timestamp"],
                "country": download["country"],
                "userId": download["user_id"]
            })
        
        # Active users
        active_users = conn.execute("""
            SELECT user_id, pages_visited, 
                   (julianday('now') - julianday(start_time)) * 24 * 60 * 60 as duration,
                   country
            FROM sessions 
            WHERE last_activity > ?
            ORDER BY last_activity DESC
            LIMIT 25
        """, (cutoff,)).fetchall()
        
        users_list = []
        for user in active_users:
            users_list.append({
                "userId": user["user_id"],
                "pageViews": user["pages_visited"],
                "duration": int(user["duration"]) if user["duration"] else 0,
                "country": user["country"],
                "isActive": True
            })
        
        # Top countries
        countries = conn.execute("""
            SELECT country, COUNT(*) as count
            FROM downloads d
            JOIN sessions s ON d.session_id = s.session_id
            WHERE s.country != 'Unknown'
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()
        
        countries_list = []
        for country in countries:
            countries_list.append({
                "name": country["country"],
                "count": country["count"]
            })
        
        # Downloads by day (last 7 days)
        downloads_by_day = conn.execute("""
            SELECT DATE(timestamp) as day, COUNT(*) as count
            FROM downloads
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY day
        """).fetchall()
        
        conn.close()
        
        return JSONResponse({
            "status": "success",
            "data": {
                **stats,
                "downloads": downloads_list,
                "users": users_list,
                "countries": countries_list,
                "downloadsByDay": [{"day": row["day"], "count": row["count"]} for row in downloads_by_day]
            }
        })
        
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"Failed to get dashboard data: {str(e)}"},
            status_code=500
        )

@router.get("/stats")
async def get_basic_stats():
    """Get basic analytics statistics"""
    try:
        conn = get_analytics_db()
        
        # Get various statistics
        stats = {}
        
        # Users and sessions
        result = conn.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                COUNT(*) as total_sessions,
                AVG(pages_visited) as avg_pages_per_session,
                AVG(downloads) as avg_downloads_per_session
            FROM sessions
        """).fetchone()
        
        stats.update({
            "totalUsers": result["total_users"],
            "totalSessions": result["total_sessions"],
            "avgPagesPerSession": round(result["avg_pages_per_session"] or 0, 2),
            "avgDownloadsPerSession": round(result["avg_downloads_per_session"] or 0, 2)
        })
        
        # Downloads
        result = conn.execute("""
            SELECT 
                COUNT(*) as total_downloads,
                COUNT(DISTINCT filename) as unique_files
            FROM downloads
        """).fetchone()
        
        stats.update({
            "totalDownloads": result["total_downloads"],
            "uniqueFiles": result["unique_files"]
        })
        
        # Geographic distribution
        result = conn.execute("""
            SELECT 
                COUNT(DISTINCT country) as countries,
                COUNT(DISTINCT city) as cities
            FROM sessions 
            WHERE country != 'Unknown'
        """).fetchone()
        
        stats.update({
            "totalCountries": result["countries"],
            "totalCities": result["cities"]
        })
        
        conn.close()
        
        return JSONResponse({
            "status": "success",
            "data": stats
        })
        
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"Failed to get stats: {str(e)}"},
            status_code=500
        )

@router.get("/export")
async def export_analytics_data():
    """Export all analytics data"""
    try:
        conn = get_analytics_db()
        
        # Get all data
        sessions = conn.execute("SELECT * FROM sessions ORDER BY start_time DESC").fetchall()
        page_views = conn.execute("SELECT * FROM page_views ORDER BY timestamp DESC").fetchall()
        events = conn.execute("SELECT * FROM events ORDER BY timestamp DESC").fetchall()
        downloads = conn.execute("SELECT * FROM downloads ORDER BY timestamp DESC").fetchall()
        
        conn.close()
        
        # Convert to dictionaries
        data = {
            "sessions": [dict(row) for row in sessions],
            "pageViews": [dict(row) for row in page_views],
            "events": [dict(row) for row in events],
            "downloads": [dict(row) for row in downloads],
            "exportedAt": datetime.now().isoformat()
        }
        
        return JSONResponse({
            "status": "success",
            "data": data
        })
        
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"Failed to export data: {str(e)}"},
            status_code=500
        )

@router.post("/track")
async def track_analytics(request: Request):
    """Track real-time analytics data from website visitors"""
    try:
        data = await request.json()
        
        # Extract data from request
        analytics_type = data.get('type', 'unknown')
        analytics_data = data.get('data', {})
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        session_id = data.get('sessionId', 'unknown')
        user_id = data.get('userId', 'anonymous')
        url = data.get('url', '')
        user_agent = data.get('userAgent', '')
        referrer = data.get('referrer', '')
        
        # Get database connection
        db = get_db_connection()
        cursor = db.cursor()
        
        # Handle different types of analytics data
        if analytics_type == 'page_view':
            # Insert page view
            cursor.execute("""
                INSERT INTO page_views (session_id, user_id, page_url, timestamp, user_agent, referrer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, url, timestamp, user_agent, referrer))
            
        elif analytics_type == 'download':
            # Insert download tracking
            filename = analytics_data.get('filename', 'unknown')
            file_type = analytics_data.get('fileType', 'unknown')
            
            cursor.execute("""
                INSERT INTO downloads (session_id, user_id, filename, file_type, timestamp, user_agent, referrer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, filename, file_type, timestamp, user_agent, referrer))
            
        elif analytics_type == 'session':
            # Handle session start/end
            action = analytics_data.get('action', 'start')
            if action == 'start':
                cursor.execute("""
                    INSERT INTO sessions (session_id, user_id, start_time, user_agent, referrer)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, user_id, timestamp, user_agent, referrer))
            
        else:
            # Insert as general event
            cursor.execute("""
                INSERT INTO events (session_id, user_id, event_type, event_data, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, analytics_type, str(analytics_data), timestamp))
        
        # Commit changes
        db.commit()
        db.close()
        
        return JSONResponse({
            "status": "success",
            "message": f"Analytics data tracked: {analytics_type}",
            "timestamp": timestamp
        })
        
    except Exception as e:
        logger.error(f"Failed to track analytics: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": f"Failed to track analytics: {str(e)}"},
            status_code=500
        )

@router.get("/software-dashboard")
async def get_software_dashboard_data():
    """Get software analytics dashboard data"""
    try:
        # Import project analytics
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from core.project_analytics import analytics
        
        # Get comprehensive analytics data
        dashboard_data = await analytics.get_admin_dashboard_data()
        
        return JSONResponse({
            "status": "success",
            "data": dashboard_data
        })
        
    except Exception as e:
        # Return demo data if analytics not available
        demo_data = {
            "stats": {
                "active_users": 1247,
                "active_honeypots": 89,
                "threats_detected": 156,
                "active_sessions": 34
            },
            "usage_data": [120, 135, 142, 158, 167, 145, 189, 201, 187, 195, 210, 198, 225, 234, 245, 238, 252, 267, 275, 289, 298, 312, 325, 334, 345, 356, 367, 378, 389, 401],
            "countries_data": [
                {"country": "ישראל", "users": 456},
                {"country": "ארה\"ב", "users": 234},
                {"country": "גרמניה", "users": 189},
                {"country": "צרפת", "users": 156},
                {"country": "בריטניה", "users": 123}
            ],
            "honeypots_data": [12, 15, 18, 14, 22, 19, 25, 28, 24, 31, 29, 35, 32, 38, 41, 37, 44, 47, 43, 50, 48, 54, 51, 58, 55, 62, 59, 65, 68, 71],
            "threats_data": [8, 12, 15, 11, 18, 14, 21, 17, 24, 20, 27, 23, 30, 26, 33, 29, 36, 32, 39, 35, 42, 38, 45, 41, 48, 44, 51, 47, 54, 50],
            "active_users_list": [
                {"user": "user_001", "country": "ישראל", "last_seen": "2 דקות", "status": "online"},
                {"user": "user_045", "country": "ארה\"ב", "last_seen": "5 דקות", "status": "online"},
                {"user": "user_123", "country": "גרמניה", "last_seen": "12 דקות", "status": "offline"},
                {"user": "user_089", "country": "צרפת", "last_seen": "18 דקות", "status": "offline"},
                {"user": "user_156", "country": "בריטניה", "last_seen": "25 דקות", "status": "offline"}
            ],
            "honeypots_list": [
                {"type": "File Trap", "attacker_ip": "192.168.1.100", "time": "3 דקות", "severity": "גבוהה"},
                {"type": "Login Trap", "attacker_ip": "10.0.0.45", "time": "7 דקות", "severity": "בינונית"},
                {"type": "Network Trap", "attacker_ip": "172.16.0.23", "time": "12 דקות", "severity": "גבוהה"},
                {"type": "Email Trap", "attacker_ip": "203.45.67.89", "time": "18 דקות", "severity": "נמוכה"},
                {"type": "Database Trap", "attacker_ip": "156.78.90.12", "time": "25 דקות", "severity": "גבוהה"}
            ]
        }
        
        return JSONResponse({
            "status": "success", 
            "data": demo_data,
            "note": "Using demo data - analytics system not fully connected"
        })
