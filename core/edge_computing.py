"""
HoneyNet Edge Computing System
מערכת Edge Computing לעיבוד מקומי ואבטחת פרטיות
"""

import asyncio
import logging
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import hashlib
import secrets


class EdgeNodeType(Enum):
    """סוגי נודי Edge"""
    IOT_DEVICE = "iot_device"
    MOBILE_DEVICE = "mobile_device"
    ROUTER = "router"
    SMART_CAMERA = "smart_camera"
    INDUSTRIAL_SENSOR = "industrial_sensor"
    VEHICLE = "vehicle"
    SMART_HOME_HUB = "smart_home_hub"
    MICRO_DATACENTER = "micro_datacenter"


class EdgeCapability(Enum):
    """יכולות Edge"""
    THREAT_DETECTION = "threat_detection"
    DATA_PROCESSING = "data_processing"
    LOCAL_STORAGE = "local_storage"
    NETWORK_MONITORING = "network_monitoring"
    ENCRYPTION = "encryption"
    AI_INFERENCE = "ai_inference"
    HONEYPOT_HOSTING = "honeypot_hosting"
    MESH_NETWORKING = "mesh_networking"


@dataclass
class EdgeNode:
    """נוד Edge"""
    node_id: str
    node_type: EdgeNodeType
    location: Tuple[float, float]  # lat, lon
    capabilities: List[EdgeCapability]
    cpu_cores: int
    memory_mb: int
    storage_gb: int
    network_bandwidth_mbps: int
    battery_level: Optional[float] = None
    last_heartbeat: datetime = field(default_factory=datetime.now)
    status: str = "online"
    workload: float = 0.0  # 0-1 scale
    trust_score: float = 0.8
    firmware_version: str = "1.0.0"
    security_level: str = "standard"


@dataclass
class EdgeTask:
    """משימת Edge"""
    task_id: str
    task_type: str
    priority: int
    data_size_mb: float
    cpu_requirement: float
    memory_requirement_mb: int
    deadline: datetime
    privacy_level: str  # public, private, confidential, secret
    assigned_node: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None


@dataclass
class EdgeCluster:
    """אשכול Edge"""
    cluster_id: str
    nodes: List[str]
    coordinator_node: str
    geographic_center: Tuple[float, float]
    total_capacity: Dict[str, float]
    current_load: Dict[str, float]
    security_perimeter: float  # km radius
    mesh_connectivity: bool = True


@dataclass
class PrivacyPreservingComputation:
    """חישוב משמר פרטיות"""
    computation_id: str
    algorithm: str  # federated_learning, differential_privacy, homomorphic_encryption
    participants: List[str]
    privacy_budget: float
    noise_level: float
    aggregation_method: str
    results_encrypted: bool = True


class EdgeComputingOrchestrator:
    """מתאם Edge Computing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Edge infrastructure
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.edge_clusters: Dict[str, EdgeCluster] = {}
        self.edge_tasks: Dict[str, EdgeTask] = {}
        self.privacy_computations: Dict[str, PrivacyPreservingComputation] = {}
        
        # Task scheduling
        self.task_queue = queue.PriorityQueue()
        self.completed_tasks: List[str] = []
        
        # Performance metrics
        self.metrics = {
            "total_tasks_processed": 0,
            "average_latency_ms": 0.0,
            "edge_utilization": 0.0,
            "privacy_violations": 0,
            "energy_consumption_kwh": 0.0
        }
        
        # Start background processes
        asyncio.create_task(self._task_scheduler())
        asyncio.create_task(self._node_health_monitor())
        asyncio.create_task(self._cluster_optimization())
        
        self.logger.info("🌐 Edge Computing Orchestrator initialized")
    
    async def register_edge_node(self, node_type: EdgeNodeType, location: Tuple[float, float],
                                capabilities: List[EdgeCapability], hardware_specs: Dict) -> EdgeNode:
        """רישום נוד Edge חדש"""
        node_id = f"edge_{node_type.value}_{datetime.now().timestamp()}_{secrets.token_hex(4)}"
        
        node = EdgeNode(
            node_id=node_id,
            node_type=node_type,
            location=location,
            capabilities=capabilities,
            cpu_cores=hardware_specs.get("cpu_cores", 1),
            memory_mb=hardware_specs.get("memory_mb", 512),
            storage_gb=hardware_specs.get("storage_gb", 8),
            network_bandwidth_mbps=hardware_specs.get("bandwidth_mbps", 10),
            battery_level=hardware_specs.get("battery_level"),
            security_level=hardware_specs.get("security_level", "standard")
        )
        
        self.edge_nodes[node_id] = node
        
        # Auto-assign to nearest cluster or create new one
        await self._assign_node_to_cluster(node_id)
        
        self.logger.info(f"📱 Edge node registered: {node_type.value} at {location}")
        return node
    
    async def submit_edge_task(self, task_type: str, data: Dict, 
                             privacy_level: str = "private",
                             deadline_minutes: int = 60) -> str:
        """הגשת משימה לעיבוד Edge"""
        task_id = f"task_{datetime.now().timestamp()}_{secrets.token_hex(4)}"
        
        # Estimate resource requirements
        data_size = len(json.dumps(data).encode()) / (1024 * 1024)  # MB
        cpu_req, memory_req = await self._estimate_resource_requirements(task_type, data_size)
        
        task = EdgeTask(
            task_id=task_id,
            task_type=task_type,
            priority=self._calculate_task_priority(task_type, privacy_level),
            data_size_mb=data_size,
            cpu_requirement=cpu_req,
            memory_requirement_mb=memory_req,
            deadline=datetime.now() + timedelta(minutes=deadline_minutes),
            privacy_level=privacy_level
        )
        
        self.edge_tasks[task_id] = task
        
        # Add to scheduling queue
        self.task_queue.put((task.priority, task.created_at.timestamp(), task_id))
        
        self.logger.info(f"📋 Edge task submitted: {task_type} (privacy: {privacy_level})")
        return task_id
    
    async def process_threat_locally(self, node_id: str, threat_data: Dict) -> Dict:
        """עיבוד מקומי של איום"""
        if node_id not in self.edge_nodes:
            return {"error": "Node not found"}
        
        node = self.edge_nodes[node_id]
        
        # Check if node has threat detection capability
        if EdgeCapability.THREAT_DETECTION not in node.capabilities:
            return {"error": "Node lacks threat detection capability"}
        
        # Process threat locally to preserve privacy
        start_time = datetime.now()
        
        # Simulate local AI inference
        threat_analysis = await self._local_threat_analysis(threat_data, node)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000  # ms
        
        # Update node workload
        node.workload = min(1.0, node.workload + 0.1)
        
        result = {
            "threat_id": threat_data.get("id", "unknown"),
            "analysis": threat_analysis,
            "processing_node": node_id,
            "processing_time_ms": processing_time,
            "privacy_preserved": True,
            "local_processing": True,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"🔍 Threat processed locally on {node_id}")
        return result
    
    async def deploy_edge_honeypot(self, node_id: str, honeypot_config: Dict) -> Dict:
        """פריסת פיתיון על נוד Edge"""
        if node_id not in self.edge_nodes:
            return {"error": "Node not found"}
        
        node = self.edge_nodes[node_id]
        
        # Check capabilities and resources
        if EdgeCapability.HONEYPOT_HOSTING not in node.capabilities:
            return {"error": "Node cannot host honeypots"}
        
        if node.workload > 0.8:
            return {"error": "Node overloaded"}
        
        # Deploy lightweight honeypot
        honeypot_id = f"edge_hp_{node_id}_{secrets.token_hex(4)}"
        
        # Configure honeypot for edge environment
        edge_honeypot_config = {
            "honeypot_id": honeypot_id,
            "type": "lightweight_edge",
            "host_node": node_id,
            "resource_limit": {
                "cpu_percent": 20,
                "memory_mb": min(128, node.memory_mb * 0.25),
                "storage_mb": min(512, node.storage_gb * 1024 * 0.1)
            },
            "privacy_mode": True,
            "local_logging": True,
            "config": honeypot_config
        }
        
        # Update node workload
        node.workload += 0.2
        
        self.logger.info(f"🍯 Edge honeypot deployed: {honeypot_id} on {node_id}")
        
        return {
            "honeypot_id": honeypot_id,
            "deployment_successful": True,
            "host_node": node_id,
            "resource_allocation": edge_honeypot_config["resource_limit"]
        }
    
    async def create_federated_learning_task(self, participants: List[str], 
                                           model_type: str, privacy_budget: float = 1.0) -> str:
        """יצירת משימת למידה פדרטיבית"""
        computation_id = f"fl_{datetime.now().timestamp()}_{secrets.token_hex(4)}"
        
        # Validate participants
        valid_participants = [
            node_id for node_id in participants 
            if (node_id in self.edge_nodes and 
                EdgeCapability.AI_INFERENCE in self.edge_nodes[node_id].capabilities)
        ]
        
        if len(valid_participants) < 2:
            raise ValueError("Need at least 2 capable participants for federated learning")
        
        computation = PrivacyPreservingComputation(
            computation_id=computation_id,
            algorithm="federated_learning",
            participants=valid_participants,
            privacy_budget=privacy_budget,
            noise_level=self._calculate_noise_level(privacy_budget),
            aggregation_method="federated_averaging"
        )
        
        self.privacy_computations[computation_id] = computation
        
        # Submit federated learning tasks to participants
        for participant in valid_participants:
            await self.submit_edge_task(
                task_type=f"federated_learning_{model_type}",
                data={"computation_id": computation_id, "model_type": model_type},
                privacy_level="confidential"
            )
        
        self.logger.info(f"🤝 Federated learning task created: {computation_id}")
        return computation_id
    
    async def establish_mesh_network(self, node_ids: List[str]) -> Dict:
        """הקמת רשת Mesh"""
        if len(node_ids) < 3:
            return {"error": "Need at least 3 nodes for mesh network"}
        
        # Validate nodes have mesh capability
        mesh_capable_nodes = [
            node_id for node_id in node_ids
            if (node_id in self.edge_nodes and 
                EdgeCapability.MESH_NETWORKING in self.edge_nodes[node_id].capabilities)
        ]
        
        if len(mesh_capable_nodes) < 3:
            return {"error": "Insufficient mesh-capable nodes"}
        
        # Create mesh topology
        mesh_id = f"mesh_{datetime.now().timestamp()}_{secrets.token_hex(4)}"
        
        # Calculate optimal connections
        mesh_topology = await self._calculate_mesh_topology(mesh_capable_nodes)
        
        # Configure mesh network
        mesh_config = {
            "mesh_id": mesh_id,
            "nodes": mesh_capable_nodes,
            "topology": mesh_topology,
            "encryption": "WPA3",
            "routing_protocol": "AODV",
            "redundancy_level": "high",
            "auto_healing": True
        }
        
        self.logger.info(f"🕸️ Mesh network established: {mesh_id} with {len(mesh_capable_nodes)} nodes")
        
        return {
            "mesh_id": mesh_id,
            "nodes_connected": len(mesh_capable_nodes),
            "topology": mesh_topology,
            "status": "active"
        }
    
    async def get_edge_status(self) -> Dict:
        """קבלת סטטוס Edge Computing"""
        total_nodes = len(self.edge_nodes)
        online_nodes = len([n for n in self.edge_nodes.values() if n.status == "online"])
        
        # Calculate resource utilization
        total_cpu = sum(n.cpu_cores for n in self.edge_nodes.values())
        total_memory = sum(n.memory_mb for n in self.edge_nodes.values())
        total_storage = sum(n.storage_gb for n in self.edge_nodes.values())
        
        avg_workload = sum(n.workload for n in self.edge_nodes.values()) / total_nodes if total_nodes > 0 else 0
        
        # Task statistics
        pending_tasks = len([t for t in self.edge_tasks.values() if t.status == "pending"])
        running_tasks = len([t for t in self.edge_tasks.values() if t.status == "running"])
        completed_tasks = len([t for t in self.edge_tasks.values() if t.status == "completed"])
        
        return {
            "infrastructure": {
                "total_nodes": total_nodes,
                "online_nodes": online_nodes,
                "node_types": {
                    node_type.value: len([n for n in self.edge_nodes.values() if n.node_type == node_type])
                    for node_type in EdgeNodeType
                },
                "total_clusters": len(self.edge_clusters)
            },
            "resources": {
                "total_cpu_cores": total_cpu,
                "total_memory_mb": total_memory,
                "total_storage_gb": total_storage,
                "average_workload": avg_workload
            },
            "tasks": {
                "pending": pending_tasks,
                "running": running_tasks,
                "completed": completed_tasks,
                "total_processed": self.metrics["total_tasks_processed"]
            },
            "privacy": {
                "federated_learning_tasks": len([c for c in self.privacy_computations.values() 
                                               if c.algorithm == "federated_learning"]),
                "privacy_violations": self.metrics["privacy_violations"],
                "encrypted_computations": len([c for c in self.privacy_computations.values() 
                                             if c.results_encrypted])
            },
            "performance": {
                "average_latency_ms": self.metrics["average_latency_ms"],
                "edge_utilization": self.metrics["edge_utilization"],
                "energy_consumption_kwh": self.metrics["energy_consumption_kwh"]
            }
        }
    
    # Private helper methods
    
    async def _assign_node_to_cluster(self, node_id: str):
        """הקצאת נוד לאשכול"""
        node = self.edge_nodes[node_id]
        
        # Find nearest cluster
        nearest_cluster = None
        min_distance = float('inf')
        
        for cluster in self.edge_clusters.values():
            distance = self._calculate_distance(node.location, cluster.geographic_center)
            if distance < min_distance:
                min_distance = distance
                nearest_cluster = cluster
        
        # If no nearby cluster or distance too far, create new cluster
        if nearest_cluster is None or min_distance > 50:  # 50km threshold
            await self._create_new_cluster(node_id)
        else:
            nearest_cluster.nodes.append(node_id)
            self.logger.info(f"Node {node_id} assigned to cluster {nearest_cluster.cluster_id}")
    
    async def _create_new_cluster(self, coordinator_node_id: str):
        """יצירת אשכול חדש"""
        cluster_id = f"cluster_{datetime.now().timestamp()}_{secrets.token_hex(4)}"
        node = self.edge_nodes[coordinator_node_id]
        
        cluster = EdgeCluster(
            cluster_id=cluster_id,
            nodes=[coordinator_node_id],
            coordinator_node=coordinator_node_id,
            geographic_center=node.location,
            total_capacity={
                "cpu_cores": node.cpu_cores,
                "memory_mb": node.memory_mb,
                "storage_gb": node.storage_gb
            },
            current_load={
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "storage_usage": 0.0
            },
            security_perimeter=25.0  # 25km radius
        )
        
        self.edge_clusters[cluster_id] = cluster
        self.logger.info(f"New cluster created: {cluster_id}")
    
    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """חישוב מרחק גיאוגרפי"""
        import math
        
        lat1, lon1 = pos1
        lat2, lon2 = pos2
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def _estimate_resource_requirements(self, task_type: str, data_size_mb: float) -> Tuple[float, int]:
        """הערכת דרישות משאבים"""
        base_requirements = {
            "threat_detection": (0.3, 128),
            "data_processing": (0.2, 64),
            "ai_inference": (0.5, 256),
            "encryption": (0.1, 32),
            "federated_learning": (0.7, 512)
        }
        
        base_cpu, base_memory = base_requirements.get(task_type.split('_')[0], (0.2, 64))
        
        # Scale with data size
        cpu_req = base_cpu * (1 + data_size_mb / 100)
        memory_req = int(base_memory * (1 + data_size_mb / 50))
        
        return cpu_req, memory_req
    
    def _calculate_task_priority(self, task_type: str, privacy_level: str) -> int:
        """חישוב עדיפות משימה"""
        base_priority = {
            "threat_detection": 1,
            "encryption": 2,
            "ai_inference": 3,
            "data_processing": 4,
            "federated_learning": 5
        }.get(task_type.split('_')[0], 5)
        
        privacy_bonus = {
            "secret": 0,
            "confidential": 1,
            "private": 2,
            "public": 3
        }.get(privacy_level, 2)
        
        return base_priority + privacy_bonus
    
    async def _local_threat_analysis(self, threat_data: Dict, node: EdgeNode) -> Dict:
        """ניתוח איום מקומי"""
        # Simulate local AI inference
        threat_score = hash(str(threat_data)) % 100 / 100.0
        
        analysis = {
            "threat_score": threat_score,
            "threat_type": "simulated_local_detection",
            "confidence": min(0.9, node.trust_score),
            "processing_node_type": node.node_type.value,
            "local_model_version": "edge_v1.0",
            "privacy_preserved": True
        }
        
        return analysis
    
    def _calculate_noise_level(self, privacy_budget: float) -> float:
        """חישוב רמת רעש לפרטיות דיפרנציאלית"""
        # Inverse relationship: higher privacy budget = lower noise
        return max(0.01, 1.0 / privacy_budget)
    
    async def _calculate_mesh_topology(self, node_ids: List[str]) -> Dict:
        """חישוב טופולוגיית Mesh"""
        topology = {
            "connections": [],
            "redundancy_paths": [],
            "load_balancing": "round_robin"
        }
        
        # Create connections between nearby nodes
        for i, node1_id in enumerate(node_ids):
            node1 = self.edge_nodes[node1_id]
            
            for j, node2_id in enumerate(node_ids[i+1:], i+1):
                node2 = self.edge_nodes[node2_id]
                
                distance = self._calculate_distance(node1.location, node2.location)
                
                # Connect nodes within 20km
                if distance <= 20:
                    topology["connections"].append({
                        "from": node1_id,
                        "to": node2_id,
                        "distance_km": distance,
                        "signal_strength": max(0.1, 1.0 - distance / 20)
                    })
        
        return topology
    
    async def _task_scheduler(self):
        """מתזמן משימות"""
        while True:
            try:
                if not self.task_queue.empty():
                    priority, timestamp, task_id = self.task_queue.get()
                    
                    if task_id in self.edge_tasks:
                        task = self.edge_tasks[task_id]
                        
                        # Find suitable node
                        suitable_node = await self._find_suitable_node(task)
                        
                        if suitable_node:
                            task.assigned_node = suitable_node
                            task.status = "running"
                            
                            # Simulate task execution
                            asyncio.create_task(self._execute_task(task_id))
                        else:
                            # Put back in queue if no suitable node
                            self.task_queue.put((priority, timestamp, task_id))
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in task scheduler: {e}")
                await asyncio.sleep(5)
    
    async def _find_suitable_node(self, task: EdgeTask) -> Optional[str]:
        """מציאת נוד מתאים למשימה"""
        suitable_nodes = []
        
        for node_id, node in self.edge_nodes.items():
            if (node.status == "online" and 
                node.workload < 0.8 and
                node.memory_mb >= task.memory_requirement_mb and
                node.cpu_cores >= task.cpu_requirement):
                
                # Calculate suitability score
                score = (1 - node.workload) * node.trust_score
                suitable_nodes.append((node_id, score))
        
        if suitable_nodes:
            # Return best node
            suitable_nodes.sort(key=lambda x: x[1], reverse=True)
            return suitable_nodes[0][0]
        
        return None
    
    async def _execute_task(self, task_id: str):
        """ביצוע משימה"""
        task = self.edge_tasks[task_id]
        node = self.edge_nodes[task.assigned_node]
        
        # Simulate task execution time
        execution_time = max(1, task.cpu_requirement * 2)  # seconds
        
        await asyncio.sleep(execution_time)
        
        # Update task status
        task.status = "completed"
        task.completed_at = datetime.now()
        task.result = {"status": "success", "execution_time": execution_time}
        
        # Update node workload
        node.workload = max(0, node.workload - 0.1)
        
        # Update metrics
        self.metrics["total_tasks_processed"] += 1
        
        self.logger.info(f"Task completed: {task_id} on {task.assigned_node}")
    
    async def _node_health_monitor(self):
        """מוניטור בריאות נודים"""
        while True:
            try:
                current_time = datetime.now()
                
                for node in self.edge_nodes.values():
                    # Check heartbeat
                    if (current_time - node.last_heartbeat).seconds > 300:  # 5 minutes
                        node.status = "offline"
                        node.workload = 0.0
                    
                    # Update battery level for battery-powered devices
                    if node.battery_level is not None:
                        node.battery_level = max(0, node.battery_level - 0.1)  # Simulate drain
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in node health monitor: {e}")
                await asyncio.sleep(60)
    
    async def _cluster_optimization(self):
        """אופטימיזציה של אשכולות"""
        while True:
            try:
                # Rebalance clusters based on load and geography
                for cluster in self.edge_clusters.values():
                    await self._rebalance_cluster(cluster)
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in cluster optimization: {e}")
                await asyncio.sleep(300)
    
    async def _rebalance_cluster(self, cluster: EdgeCluster):
        """איזון מחדש של אשכול"""
        # Calculate current load distribution
        total_load = sum(
            self.edge_nodes[node_id].workload 
            for node_id in cluster.nodes 
            if node_id in self.edge_nodes
        )
        
        avg_load = total_load / len(cluster.nodes) if cluster.nodes else 0
        
        # Update cluster metrics
        cluster.current_load = {
            "average_workload": avg_load,
            "total_nodes": len(cluster.nodes),
            "overloaded_nodes": len([
                node_id for node_id in cluster.nodes
                if node_id in self.edge_nodes and self.edge_nodes[node_id].workload > 0.8
            ])
        }
    
    async def cleanup(self):
        """ניקוי משאבי Edge Computing"""
        self.logger.info("🧹 Cleaning up Edge Computing Orchestrator...")
        
        # Mark all nodes as offline
        for node in self.edge_nodes.values():
            node.status = "offline"
        
        # Clear task queue
        while not self.task_queue.empty():
            self.task_queue.get()
        
        self.logger.info("✅ Edge Computing cleanup complete")
