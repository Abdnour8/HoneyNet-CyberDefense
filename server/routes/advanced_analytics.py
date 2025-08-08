#!/usr/bin/env python3
"""
Advanced Analytics API - Google Analytics Level Features
API מתקדם לאנליטיקס ברמה של Google Analytics
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

# הגדרת הנתב
router = APIRouter(prefix="/api/analytics", tags=["Advanced Analytics"])

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# נתיב למסד הנתונים המתקדם
ADVANCED_DB_PATH = "server/data/advanced_analytics.db"

def get_db_connection():
    """יצירת חיבור למסד הנתונים המתקדם"""
    try:
        conn = sqlite3.connect(ADVANCED_DB_PATH)
        conn.row_factory = sqlite3.Row  # מאפשר גישה לעמודות לפי שם
        return conn
    except Exception as e:
        logger.error(f"שגיאה בחיבור למסד הנתונים: {e}")
        raise HTTPException(status_code=500, detail="שגיאה בחיבור למסד הנתונים")

@router.get("/advanced-dashboard")
async def get_advanced_dashboard_data():
    """
    קבלת נתונים מתקדמים לדשבורד ברמה של Google Analytics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. מטריקות זמן אמת
        real_time_metrics = get_real_time_metrics(cursor)
        
        # 2. נתונים לפי שעות (24 שעות אחרונות)
        hourly_data = get_hourly_data(cursor)
        
        # 3. נתוני מכשירים
        device_data = get_device_analytics(cursor)
        
        # 4. נתוני דפדפנים
        browser_data = get_browser_analytics(cursor)
        
        # 5. נתונים גיאוגרפיים
        geographic_data = get_geographic_analytics(cursor)
        
        # 6. עמודים פופולריים
        popular_pages = get_popular_pages(cursor)
        
        # 7. מסלולי משתמשים
        user_journeys = get_user_journeys(cursor)
        
        # 8. משפכי המרה
        conversion_funnels = get_conversion_funnels(cursor)
        
        # 9. ניתוח קבוצות
        cohort_analysis = get_cohort_analysis(cursor)
        
        conn.close()
        
        return JSONResponse({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "realTimeMetrics": real_time_metrics,
                "hourlyData": hourly_data,
                "deviceData": device_data,
                "browserData": browser_data,
                "geographicData": geographic_data,
                "popularPages": popular_pages,
                "userJourneys": user_journeys,
                "conversionFunnels": conversion_funnels,
                "cohortAnalysis": cohort_analysis
            }
        })
        
    except Exception as e:
        logger.error(f"שגיאה בקבלת נתוני דשבורד מתקדם: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_real_time_metrics(cursor) -> Dict[str, Any]:
    """קבלת מטריקות זמן אמת"""
    
    # משתמשים פעילים (15 דקות אחרונות)
    cursor.execute("""
        SELECT COUNT(DISTINCT session_id) as active_users
        FROM user_sessions 
        WHERE start_time >= datetime('now', '-15 minutes')
    """)
    active_users = cursor.fetchone()['active_users']
    
    # צפיות בעמוד היום
    cursor.execute("""
        SELECT COUNT(*) as page_views
        FROM page_analytics 
        WHERE DATE(timestamp) = DATE('now')
    """)
    page_views_today = cursor.fetchone()['page_views']
    
    # אחוז נטישה ממוצע
    cursor.execute("""
        SELECT AVG(bounce_rate) as avg_bounce_rate
        FROM user_sessions 
        WHERE DATE(start_time) = DATE('now')
    """)
    bounce_rate = cursor.fetchone()['avg_bounce_rate'] or 0
    
    # משך סשן ממוצע (בשניות)
    cursor.execute("""
        SELECT AVG(duration) as avg_duration
        FROM user_sessions 
        WHERE DATE(start_time) = DATE('now')
    """)
    avg_session_duration = cursor.fetchone()['avg_duration'] or 0
    
    # המרות היום
    cursor.execute("""
        SELECT COUNT(*) as conversions
        FROM conversion_funnels 
        WHERE completed = 1 AND DATE(timestamp) = DATE('now')
    """)
    conversions_today = cursor.fetchone()['conversions']
    
    # הכנסות היום
    cursor.execute("""
        SELECT SUM(conversion_value) as revenue
        FROM user_sessions 
        WHERE DATE(start_time) = DATE('now')
    """)
    revenue_today = cursor.fetchone()['revenue'] or 0
    
    return {
        "activeUsers": active_users,
        "pageViewsToday": page_views_today,
        "bounceRate": bounce_rate,
        "avgSessionDuration": int(avg_session_duration),
        "conversionsToday": conversions_today,
        "revenueToday": round(revenue_today, 2)
    }

def get_hourly_data(cursor) -> List[Dict[str, Any]]:
    """קבלת נתונים לפי שעות (24 שעות אחרונות)"""
    
    cursor.execute("""
        SELECT 
            strftime('%H', start_time) as hour,
            COUNT(DISTINCT session_id) as users,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(page_views) as page_views,
            SUM(downloads) as downloads,
            AVG(duration) as avg_duration
        FROM user_sessions 
        WHERE start_time >= datetime('now', '-24 hours')
        GROUP BY strftime('%H', start_time)
        ORDER BY hour
    """)
    
    hourly_data = []
    for row in cursor.fetchall():
        hourly_data.append({
            "hour": int(row['hour']),
            "users": row['users'],
            "uniqueUsers": row['unique_users'],
            "pageViews": row['page_views'] or 0,
            "downloads": row['downloads'] or 0,
            "avgDuration": round(row['avg_duration'] or 0, 2)
        })
    
    return hourly_data

def get_device_analytics(cursor) -> List[Dict[str, Any]]:
    """ניתוח מכשירים"""
    
    cursor.execute("""
        SELECT 
            device_type,
            COUNT(DISTINCT session_id) as sessions,
            COUNT(DISTINCT user_id) as users,
            AVG(duration) as avg_duration,
            AVG(page_views) as avg_page_views
        FROM user_sessions 
        WHERE DATE(start_time) >= DATE('now', '-7 days')
        GROUP BY device_type
        ORDER BY users DESC
    """)
    
    device_data = []
    total_users = 0
    
    # חישוב סך המשתמשים
    for row in cursor.fetchall():
        total_users += row['users']
    
    cursor.execute("""
        SELECT 
            device_type,
            COUNT(DISTINCT session_id) as sessions,
            COUNT(DISTINCT user_id) as users,
            AVG(duration) as avg_duration,
            AVG(page_views) as avg_page_views
        FROM user_sessions 
        WHERE DATE(start_time) >= DATE('now', '-7 days')
        GROUP BY device_type
        ORDER BY users DESC
    """)
    
    for row in cursor.fetchall():
        percentage = (row['users'] / total_users * 100) if total_users > 0 else 0
        device_data.append({
            "device": row['device_type'],
            "sessions": row['sessions'],
            "users": row['users'],
            "percentage": round(percentage, 1),
            "avgDuration": round(row['avg_duration'] or 0, 2),
            "avgPageViews": round(row['avg_page_views'] or 0, 2)
        })
    
    return device_data

def get_browser_analytics(cursor) -> List[Dict[str, Any]]:
    """ניתוח דפדפנים"""
    
    cursor.execute("""
        SELECT 
            browser,
            COUNT(DISTINCT session_id) as sessions,
            COUNT(DISTINCT user_id) as users,
            AVG(duration) as avg_duration
        FROM user_sessions 
        WHERE DATE(start_time) >= DATE('now', '-7 days')
        GROUP BY browser
        ORDER BY users DESC
        LIMIT 10
    """)
    
    browser_data = []
    for row in cursor.fetchall():
        browser_data.append({
            "browser": row['browser'],
            "sessions": row['sessions'],
            "users": row['users'],
            "avgDuration": round(row['avg_duration'] or 0, 2)
        })
    
    return browser_data

def get_geographic_analytics(cursor) -> List[Dict[str, Any]]:
    """ניתוח גיאוגרפי"""
    
    cursor.execute("""
        SELECT 
            country_name as country,
            COUNT(DISTINCT s.session_id) as sessions,
            COUNT(DISTINCT s.user_id) as users,
            AVG(s.duration) as avg_duration,
            0 as conversions
        FROM geographic_data g
        JOIN user_sessions s ON g.session_id = s.session_id
        WHERE DATE(s.start_time) >= DATE('now', '-7 days')
        GROUP BY country_name
        ORDER BY users DESC
        LIMIT 20
    """)
    
    geographic_data = []
    for row in cursor.fetchall():
        geographic_data.append({
            "country": row['country'],
            "sessions": row['sessions'],
            "users": row['users'],
            "avgDuration": round(row['avg_duration'] or 0, 2),
            "conversions": row['conversions'] or 0
        })
    
    return geographic_data

def get_popular_pages(cursor) -> List[Dict[str, Any]]:
    """עמודים פופולריים"""
    
    cursor.execute("""
        SELECT 
            page_url,
            page_title,
            COUNT(*) as views,
            AVG(time_on_page) as avg_time,
            AVG(CASE WHEN bounce = 1 THEN 1.0 ELSE 0.0 END) as bounce_rate,
            COUNT(DISTINCT session_id) as unique_visitors
        FROM page_analytics 
        WHERE DATE(timestamp) >= DATE('now', '-7 days')
        GROUP BY page_url, page_title
        ORDER BY views DESC
        LIMIT 20
    """)
    
    popular_pages = []
    for row in cursor.fetchall():
        popular_pages.append({
            "page": row['page_url'],
            "title": row['page_title'],
            "views": row['views'],
            "avgTime": round(row['avg_time'] or 0, 2),
            "bounceRate": round(row['bounce_rate'] or 0, 3),
            "uniqueVisitors": row['unique_visitors']
        })
    
    return popular_pages

def get_user_journeys(cursor) -> List[Dict[str, Any]]:
    """מסלולי משתמשים"""
    
    cursor.execute("""
        SELECT 
            uj1.page_url as from_page,
            uj2.page_url as to_page,
            COUNT(*) as transitions
        FROM user_journeys uj1
        JOIN user_journeys uj2 ON uj1.session_id = uj2.session_id 
            AND uj2.journey_step = uj1.journey_step + 1
        WHERE DATE(uj1.timestamp) >= DATE('now', '-7 days')
        GROUP BY uj1.page_url, uj2.page_url
        ORDER BY transitions DESC
        LIMIT 20
    """)
    
    user_journeys = []
    for row in cursor.fetchall():
        user_journeys.append({
            "from": row['from_page'],
            "to": row['to_page'],
            "transitions": row['transitions']
        })
    
    return user_journeys

def get_conversion_funnels(cursor) -> List[Dict[str, Any]]:
    """משפכי המרה"""
    
    cursor.execute("""
        SELECT 
            funnel_name,
            step_number,
            step_name,
            COUNT(DISTINCT session_id) as users,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed,
            AVG(time_to_complete) as avg_time
        FROM conversion_funnels 
        WHERE DATE(timestamp) >= DATE('now', '-7 days')
        GROUP BY funnel_name, step_number, step_name
        ORDER BY funnel_name, step_number
    """)
    
    funnels = {}
    for row in cursor.fetchall():
        funnel_name = row['funnel_name']
        if funnel_name not in funnels:
            funnels[funnel_name] = []
        
        completion_rate = (row['completed'] / row['users'] * 100) if row['users'] > 0 else 0
        
        funnels[funnel_name].append({
            "step": row['step_number'],
            "name": row['step_name'],
            "users": row['users'],
            "completed": row['completed'],
            "completionRate": round(completion_rate, 1),
            "avgTime": round(row['avg_time'] or 0, 2)
        })
    
    return funnels

def get_cohort_analysis(cursor) -> Dict[str, Any]:
    """ניתוח קבוצות (Cohort Analysis)"""
    
    cursor.execute("""
        SELECT 
            cohort_date,
            retention_day,
            COUNT(DISTINCT user_id) as retained_users,
            AVG(sessions_count) as avg_sessions,
            SUM(total_revenue) as total_revenue
        FROM cohort_analysis 
        WHERE cohort_date >= DATE('now', '-90 days')
        GROUP BY cohort_date, retention_day
        ORDER BY cohort_date, retention_day
    """)
    
    cohorts = {}
    for row in cursor.fetchall():
        cohort_date = row['cohort_date']
        if cohort_date not in cohorts:
            cohorts[cohort_date] = {}
        
        cohorts[cohort_date][f"day_{row['retention_day']}"] = {
            "retainedUsers": row['retained_users'],
            "avgSessions": round(row['avg_sessions'] or 0, 2),
            "totalRevenue": round(row['total_revenue'] or 0, 2)
        }
    
    return cohorts

@router.post("/track-advanced")
async def track_advanced_analytics(request: Request):
    """
    מעקב מתקדם אחר פעילות משתמשים
    """
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # עדכון או יצירת סשן משתמש
        session_data = data.get('session', {})
        if session_data:
            update_user_session(cursor, session_data)
        
        # הוספת אירועים
        events = data.get('events', [])
        for event in events:
            insert_user_event(cursor, event)
        
        # עדכון מסלול משתמש
        journey_data = data.get('journey', {})
        if journey_data:
            update_user_journey(cursor, journey_data)
        
        # עדכון נתונים גיאוגרפיים
        geo_data = data.get('geographic', {})
        if geo_data:
            update_geographic_data(cursor, geo_data)
        
        conn.commit()
        conn.close()
        
        return JSONResponse({
            "status": "success",
            "message": "נתונים מתקדמים נשמרו בהצלחה",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"שגיאה במעקב מתקדם: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def update_user_session(cursor, session_data):
    """עדכון נתוני סשן משתמש"""
    cursor.execute("""
        INSERT OR REPLACE INTO user_sessions (
            session_id, user_id, ip_address, country, city,
            device_type, browser, os, start_time, duration,
            page_views, bounce_rate, conversion_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_data.get('session_id'),
        session_data.get('user_id'),
        session_data.get('ip_address'),
        session_data.get('country'),
        session_data.get('city'),
        session_data.get('device_type'),
        session_data.get('browser'),
        session_data.get('os'),
        session_data.get('start_time'),
        session_data.get('duration', 0),
        session_data.get('page_views', 0),
        session_data.get('bounce_rate', 0),
        session_data.get('conversion_value', 0)
    ))

def insert_user_event(cursor, event_data):
    """הוספת אירוע משתמש"""
    cursor.execute("""
        INSERT INTO user_events (
            session_id, event_type, event_category, event_action,
            event_label, event_value, page_url, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_data.get('session_id'),
        event_data.get('event_type'),
        event_data.get('event_category'),
        event_data.get('event_action'),
        event_data.get('event_label'),
        event_data.get('event_value', 0),
        event_data.get('page_url'),
        datetime.now().isoformat()
    ))

def update_user_journey(cursor, journey_data):
    """עדכון מסלול משתמש"""
    cursor.execute("""
        INSERT INTO user_journeys (
            user_id, session_id, journey_step, page_url,
            action_type, time_spent, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        journey_data.get('user_id'),
        journey_data.get('session_id'),
        journey_data.get('journey_step'),
        journey_data.get('page_url'),
        journey_data.get('action_type'),
        journey_data.get('time_spent', 0),
        datetime.now().isoformat()
    ))

def update_geographic_data(cursor, geo_data):
    """עדכון נתונים גיאוגרפיים"""
    cursor.execute("""
        INSERT OR REPLACE INTO geographic_data (
            session_id, ip_address, country_code, country_name,
            city, latitude, longitude, timezone, isp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        geo_data.get('session_id'),
        geo_data.get('ip_address'),
        geo_data.get('country_code'),
        geo_data.get('country_name'),
        geo_data.get('city'),
        geo_data.get('latitude'),
        geo_data.get('longitude'),
        geo_data.get('timezone'),
        geo_data.get('isp')
    ))

@router.get("/real-time-metrics")
async def get_real_time_metrics_endpoint():
    """קבלת מטריקות זמן אמת בלבד"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        metrics = get_real_time_metrics(cursor)
        
        conn.close()
        
        return JSONResponse({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })
        
    except Exception as e:
        logger.error(f"שגיאה בקבלת מטריקות זמן אמת: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """בדיקת תקינות API מתקדם"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # בדיקה שהטבלאות קיימות
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'user_sessions', 'page_analytics', 'user_events',
            'geographic_data', 'user_journeys', 'cohort_analysis'
        ]
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        conn.close()
        
        return JSONResponse({
            "status": "healthy" if not missing_tables else "warning",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "tables": len(tables),
            "missing_tables": missing_tables
        })
        
    except Exception as e:
        logger.error(f"שגיאה בבדיקת תקינות: {e}")
        return JSONResponse({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }, status_code=500)
