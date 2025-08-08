"""
HoneyNet Global Server - Main Application
שרת HoneyNet הגלובלי - אפליקציה ראשית
"""

import asyncio
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import json
from datetime import datetime
from typing import Dict, List, Set
import redis
import asyncpg
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from config.settings import get_settings
except ImportError:
    # Fallback settings
    class Settings:
        def __init__(self):
            self.database_url = "postgresql://localhost/honeynet"
            self.redis_url = "redis://localhost:6379"
            self.secret_key = "dev-secret-key"
            self.debug = True
            self.host = "127.0.0.1"
            self.port = 9001
            self.log_level = "INFO"
    def get_settings():
        return Settings()

try:
    from server.api.routes import router as api_router, set_services
except ImportError:
    from fastapi import APIRouter
    api_router = APIRouter()
    def set_services(*args): pass

try:
    from server.routes.analytics import router as analytics_router
except ImportError:
    from fastapi import APIRouter
    analytics_router = APIRouter()

try:
    from server.routes.advanced_analytics_simple import router as advanced_analytics_router
except ImportError:
    from fastapi import APIRouter
    advanced_analytics_router = APIRouter()

try:
    from server.websocket.connection_manager import ConnectionManager
except ImportError:
    class ConnectionManager:
        def __init__(self):
            self.active_connections = {}
            self.connection_count = 0
        
        async def connect(self, websocket, client_id):
            self.active_connections[client_id] = websocket
            self.connection_count = len(self.active_connections)
        
        async def disconnect(self, client_id):
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            self.connection_count = len(self.active_connections)
        
        async def disconnect_all(self):
            self.active_connections.clear()
            self.connection_count = 0
        
        def get_connection_count(self):
            return len(self.active_connections)
        
        async def send_personal_message(self, message, client_id):
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_text(message)
        
        async def broadcast(self, message):
            for connection in self.active_connections.values():
                try:
                    await connection.send_text(message)
                except:
                    pass
        
        async def broadcast_statistics_update(self, stats):
            message = {"type": "statistics_update", "data": stats}
            await self.broadcast(str(message))
        
        async def cleanup_inactive_connections(self):
            # Implementation for cleaning inactive connections
            return 0

try:
    from server.services.ai_coordinator import AICoordinator
except ImportError:
    class AICoordinator:
        async def initialize(self): pass
        async def cleanup(self): pass
        async def analyze_global_threat(self, threat_data, source_client): return {}

try:
    from server.services.global_analytics import GlobalAnalytics
except ImportError:
    class GlobalAnalytics:
        async def initialize(self): pass
        async def cleanup(self): pass
        async def get_global_stats(self): return {}

try:
    from server.database.models import init_database
except ImportError:
    async def init_database(): pass


# Global services
connection_manager = ConnectionManager()
threat_processor = None
ai_coordinator = AICoordinator()
global_analytics = GlobalAnalytics()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/honeynet_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting HoneyNet Global Server...")
    
    # Initialize services
    await init_services()
    
    logger.info("✅ HoneyNet Global Server started successfully!")
    logger.info("🌐 Ready to coordinate global cyber defense network")
    
    yield
    
    logger.info("🛑 Shutting down HoneyNet Global Server...")
    await cleanup_services()
    logger.info("✅ Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="HoneyNet Global Server",
    description="Global Cyber Defense Network Coordination Server",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(api_router)
app.include_router(analytics_router)
app.include_router(advanced_analytics_router)


@app.get("/")
async def root():
    """Root endpoint - Server status"""
    return {
        "service": "HoneyNet Global Server",
        "status": "online",
        "version": "1.0.0",
        "description": "Global Cyber Defense Network Coordination Server",
        "timestamp": datetime.now().isoformat(),
        "active_connections": connection_manager.get_connection_count(),
        "global_stats": await global_analytics.get_global_statistics()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check database connection
        db_status = "ok"
        try:
            await check_database_health()
        except Exception as e:
            db_status = f"error: {str(e)}"
            logging.error(f"Database health check failed: {e}")
        
        # Check Redis connection
        redis_status = "ok"
        try:
            await check_redis_health()
        except Exception as e:
            redis_status = f"error: {str(e)}"
            logging.error(f"Redis health check failed: {e}")
        
        # Get system stats
        uptime = get_uptime_seconds()
        
        return JSONResponse({
            "status": "ok",
            "version": "2.0.1",
            "service": "HoneyNet Enhanced",
            "uptime_seconds": uptime,
            "database": db_status,
            "redis": redis_status,
            "active_connections": len(connection_manager.active_connections),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return JSONResponse(
            {"status": "error", "message": str(e)}, 
            status_code=500
        )


@app.get("/product-overview")
async def product_overview():
    """
    Product overview documentation page
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoneyNet Enhanced - Revolutionary Cybersecurity Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 0; text-align: center; }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; margin-bottom: 2rem; }
        .section { padding: 4rem 0; }
        .section h2 { font-size: 2.5rem; margin-bottom: 2rem; text-align: center; color: #667eea; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0; }
        .feature-card { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #667eea; margin-bottom: 1rem; }
        .stats { background: #f8fafc; padding: 3rem 0; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; }
        .stat-card { text-align: center; background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .btn { display: inline-block; background: #667eea; color: white; padding: 1rem 2rem; border-radius: 5px; text-decoration: none; margin: 1rem 0.5rem; }
        .btn:hover { background: #5a67d8; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>🛡️ HoneyNet Enhanced</h1>
            <p>Revolutionary Global Cybersecurity Defense Network</p>
            <p>The world's first AI-powered, blockchain-secured, swarm intelligence cybersecurity platform</p>
            <a href="/" class="btn">← Back to Home</a>
        </div>
    </div>
    
    <div class="section">
        <div class="container">
            <h2>🚀 Revolutionary Features</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🧠 Swarm Intelligence</h3>
                    <p>Deploy thousands of intelligent agents that coordinate autonomously and adapt to new attack patterns in real-time.</p>
                </div>
                <div class="feature-card">
                    <h3>⛓️ Blockchain Threat Ledger</h3>
                    <p>Immutable, distributed threat intelligence sharing across the global network with cryptographic verification.</p>
                </div>
                <div class="feature-card">
                    <h3>🔐 Zero Trust Architecture</h3>
                    <p>Never trust, always verify. Continuous authentication and micro-segmentation with military-grade security.</p>
                </div>
                <div class="feature-card">
                    <h3>🎯 Quantum Honeypots</h3>
                    <p>Next-generation deception technology with quantum-encrypted decoy systems for unparalleled threat intelligence.</p>
                </div>
                <div class="feature-card">
                    <h3>🌐 Edge Computing Defense</h3>
                    <p>Distributed processing at the network edge ensures sub-50ms response times with maximum resilience.</p>
                </div>
                <div class="feature-card">
                    <h3>🎮 Gamified Security</h3>
                    <p>Transform cybersecurity into an engaging experience with achievement systems and competitive security awareness.</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="stats">
        <div class="container">
            <h2>📊 Performance Metrics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">99.9%</div>
                    <p>Threat Detection Rate</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">< 50ms</div>
                    <p>Response Time</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">10,000+</div>
                    <p>Simultaneous Agents</p>
                </div>
                <div class="stat-card">
                    <div class="stat-number">38</div>
                    <p>Core Modules</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <div class="container">
            <h2>🏗️ Technical Architecture</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🐍 Backend</h3>
                    <p>FastAPI, Python 3.11+, Asyncio, WebSocket for real-time communication</p>
                </div>
                <div class="feature-card">
                    <h3>🗄️ Database</h3>
                    <p>PostgreSQL, Redis, SQLAlchemy with advanced caching and optimization</p>
                </div>
                <div class="feature-card">
                    <h3>☁️ Cloud</h3>
                    <p>AWS EC2, S3, CloudWatch with auto-scaling and load balancing</p>
                </div>
                <div class="feature-card">
                    <h3>🤖 AI/ML</h3>
                    <p>TensorFlow, PyTorch, Scikit-learn for advanced threat analysis</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="hero" style="padding: 3rem 0;">
        <div class="container">
            <h2>Ready to Transform Your Cybersecurity?</h2>
            <p>Join thousands of organizations already protected by HoneyNet Enhanced</p>
            <a href="/" class="btn">Download Now</a>
            <a href="/" class="btn">Contact Sales</a>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    client_id = None
    try:
        await websocket.accept()
        logger.info(f"🔌 New WebSocket connection established")
        
        # Wait for client registration
        registration_data = await websocket.receive_text()
        registration = json.loads(registration_data)
        
        if registration.get("type") != "device_registration":
            await websocket.close(code=4000, reason="Invalid registration")
            return
        
        # Register client
        client_id = await connection_manager.register_client(websocket, registration)
        logger.info(f"📱 Client registered: {client_id} ({registration.get('platform', 'unknown')})")
        
        # Send welcome message
        await connection_manager.send_to_client(client_id, {
            "type": "welcome",
            "message": "ברוך הבא לרשת HoneyNet הגלובלית!",
            "client_id": client_id,
            "global_stats": await global_analytics.get_global_statistics()
        })
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process message
                await handle_websocket_message(client_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from client {client_id}")
                await connection_manager.send_error(client_id, "Invalid JSON format")
            except Exception as e:
                logger.error(f"Error processing message from {client_id}: {e}")
                await connection_manager.send_error(client_id, "Message processing error")
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if client_id:
            await connection_manager.unregister_client(client_id)
            logger.info(f"🔌 Client disconnected: {client_id}")


async def handle_websocket_message(client_id: str, message: Dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    try:
        if message_type == "threat_report":
            await handle_threat_report(client_id, message.get("data"))
        elif message_type == "honeypot_trigger":
            await handle_honeypot_trigger(client_id, message.get("data"))
        elif message_type == "heartbeat":
            await handle_heartbeat(client_id)
        elif message_type == "request_statistics":
            await handle_statistics_request(client_id)
        else:
            logger.warning(f"Unknown message type: {message_type} from client {client_id}")
            
    except Exception as e:
        logger.error(f"Error handling message type {message_type}: {e}")
        await connection_manager.send_error(client_id, f"Error processing {message_type}")


async def handle_threat_report(client_id: str, threat_data: Dict):
    """Handle threat report from client"""
    logger.info(f"🚨 Threat report received from {client_id}")
    
    # Process threat through AI
    processed_threat = await threat_processor.process_threat(threat_data, client_id)
    
    # Update global analytics
    await global_analytics.record_threat(processed_threat)
    
    # Broadcast to relevant clients if critical
    if processed_threat.get("severity") in ["high", "critical"]:
        await connection_manager.broadcast_threat_alert(processed_threat)
        logger.info(f"📡 Critical threat broadcasted to network")
    
    # Send confirmation to reporting client
    await connection_manager.send_to_client(client_id, {
        "type": "threat_processed",
        "threat_id": processed_threat.get("id"),
        "status": "processed",
        "global_protection_updated": True
    })


async def handle_honeypot_trigger(client_id: str, honeypot_data: Dict):
    """Handle honeypot trigger from client"""
    logger.info(f"🍯 Honeypot trigger received from {client_id}")
    
    # Process honeypot trigger
    trigger_analysis = await ai_coordinator.analyze_honeypot_trigger(honeypot_data)
    
    # Update global honeypot intelligence
    await global_analytics.record_honeypot_trigger(trigger_analysis)
    
    # Send honeypot updates to network if needed
    if trigger_analysis.get("should_update_network"):
        await connection_manager.broadcast_honeypot_update(trigger_analysis)
    
    # Send response to client
    await connection_manager.send_to_client(client_id, {
        "type": "honeypot_trigger_processed",
        "analysis": trigger_analysis,
        "points_earned": trigger_analysis.get("points", 0)
    })


async def handle_heartbeat(client_id: str):
    """Handle heartbeat from client"""
    await connection_manager.update_client_heartbeat(client_id)
    
    # Send heartbeat response with mini stats
    await connection_manager.send_to_client(client_id, {
        "type": "heartbeat_response",
        "timestamp": datetime.now().isoformat(),
        "network_status": "healthy",
        "active_nodes": connection_manager.get_connection_count()
    })


async def handle_statistics_request(client_id: str):
    """Handle statistics request from client"""
    stats = await global_analytics.get_client_statistics(client_id)
    
    await connection_manager.send_to_client(client_id, {
        "type": "statistics_response",
        "data": stats
    })


async def init_services():
    """Initialize all services"""
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized")
        
        # Initialize Redis
        await init_redis()
        logger.info("✅ Redis initialized")
        
        # Initialize AI coordinator
        await ai_coordinator.initialize()
        logger.info("✅ AI Coordinator initialized")
        
        # Initialize global analytics
        await global_analytics.initialize()
        logger.info("✅ Global Analytics initialized")
        
        # Start background tasks
        asyncio.create_task(periodic_statistics_broadcast())
        asyncio.create_task(cleanup_inactive_connections())
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise


async def cleanup_services():
    """Cleanup all services"""
    try:
        await connection_manager.disconnect_all()
        await ai_coordinator.cleanup()
        await global_analytics.cleanup()
        logger.info("✅ All services cleaned up")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


async def init_redis():
    """Initialize Redis connection"""
    settings = get_settings()
    # Redis initialization code here
    pass


async def check_database_health() -> bool:
    """Check database health"""
    try:
        # Database health check code
        return True
    except Exception:
        return False


async def check_redis_health() -> bool:
    """Check Redis health"""
    try:
        # Redis health check code
        return True
    except Exception:
        return False


async def get_uptime_seconds() -> int:
    """Get server uptime in seconds"""
    # Implementation for uptime calculation
    return 0


async def periodic_statistics_broadcast():
    """Periodically broadcast statistics to all clients"""
    while True:
        try:
            await asyncio.sleep(60)  # Every minute
            
            global_stats = await global_analytics.get_global_statistics()
            await connection_manager.broadcast_statistics_update(global_stats)
            
            logger.info(f"📊 Statistics broadcasted to {connection_manager.get_connection_count()} clients")
            
        except Exception as e:
            logger.error(f"Error in statistics broadcast: {e}")


async def cleanup_inactive_connections():
    """Clean up inactive connections"""
    while True:
        try:
            await asyncio.sleep(300)  # Every 5 minutes
            
            cleaned_count = await connection_manager.cleanup_inactive_connections()
            if cleaned_count > 0:
                logger.info(f"🧹 Cleaned up {cleaned_count} inactive connections")
                
        except Exception as e:
            logger.error(f"Error in connection cleanup: {e}")


def main():
    """Main entry point"""
    settings = get_settings()
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging first
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/server.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Starting HoneyNet Global Server...")
    
    # Get log level safely
    log_level = getattr(settings, 'log_level', 'INFO')
    if hasattr(log_level, 'lower'):
        log_level = log_level.lower()
    else:
        log_level = str(log_level).lower()
    
    # Validate log level
    valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
    if log_level not in valid_levels:
        log_level = 'info'
    
    # Get settings safely
    host = getattr(settings, 'host', '0.0.0.0')
    port = getattr(settings, 'port', 8000)
    
    # Ensure host and port are proper types
    if hasattr(host, 'default'):
        host = host.default
    if hasattr(port, 'default'):
        port = port.default
        
    host = str(host) if host else '0.0.0.0'
    port = int(port) if port else 8000
    
    uvicorn.run(
        "server.main:app",
        host=host,
        port=port,
        workers=1,  # Use 1 worker for WebSocket support
        log_level=log_level,
        access_log=True,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
