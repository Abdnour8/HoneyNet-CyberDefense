"""
HoneyNet Enterprise API
Advanced API for enterprise customers with authentication, analytics, and management features
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import sqlite3
import json
from pathlib import Path
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HoneyNet Enterprise API",
    description="Professional API for HoneyNet Enterprise customers",
    version="2.0.0",
    docs_url="/enterprise/docs",
    redoc_url="/enterprise/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "honeynet-enterprise-secret-key-2025"
ALGORITHM = "HS256"

# Database setup
DB_PATH = Path("enterprise.db")

class EnterpriseDB:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialize enterprise database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Organizations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                domain TEXT UNIQUE NOT NULL,
                subscription_tier TEXT DEFAULT 'free',
                api_key TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings JSON DEFAULT '{}'
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enterprise_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                password_hash TEXT NOT NULL,
                api_access BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations (id)
            )
        """)
        
        # API usage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time REAL,
                status_code INTEGER,
                FOREIGN KEY (organization_id) REFERENCES organizations (id)
            )
        """)
        
        # Enterprise analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enterprise_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations (id)
            )
        """)
        
        conn.commit()
        conn.close()

# Initialize database
db = EnterpriseDB()

# Pydantic models
class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    domain: str = Field(..., min_length=3, max_length=100)
    contact_email: str
    subscription_tier: str = "free"

class OrganizationResponse(BaseModel):
    id: int
    name: str
    domain: str
    subscription_tier: str
    api_key: str
    created_at: datetime
    last_active: datetime

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    organization_id: int
    api_access: bool
    created_at: datetime

class AnalyticsQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metric_types: Optional[List[str]] = None
    aggregation: str = "hour"  # hour, day, week, month

class ThreatIntelligence(BaseModel):
    threat_id: str
    threat_type: str
    severity: str
    source_ip: str
    target_assets: List[str]
    attack_vector: str
    timestamp: datetime
    metadata: Dict[str, Any]

# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key and return organization info"""
    api_key = credentials.credentials
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, domain, subscription_tier 
        FROM organizations 
        WHERE api_key = ?
    """, (api_key,))
    
    org = cursor.fetchone()
    conn.close()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return {
        "id": org[0],
        "name": org[1], 
        "domain": org[2],
        "subscription_tier": org[3]
    }

def log_api_usage(org_id: int, endpoint: str, method: str, response_time: float, status_code: int):
    """Log API usage for analytics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO api_usage (organization_id, endpoint, method, response_time, status_code)
        VALUES (?, ?, ?, ?, ?)
    """, (org_id, endpoint, method, response_time, status_code))
    
    conn.commit()
    conn.close()

# API Endpoints

@app.get("/enterprise/health")
async def enterprise_health():
    """Enterprise API health check"""
    return {
        "status": "healthy",
        "service": "HoneyNet Enterprise API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow()
    }

@app.post("/enterprise/organizations", response_model=OrganizationResponse)
async def create_organization(org: OrganizationCreate):
    """Create new enterprise organization"""
    # Generate API key
    api_key = f"hn_ent_{secrets.token_urlsafe(32)}"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO organizations (name, domain, subscription_tier, api_key)
            VALUES (?, ?, ?, ?)
        """, (org.name, org.domain, org.subscription_tier, api_key))
        
        org_id = cursor.lastrowid
        conn.commit()
        
        # Get created organization
        cursor.execute("""
            SELECT id, name, domain, subscription_tier, api_key, created_at, last_active
            FROM organizations WHERE id = ?
        """, (org_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return OrganizationResponse(
            id=result[0],
            name=result[1],
            domain=result[2],
            subscription_tier=result[3],
            api_key=result[4],
            created_at=datetime.fromisoformat(result[5]),
            last_active=datetime.fromisoformat(result[6])
        )
        
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Organization domain already exists"
        )

@app.get("/enterprise/analytics/dashboard")
async def get_enterprise_dashboard(org: dict = Depends(verify_api_key)):
    """Get enterprise dashboard data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get threat statistics
    cursor.execute("""
        SELECT COUNT(*) as total_threats,
               COUNT(CASE WHEN DATE(timestamp) = DATE('now') THEN 1 END) as today_threats,
               COUNT(CASE WHEN DATE(timestamp) >= DATE('now', '-7 days') THEN 1 END) as week_threats
        FROM enterprise_analytics 
        WHERE organization_id = ? AND metric_type = 'threat_detected'
    """, (org["id"],))
    
    threat_stats = cursor.fetchone()
    
    # Get honeypot statistics
    cursor.execute("""
        SELECT COUNT(*) as total_honeypots,
               AVG(metric_value) as avg_triggers
        FROM enterprise_analytics 
        WHERE organization_id = ? AND metric_type = 'honeypot_trigger'
    """, (org["id"],))
    
    honeypot_stats = cursor.fetchone()
    
    # Get API usage statistics
    cursor.execute("""
        SELECT COUNT(*) as total_calls,
               COUNT(CASE WHEN DATE(timestamp) = DATE('now') THEN 1 END) as today_calls,
               AVG(response_time) as avg_response_time
        FROM api_usage 
        WHERE organization_id = ?
    """, (org["id"],))
    
    api_stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "organization": org,
        "threats": {
            "total": threat_stats[0] or 0,
            "today": threat_stats[1] or 0,
            "this_week": threat_stats[2] or 0
        },
        "honeypots": {
            "total": honeypot_stats[0] or 0,
            "avg_triggers": round(honeypot_stats[1] or 0, 2)
        },
        "api_usage": {
            "total_calls": api_stats[0] or 0,
            "today_calls": api_stats[1] or 0,
            "avg_response_time": round(api_stats[2] or 0, 3)
        },
        "subscription": {
            "tier": org["subscription_tier"],
            "features": get_tier_features(org["subscription_tier"])
        }
    }

@app.get("/enterprise/analytics/threats")
async def get_threat_analytics(
    query: AnalyticsQuery = None,
    org: dict = Depends(verify_api_key)
):
    """Get detailed threat analytics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Build query based on parameters
    where_clause = "WHERE organization_id = ?"
    params = [org["id"]]
    
    if query and query.start_date:
        where_clause += " AND timestamp >= ?"
        params.append(query.start_date.isoformat())
    
    if query and query.end_date:
        where_clause += " AND timestamp <= ?"
        params.append(query.end_date.isoformat())
    
    # Get threat timeline
    cursor.execute(f"""
        SELECT DATE(timestamp) as date, 
               COUNT(*) as threat_count,
               metric_type
        FROM enterprise_analytics 
        {where_clause} AND metric_type LIKE 'threat_%'
        GROUP BY DATE(timestamp), metric_type
        ORDER BY date DESC
        LIMIT 30
    """, params)
    
    timeline = cursor.fetchall()
    
    # Get threat types distribution
    cursor.execute(f"""
        SELECT JSON_EXTRACT(metadata, '$.threat_type') as threat_type,
               COUNT(*) as count
        FROM enterprise_analytics 
        {where_clause} AND metric_type = 'threat_detected'
        GROUP BY threat_type
        ORDER BY count DESC
    """, params)
    
    threat_types = cursor.fetchall()
    
    conn.close()
    
    return {
        "timeline": [
            {
                "date": row[0],
                "threat_count": row[1],
                "metric_type": row[2]
            }
            for row in timeline
        ],
        "threat_types": [
            {
                "type": row[0] or "unknown",
                "count": row[1]
            }
            for row in threat_types
        ]
    }

@app.post("/enterprise/threats/report")
async def report_threat(threat: ThreatIntelligence, org: dict = Depends(verify_api_key)):
    """Report a new threat to the enterprise system"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Store threat in analytics
    cursor.execute("""
        INSERT INTO enterprise_analytics (organization_id, metric_type, metric_value, metadata)
        VALUES (?, 'threat_detected', 1, ?)
    """, (org["id"], json.dumps(threat.dict())))
    
    conn.commit()
    conn.close()
    
    # Log API usage
    log_api_usage(org["id"], "/enterprise/threats/report", "POST", 0.1, 200)
    
    return {
        "status": "success",
        "message": "Threat reported successfully",
        "threat_id": threat.threat_id
    }

@app.get("/enterprise/subscription/features")
async def get_subscription_features(org: dict = Depends(verify_api_key)):
    """Get features available for current subscription tier"""
    features = get_tier_features(org["subscription_tier"])
    
    return {
        "organization": org["name"],
        "tier": org["subscription_tier"],
        "features": features
    }

def get_tier_features(tier: str) -> Dict[str, Any]:
    """Get features for subscription tier"""
    features = {
        "free": {
            "api_calls_per_month": 1000,
            "threat_reports": True,
            "basic_analytics": True,
            "email_alerts": False,
            "custom_integrations": False,
            "priority_support": False,
            "advanced_analytics": False
        },
        "professional": {
            "api_calls_per_month": 50000,
            "threat_reports": True,
            "basic_analytics": True,
            "email_alerts": True,
            "custom_integrations": True,
            "priority_support": False,
            "advanced_analytics": True,
            "custom_dashboards": True
        },
        "enterprise": {
            "api_calls_per_month": -1,  # Unlimited
            "threat_reports": True,
            "basic_analytics": True,
            "email_alerts": True,
            "custom_integrations": True,
            "priority_support": True,
            "advanced_analytics": True,
            "custom_dashboards": True,
            "dedicated_support": True,
            "sla_guarantee": "99.9%"
        }
    }
    
    return features.get(tier, features["free"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
