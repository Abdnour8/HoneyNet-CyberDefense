"""
HoneyNet Global Server - API Routes
נתיבי API לשרת HoneyNet הגלובלי
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json

from ..services.global_analytics import GlobalAnalytics
from ..services.ai_coordinator import AICoordinator
from ..websocket.connection_manager import ConnectionManager


# Security
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global instances (will be injected)
analytics: Optional[GlobalAnalytics] = None
ai_coordinator: Optional[AICoordinator] = None
connection_manager: Optional[ConnectionManager] = None


def set_services(analytics_service: GlobalAnalytics, ai_service: AICoordinator, conn_manager: ConnectionManager):
    """הגדרת שירותים גלובליים"""
    global analytics, ai_coordinator, connection_manager
    analytics = analytics_service
    ai_coordinator = ai_service
    connection_manager = conn_manager


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """אימות טוקן"""
    # For demo purposes, accept any token
    # In production, implement proper JWT validation
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials


# Health and Status Routes

@router.get("/health")
async def health_check():
    """בדיקת בריאות השרת"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "analytics": analytics is not None,
            "ai_coordinator": ai_coordinator is not None,
            "connection_manager": connection_manager is not None
        }
    }


@router.get("/status")
async def server_status():
    """סטטוס מפורט של השרת"""
    if not analytics:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    stats = analytics.get_statistics_summary()
    
    return {
        "server_status": "operational",
        "uptime": "99.9%",  # Placeholder
        "active_connections": len(connection_manager.active_connections) if connection_manager else 0,
        "statistics": stats,
        "last_updated": datetime.now().isoformat()
    }


# Statistics and Analytics Routes

@router.get("/statistics/global")
async def get_global_statistics(token: str = Depends(verify_token)):
    """קבלת סטטיסטיקות גלובליות"""
    if not analytics:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        stats = await analytics.get_global_statistics()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting global statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.get("/statistics/client/{client_id}")
async def get_client_statistics(client_id: str, token: str = Depends(verify_token)):
    """קבלת סטטיסטיקות לקוח ספציפי"""
    if not analytics:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        stats = await analytics.get_client_statistics(client_id)
        return {
            "success": True,
            "client_id": client_id,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting client statistics for {client_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve client statistics")


@router.get("/statistics/trends")
async def get_threat_trends(
    hours: int = Query(24, description="Time period in hours"),
    token: str = Depends(verify_token)
):
    """קבלת מגמות איומים"""
    if not analytics:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        trends = await analytics.get_threat_trends(hours)
        return {
            "success": True,
            "time_period_hours": hours,
            "trends": [
                {
                    "threat_type": trend.threat_type,
                    "current_count": trend.current_count,
                    "previous_count": trend.previous_count,
                    "trend_direction": trend.trend_direction,
                    "trend_percentage": trend.trend_percentage,
                    "geographic_hotspots": trend.geographic_hotspots,
                    "time_pattern": trend.time_pattern
                }
                for trend in trends
            ]
        }
    except Exception as e:
        logger.error(f"Error getting threat trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve threat trends")


# Threat Management Routes

@router.post("/threats/report")
async def report_threat(
    threat_data: Dict,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """דיווח על איום חדש"""
    if not analytics or not ai_coordinator:
        raise HTTPException(status_code=503, detail="Required services not available")
    
    try:
        # Validate threat data
        required_fields = ["type", "source_ip", "client_id"]
        for field in required_fields:
            if field not in threat_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Record threat in analytics
        background_tasks.add_task(analytics.record_threat, threat_data)
        
        # Analyze threat with AI
        background_tasks.add_task(ai_coordinator.analyze_threat, threat_data)
        
        # Broadcast to network if severe
        if threat_data.get("severity") in ["high", "critical"]:
            broadcast_data = {
                "type": "threat_alert",
                "threat_type": threat_data["type"],
                "severity": threat_data["severity"],
                "source_region": threat_data.get("region", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            if connection_manager:
                background_tasks.add_task(
                    connection_manager.broadcast_to_all,
                    json.dumps(broadcast_data)
                )
        
        return {
            "success": True,
            "message": "Threat reported successfully",
            "threat_id": threat_data.get("id", "generated_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting threat: {e}")
        raise HTTPException(status_code=500, detail="Failed to report threat")


@router.get("/threats/active")
async def get_active_threats(
    limit: int = Query(50, description="Maximum number of threats to return"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    token: str = Depends(verify_token)
):
    """קבלת איומים פעילים"""
    if not analytics:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        # Get recent threats from analytics
        all_threats = analytics.threat_history[-limit:] if analytics.threat_history else []
        
        # Filter by severity if specified
        if severity:
            all_threats = [t for t in all_threats if t.get("severity") == severity]
        
        # Format response
        active_threats = []
        for threat in all_threats:
            active_threats.append({
                "id": threat.get("id"),
                "type": threat.get("type"),
                "severity": threat.get("severity"),
                "source_ip": threat.get("source_ip"),
                "region": threat.get("region"),
                "timestamp": threat.get("timestamp").isoformat() if threat.get("timestamp") else None,
                "blocked": threat.get("blocked", False)
            })
        
        return {
            "success": True,
            "count": len(active_threats),
            "threats": active_threats
        }
        
    except Exception as e:
        logger.error(f"Error getting active threats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active threats")


# Honeypot Management Routes

@router.post("/honeypots/trigger")
async def report_honeypot_trigger(
    honeypot_data: Dict,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """דיווח על הפעלת פיתיון"""
    if not analytics or not ai_coordinator:
        raise HTTPException(status_code=503, detail="Required services not available")
    
    try:
        # Validate honeypot data
        required_fields = ["honeypot_type", "client_id"]
        for field in required_fields:
            if field not in honeypot_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Record honeypot trigger
        background_tasks.add_task(analytics.record_honeypot_trigger, honeypot_data)
        
        # Analyze with AI
        background_tasks.add_task(ai_coordinator.analyze_honeypot_trigger, honeypot_data)
        
        return {
            "success": True,
            "message": "Honeypot trigger reported successfully",
            "trigger_id": honeypot_data.get("trigger_id", "generated_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting honeypot trigger: {e}")
        raise HTTPException(status_code=500, detail="Failed to report honeypot trigger")


@router.get("/honeypots/recommendations")
async def get_honeypot_recommendations(
    client_id: str = Query(..., description="Client ID for personalized recommendations"),
    token: str = Depends(verify_token)
):
    """קבלת המלצות לפיתיונות"""
    if not ai_coordinator:
        raise HTTPException(status_code=503, detail="AI Coordinator service not available")
    
    try:
        recommendations = await ai_coordinator.get_honeypot_recommendations(client_id)
        
        return {
            "success": True,
            "client_id": client_id,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting honeypot recommendations for {client_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")


# AI and Intelligence Routes

@router.get("/intelligence/predictions")
async def get_threat_predictions(
    hours_ahead: int = Query(24, description="Hours ahead to predict"),
    token: str = Depends(verify_token)
):
    """קבלת תחזיות איומים"""
    if not ai_coordinator:
        raise HTTPException(status_code=503, detail="AI Coordinator service not available")
    
    try:
        predictions = await ai_coordinator.predict_threats(hours_ahead)
        
        return {
            "success": True,
            "prediction_horizon_hours": hours_ahead,
            "predictions": predictions,
            "confidence_score": 0.85,  # Placeholder
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting threat predictions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get predictions")


@router.get("/intelligence/attack-patterns")
async def get_attack_patterns(
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    token: str = Depends(verify_token)
):
    """קבלת דפוסי התקפה"""
    if not ai_coordinator:
        raise HTTPException(status_code=503, detail="AI Coordinator service not available")
    
    try:
        patterns = await ai_coordinator.get_attack_patterns()
        
        # Filter by type if specified
        if pattern_type:
            patterns = [p for p in patterns if p.get("type") == pattern_type]
        
        return {
            "success": True,
            "pattern_count": len(patterns),
            "patterns": patterns
        }
        
    except Exception as e:
        logger.error(f"Error getting attack patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get attack patterns")


# Reports and Analytics Routes

@router.get("/reports/generate")
async def generate_threat_report(
    report_type: str = Query("daily", description="Report type: daily, weekly, monthly"),
    format: str = Query("json", description="Report format: json, pdf"),
    token: str = Depends(verify_token)
):
    """יצירת דוח איומים"""
    if not analytics:
        raise HTTPException(status_code=503, detail="Analytics service not available")
    
    try:
        if report_type not in ["daily", "weekly", "monthly"]:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        report = await analytics.generate_threat_report(report_type)
        
        if format == "json":
            return {
                "success": True,
                "report": report
            }
        elif format == "pdf":
            # TODO: Implement PDF generation
            raise HTTPException(status_code=501, detail="PDF format not yet implemented")
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


# Network Management Routes

@router.get("/network/nodes")
async def get_network_nodes(token: str = Depends(verify_token)):
    """קבלת רשימת נודים ברשת"""
    if not connection_manager:
        raise HTTPException(status_code=503, detail="Connection manager not available")
    
    try:
        nodes = []
        for client_id, client_info in connection_manager.active_connections.items():
            nodes.append({
                "client_id": client_id,
                "connected_at": client_info.get("connected_at"),
                "last_heartbeat": client_info.get("last_heartbeat"),
                "client_type": client_info.get("client_type", "unknown"),
                "region": client_info.get("region", "unknown"),
                "version": client_info.get("version", "unknown")
            })
        
        return {
            "success": True,
            "total_nodes": len(nodes),
            "nodes": nodes
        }
        
    except Exception as e:
        logger.error(f"Error getting network nodes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get network nodes")


@router.post("/network/broadcast")
async def broadcast_message(
    message_data: Dict,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """שידור הודעה לכל הרשת"""
    if not connection_manager:
        raise HTTPException(status_code=503, detail="Connection manager not available")
    
    try:
        # Validate message data
        if "type" not in message_data or "content" not in message_data:
            raise HTTPException(status_code=400, detail="Message must have 'type' and 'content'")
        
        # Add timestamp
        message_data["timestamp"] = datetime.now().isoformat()
        
        # Broadcast message
        background_tasks.add_task(
            connection_manager.broadcast_to_all,
            json.dumps(message_data)
        )
        
        return {
            "success": True,
            "message": "Broadcast sent successfully",
            "recipients": len(connection_manager.active_connections)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")


# Configuration Routes

@router.get("/config/global")
async def get_global_config(token: str = Depends(verify_token)):
    """קבלת תצורה גלובלית"""
    return {
        "success": True,
        "config": {
            "threat_detection_sensitivity": "high",
            "auto_block_enabled": True,
            "honeypot_rotation_interval": 3600,  # 1 hour
            "ai_analysis_enabled": True,
            "global_sharing_enabled": True,
            "max_clients_per_region": 10000,
            "heartbeat_interval": 30,  # seconds
            "threat_alert_threshold": "medium"
        }
    }


@router.post("/config/update")
async def update_global_config(
    config_data: Dict,
    token: str = Depends(verify_token)
):
    """עדכון תצורה גלובלית"""
    try:
        # Validate and update configuration
        # In a real implementation, this would update the actual configuration
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "updated_fields": list(config_data.keys())
        }
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")


# Error handlers

@router.get("/test/error")
async def test_error():
    """בדיקת טיפול בשגיאות"""
    raise HTTPException(status_code=500, detail="This is a test error")


# Export router
__all__ = ["router", "set_services"]
