"""
HoneyNet Enhanced Main Server
שרת מרכזי משופר עם כל האופטימיזציות החדשות
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our enhanced modules
from core.memory_manager import memory_manager
from core.database_optimizer import db_optimizer
from core.event_bus import event_bus, Event, EventType, EventPriority
from core.zero_trust_security import zero_trust_manager
from core.api_monetization import api_monetization, APIEndpointType
from core.swarm_intelligence import SwarmIntelligence
from core.defense_engine import DefenseEngine
from core.threat_analyzer import ThreatAnalyzer
from core.gamification import GamificationEngine
from core.blockchain_ledger import BlockchainThreatLedger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HoneyNet Enhanced API",
    description="Advanced Cybersecurity Platform with Optimized Performance",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global components
components = {
    "swarm_intelligence": None,
    "defense_engine": None,
    "threat_analyzer": None,
    "gamification": None,
    "blockchain": None
}

# Performance monitoring
performance_stats = {
    "requests_total": 0,
    "requests_per_second": 0.0,
    "avg_response_time": 0.0,
    "error_count": 0,
    "last_reset": time.time()
}


# Middleware for API monitoring and security
@app.middleware("http")
async def api_middleware(request: Request, call_next):
    """Middleware לניטור API ואבטחה"""
    start_time = time.time()
    
    # Update performance stats
    performance_stats["requests_total"] += 1
    
    # Extract user info (simplified)
    user_id = request.headers.get("X-User-ID", "anonymous")
    api_key = request.headers.get("X-API-Key")
    
    # Security validation for API endpoints
    if request.url.path.startswith("/api/"):
        # Skip auth for public endpoints
        public_endpoints = ["/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"]
        
        if request.url.path not in public_endpoints:
            # Validate API access
            endpoint_type = _determine_endpoint_type(request.url.path)
            
            if user_id != "anonymous":
                # Check API monetization limits
                allowed, validation_info = await api_monetization.validate_api_request(
                    user_id, request.url.path, endpoint_type
                )
                
                if not allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "API limit exceeded",
                            "details": validation_info,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # ms
        
        # Update performance metrics
        current_avg = performance_stats["avg_response_time"]
        total_requests = performance_stats["requests_total"]
        performance_stats["avg_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Track API usage if authenticated
        if user_id != "anonymous" and request.url.path.startswith("/api/"):
            endpoint_type = _determine_endpoint_type(request.url.path)
            
            await api_monetization.track_api_usage(
                user_id=user_id,
                endpoint=request.url.path,
                endpoint_type=endpoint_type,
                response_time_ms=response_time,
                status_code=response.status_code,
                request_size=len(await request.body()) if hasattr(request, 'body') else 0,
                response_size=0,  # Will be calculated later
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("User-Agent", "unknown")
            )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-Server-Version"] = "2.0.0"
        
        return response
        
    except Exception as e:
        performance_stats["error_count"] += 1
        logger.error(f"Request failed: {e}")
        
        # Publish error event
        await event_bus.publish(Event(
            event_id=f"api_error_{int(time.time())}",
            event_type=EventType.SYSTEM_ERROR,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="enhanced_main_server",
            data={
                "error": str(e),
                "endpoint": request.url.path,
                "user_id": user_id,
                "response_time": (time.time() - start_time) * 1000
            }
        ))
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat(),
                "request_id": f"req_{int(time.time())}"
            }
        )


def _determine_endpoint_type(path: str) -> APIEndpointType:
    """קביעת סוג נקודת קצה של API"""
    if "/threats" in path:
        return APIEndpointType.THREAT_DETECTION
    elif "/honeypots" in path:
        return APIEndpointType.HONEYPOT_MANAGEMENT
    elif "/analytics" in path:
        return APIEndpointType.ANALYTICS
    elif "/reports" in path:
        return APIEndpointType.REPORTING
    elif "/monitor" in path or "/realtime" in path:
        return APIEndpointType.REAL_TIME_MONITORING
    elif "/intelligence" in path:
        return APIEndpointType.THREAT_INTELLIGENCE
    else:
        return APIEndpointType.CUSTOM_INTEGRATION


# Startup event
@app.on_event("startup")
async def startup_event():
    """אירוע התחלה - אתחול כל המערכות"""
    logger.info("🚀 Starting HoneyNet Enhanced Server...")
    
    try:
        # Initialize core systems
        logger.info("Initializing core systems...")
        
        # 1. Memory Manager
        await memory_manager.start_monitoring()
        logger.info("✅ Memory Manager initialized")
        
        # 2. Database Optimizer
        await db_optimizer.initialize()
        logger.info("✅ Database Optimizer initialized")
        
        # 3. Event Bus
        await event_bus.start()
        logger.info("✅ Event Bus initialized")
        
        # 4. Zero-Trust Security
        # Zero-Trust Manager is ready to use without initialization
        logger.info("✅ Zero-Trust Security initialized")
        
        # 5. API Monetization
        # API Monetization is ready to use without initialization
        logger.info("✅ API Monetization initialized")
        
        # Initialize HoneyNet components
        logger.info("Initializing HoneyNet components...")
        
        # 6. Swarm Intelligence
        components["swarm_intelligence"] = SwarmIntelligence()
        await components["swarm_intelligence"].start_swarm()
        logger.info("✅ Swarm Intelligence initialized")
        
        # 7. Defense Engine
        components["defense_engine"] = DefenseEngine()
        await components["defense_engine"].start()
        logger.info("✅ Defense Engine initialized")
        
        # 8. Threat Analyzer
        components["threat_analyzer"] = ThreatAnalyzer()
        await components["threat_analyzer"].start()
        logger.info("✅ Threat Analyzer initialized")
        
        # 9. Gamification Engine
        components["gamification"] = GamificationEngine()
        await components["gamification"].initialize()
        logger.info("✅ Gamification Engine initialized")
        
        # 10. Blockchain Ledger
        components["blockchain"] = BlockchainThreatLedger()
        # BlockchainThreatLedger doesn't have initialize method, it's ready to use
        logger.info("✅ Blockchain Ledger initialized")
        
        # Publish startup event
        await event_bus.publish(Event(
            event_id=f"server_startup_{int(time.time())}",
            event_type=EventType.SYSTEM_STARTED,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="enhanced_main_server",
            data={
                "message": "HoneyNet Enhanced Server started successfully",
                "version": "2.0.0",
                "components": list(components.keys())
            }
        ))
        
        logger.info("🎉 HoneyNet Enhanced Server started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """אירוע סגירה - ניקוי משאבים"""
    logger.info("🛑 Shutting down HoneyNet Enhanced Server...")
    
    try:
        # Publish shutdown event
        await event_bus.publish(Event(
            event_id=f"server_shutdown_{int(time.time())}",
            event_type=EventType.SYSTEM_STOPPED,
            priority=EventPriority.HIGH,
            timestamp=datetime.now(),
            source="enhanced_main_server",
            data={"message": "HoneyNet Enhanced Server shutting down"}
        ))
        
        # Stop HoneyNet components
        if components["swarm_intelligence"]:
            await components["swarm_intelligence"].stop_swarm()
        
        if components["defense_engine"]:
            await components["defense_engine"].stop()
        
        if components["threat_analyzer"]:
            await components["threat_analyzer"].stop()
        
        # Stop core systems
        await event_bus.stop()
        await memory_manager.stop_monitoring()
        await db_optimizer.cleanup()
        
        logger.info("✅ Server shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """בדיקת בריאות המערכת"""
    try:
        # Check all systems
        system_health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "uptime": time.time() - performance_stats["last_reset"],
            "components": {}
        }
        
        # Memory health
        memory_health = memory_manager.get_system_health()
        system_health["components"]["memory"] = memory_health["memory"]
        
        # Database health
        db_stats = await db_optimizer.get_performance_stats()
        system_health["components"]["database"] = {
            "status": "healthy" if db_stats["connection_stats"]["active_connections"] > 0 else "warning",
            "connections": db_stats["connection_stats"]["active_connections"]
        }
        
        # Event bus health
        event_stats = event_bus.get_stats()
        system_health["components"]["event_bus"] = {
            "status": "healthy" if event_stats["processing_active"] else "stopped",
            "active_workers": event_stats["active_workers"]
        }
        
        # API monetization health
        monetization_stats = api_monetization.get_monetization_stats()
        system_health["components"]["api_monetization"] = {
            "status": "healthy",
            "active_subscriptions": monetization_stats["stats"]["active_subscriptions"]
        }
        
        # Performance stats
        current_time = time.time()
        time_diff = current_time - performance_stats["last_reset"]
        if time_diff > 0:
            performance_stats["requests_per_second"] = performance_stats["requests_total"] / time_diff
        
        system_health["performance"] = {
            "requests_total": performance_stats["requests_total"],
            "requests_per_second": performance_stats["requests_per_second"],
            "avg_response_time_ms": performance_stats["avg_response_time"],
            "error_count": performance_stats["error_count"]
        }
        
        return system_health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# Dashboard endpoint
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """קבלת סטטיסטיקות לדשבורד"""
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "status": "operational",
                "uptime": time.time() - performance_stats["last_reset"],
                "version": "2.0.0"
            },
            "threats": {},
            "honeypots": {},
            "swarm": {},
            "performance": performance_stats.copy()
        }
        
        # Get component stats
        if components["defense_engine"]:
            stats["threats"] = components["defense_engine"].get_statistics()
        
        if components["swarm_intelligence"]:
            stats["swarm"] = components["swarm_intelligence"].get_swarm_status()
        
        # Get gamification stats
        if components["gamification"]:
            stats["gamification"] = await components["gamification"].get_user_stats("system")
        
        return stats
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Real-time monitoring endpoint
@app.get("/api/monitor/realtime")
async def get_realtime_data():
    """נתונים בזמן אמת לניטור"""
    try:
        realtime_data = {
            "timestamp": datetime.now().isoformat(),
            "active_threats": 0,
            "honeypots_triggered": 0,
            "swarm_agents": 0,
            "system_load": memory_manager.get_system_health(),
            "recent_events": await event_bus.get_event_history(limit=10)
        }
        
        # Get real-time component data
        if components["defense_engine"]:
            defense_stats = components["defense_engine"].get_statistics()
            realtime_data["active_threats"] = len(defense_stats.get("active_threats", {}))
        
        if components["swarm_intelligence"]:
            swarm_status = components["swarm_intelligence"].get_swarm_status()
            realtime_data["swarm_agents"] = swarm_status.get("active_agents", 0)
        
        return realtime_data
        
    except Exception as e:
        logger.error(f"Real-time data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# API statistics endpoint
@app.get("/api/admin/stats")
async def get_api_stats():
    """סטטיסטיקות API למנהלים"""
    try:
        api_stats = {
            "monetization": api_monetization.get_monetization_stats(),
            "database": await db_optimizer.get_performance_stats(),
            "event_bus": event_bus.get_stats(),
            "security": zero_trust_manager.get_security_stats(),
            "memory": memory_manager.get_system_health(),
            "performance": performance_stats.copy()
        }
        
        return api_stats
        
    except Exception as e:
        logger.error(f"API stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files
if os.path.exists("client/web"):
    app.mount("/", StaticFiles(directory="client/web", html=True), name="static")


def main():
    """הפעלת השרת המשופר"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=False,  # Disable in production
        workers=1,  # Single worker for now due to shared state
        loop="asyncio"
    )
    
    server = uvicorn.Server(config)
    
    try:
        logger.info("🚀 Starting HoneyNet Enhanced Server on http://0.0.0.0:8000")
        server.run()
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
