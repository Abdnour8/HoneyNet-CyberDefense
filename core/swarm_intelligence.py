"""
HoneyNet Swarm Intelligence System
מערכת אינטליגנציה נחילית לתיאום הגנה קולקטיבית
"""

import asyncio
import logging
import json
import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import weakref

# Import the new memory manager
from .memory_manager import memory_manager, MemoryPool

class SwarmRole(Enum):
    """תפקידים בנחיל"""
    SCOUT = "scout"           # סיירים - מחפשים איומים
    WORKER = "worker"         # עובדים - מעבדים נתונים
    GUARD = "guard"           # שומרים - מגנים על המערכת
    QUEEN = "queen"           # מלכה - מתאמת הנחיל
    DRONE = "drone"           # זכרים - מפיצים מידע


class ThreatLevel(Enum):
    """רמות איום"""
    GREEN = 0    # בטוח
    YELLOW = 1   # חשוד
    ORANGE = 2   # מסוכן
    RED = 3      # קריטי


@dataclass
class SwarmAgent:
    """סוכן בנחיל"""
    agent_id: str
    role: SwarmRole
    position: Tuple[float, float]  # Geographic coordinates
    energy: float = 100.0
    experience: int = 0
    specialization: List[str] = field(default_factory=list)
    connections: Set[str] = field(default_factory=set)
    last_activity: datetime = field(default_factory=datetime.now)
    threat_detection_score: float = 0.0
    collaboration_score: float = 0.0
    reputation: float = 50.0


@dataclass
class ThreatPheromone:
    """פרומון איום - מידע שמשאירים הסוכנים"""
    pheromone_id: str
    threat_type: str
    intensity: float
    position: Tuple[float, float]
    timestamp: datetime
    depositor_id: str
    decay_rate: float = 0.1
    effective_radius: float = 10.0  # km


@dataclass
class SwarmTask:
    """משימה לנחיל"""
    task_id: str
    task_type: str
    priority: int
    target_area: Tuple[float, float, float]  # lat, lon, radius
    required_agents: int
    assigned_agents: Set[str] = field(default_factory=set)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None


@dataclass
class CollectiveIntelligence:
    """אינטליגנציה קולקטיבית"""
    pattern_id: str
    pattern_type: str
    confidence: float
    contributing_agents: Set[str]
    geographic_spread: List[Tuple[float, float]]
    temporal_pattern: Dict[int, float]  # hour -> intensity
    evolution_history: List[Dict] = field(default_factory=list)


class SwarmIntelligence:
    """מערכת אינטליגנציה נחיל מתקדמת עם אופטימיזציה של זיכרון"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Dynamic resource limits based on available memory
        self.resource_limits = memory_manager.calculate_dynamic_limits()
        self.max_agents = min(1000, self.resource_limits.max_async_tasks // 2)  # הגבלה דינמית
        
        # Use weak references for better memory management
        self.active_agents: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self.pheromone_map: Dict[str, ThreatPheromone] = {}
        self.global_knowledge = CollectiveIntelligence(
            pattern_id="global",
            pattern_type="global",
            confidence=0.0,
            contributing_agents=set(),
            geographic_spread=[],
            temporal_pattern={},
            evolution_history=[]
        )
        
        # Create memory pools for frequently used objects
        memory_manager.create_memory_pool(
            'swarm_agents', 
            lambda: SwarmAgent(agent_id=f"temp_{random.randint(1000, 9999)}", role=SwarmRole.SCOUT),
            initial_size=50,
            max_size=200
        )
        memory_manager.create_memory_pool(
            'pheromone_trails',
            lambda: ThreatPheromone(pheromone_id=f"temp_{random.randint(1000, 9999)}", threat_type="temp", intensity=0.0, position=(0.0, 0.0), timestamp=datetime.now(), depositor_id="temp"),
            initial_size=20,
            max_size=100
        )
        
        # Coordination mechanisms with size limits
        self.coordination_graph = defaultdict(set)
        self.task_queue = asyncio.Queue(maxsize=self.max_agents)
        self.results_cache = {}  # Will be limited by cleanup process
        
        # Emergence detection
        self.emergence_patterns: List[Dict] = []
        self.collective_behaviors: Dict[str, Any] = {}
        
        # Performance metrics
        self.swarm_metrics = {
            "total_agents": 0,
            "active_tasks": 0,
            "completed_tasks": 0,
            "emergence_events": 0,
            "coordination_efficiency": 0.0,
            "collective_intelligence_score": 0.0,
            "memory_usage_mb": 0,
            "agent_pool_size": 0
        }
        
        # Use memory manager's task manager
        self.task_manager = memory_manager.task_manager
        self.is_active = False
        
        self.logger.info(f"🐝 Swarm Intelligence System initialized with max {self.max_agents} agents")
    
    async def create_agent(self, role: SwarmRole, task_data: Optional[Dict] = None) -> SwarmAgent:
        """יצירת agent חדש עם ניהול זיכרון"""
        # Check current resource limits
        current_limits = memory_manager.calculate_dynamic_limits()
        max_agents_now = min(self.max_agents, current_limits.max_async_tasks // 2)
        
        if len(self.active_agents) >= max_agents_now:
            # Remove least active agent and return to pool
            least_active = min(self.active_agents.values(), 
                             key=lambda a: a.last_activity)
            await self.remove_agent(least_active.agent_id)
        
        # Try to get agent from memory pool first
        try:
            agent = memory_manager.get_from_pool('swarm_agents')
            agent.agent_id = f"agent_{len(self.active_agents)}_{int(time.time())}"
            agent.role = role
            agent.reset()  # Reset agent state
        except:
            # Create new agent if pool is empty
            agent_id = f"agent_{len(self.active_agents)}_{int(time.time())}"
            agent = SwarmAgent(agent_id=agent_id, role=role)
        
        if task_data:
            agent.assign_task(task_data)
        
        self.active_agents[agent.agent_id] = agent
        self.swarm_metrics["total_agents"] += 1
        self.swarm_metrics["agent_pool_size"] = len(memory_manager.memory_pools.get('swarm_agents', {}).pool)
        
        # Add to coordination graph
        self._add_to_coordination_graph(agent)
        
        self.logger.debug(f"Created agent {agent.agent_id} with role {role.value}")
        return agent
    
    async def deposit_threat_pheromone(self, agent_id: str, threat_type: str, 
                                     intensity: float, position: Tuple[float, float]) -> str:
        """הפקדת פרומון איום"""
        if agent_id not in self.active_agents:
            raise Exception("Agent not found")
        
        pheromone_id = f"pheromone_{datetime.now().timestamp()}_{agent_id}"
        
        pheromone = ThreatPheromone(
            pheromone_id=pheromone_id,
            threat_type=threat_type,
            intensity=intensity,
            position=position,
            timestamp=datetime.now(),
            depositor_id=agent_id,
            decay_rate=0.05
        )
        
        self.pheromone_map[pheromone_id] = pheromone
        
        # Update agent experience
        self.active_agents[agent_id].experience += 1
        self.active_agents[agent_id].threat_detection_score += intensity * 0.1
        
        # Trigger nearby agents
        await self._alert_nearby_agents(position, threat_type, intensity)
        
        self.logger.info(f"💨 Pheromone deposited: {threat_type} by {agent_id}")
        return pheromone_id
    
    async def stop_swarm(self):
        """עצירת מערכת הנחיל עם ניקוי זיכרון"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        # Cancel all tasks through task manager
        await self.task_manager.cancel_all_tasks()
        
        # Return agents to memory pool
        for agent in list(self.active_agents.values()):
            await agent.deactivate()
            try:
                memory_manager.return_to_pool('swarm_agents', agent)
            except:
                pass  # Agent might not be from pool
        
        # Return pheromone trails to pool
        for trail in list(self.pheromone_map.values()):
            try:
                memory_manager.return_to_pool('pheromone_trails', trail)
            except:
                pass
        
        # Clear collections
        self.active_agents.clear()
        self.pheromone_map.clear()
        self.results_cache.clear()
        
        self.logger.info("🛑 Swarm Intelligence deactivated with memory cleanup")
    
    async def remove_agent(self, agent_id: str):
        """הסרת agent והחזרתו למאגר זיכרון"""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            await agent.deactivate()
            
            # Return to memory pool
            try:
                memory_manager.return_to_pool('swarm_agents', agent)
            except:
                pass
            
            # Remove from coordination graph
            self._remove_from_coordination_graph(agent_id)
            
            del self.active_agents[agent_id]
            self.logger.debug(f"Removed agent {agent_id}")
    
    def _add_to_coordination_graph(self, agent):
        """הוספת agent לגרף התיאום"""
        # Connect to nearby agents based on role compatibility
        for other_id, other_agent in self.active_agents.items():
            if other_id != agent.agent_id and self._should_connect_agents(agent, other_agent):
                self.coordination_graph[agent.agent_id].add(other_id)
                self.coordination_graph[other_id].add(agent.agent_id)
    
    def _remove_from_coordination_graph(self, agent_id: str):
        """הסרת agent מגרף התיאום"""
        # Remove all connections to this agent
        for connected_id in list(self.coordination_graph[agent_id]):
            self.coordination_graph[connected_id].discard(agent_id)
        
        # Remove the agent's entry
        if agent_id in self.coordination_graph:
            del self.coordination_graph[agent_id]
    
    def _should_connect_agents(self, agent1, agent2) -> bool:
        """בדיקה האם שני agents צריכים להתחבר"""
        # Connect based on role compatibility
        compatible_roles = {
            SwarmRole.QUEEN: [SwarmRole.WORKER, SwarmRole.DRONE, SwarmRole.SCOUT],
            SwarmRole.WORKER: [SwarmRole.QUEEN, SwarmRole.WORKER, SwarmRole.GUARD],
            SwarmRole.SCOUT: [SwarmRole.QUEEN, SwarmRole.GUARD],
            SwarmRole.GUARD: [SwarmRole.WORKER, SwarmRole.SCOUT],
            SwarmRole.DRONE: [SwarmRole.QUEEN]
        }
        
        return agent2.role in compatible_roles.get(agent1.role, [])
    
    async def _memory_cleanup_process(self):
        """תהליך ניקוי זיכרון תקופתי"""
        while self.is_active:
            try:
                # Clean old cache entries
                current_time = datetime.now()
                old_entries = [
                    key for key, (data, timestamp) in self.results_cache.items()
                    if (current_time - timestamp).total_seconds() > 3600  # 1 hour
                ]
                
                for key in old_entries:
                    del self.results_cache[key]
                
                # Limit cache size
                if len(self.results_cache) > 1000:
                    # Keep only the 500 most recent entries
                    sorted_items = sorted(
                        self.results_cache.items(),
                        key=lambda x: x[1][1],  # Sort by timestamp
                        reverse=True
                    )
                    self.results_cache = dict(sorted_items[:500])
                
                # Clean old pheromone trails
                old_pheromones = [
                    pid for pid, pheromone in self.pheromone_map.items()
                    if (current_time - pheromone.timestamp).total_seconds() > 1800  # 30 minutes
                    or pheromone.intensity < 0.1
                ]
                
                for pid in old_pheromones:
                    pheromone = self.pheromone_map[pid]
                    try:
                        memory_manager.return_to_pool('pheromone_trails', pheromone)
                    except:
                        pass
                    del self.pheromone_map[pid]
                
                # Update metrics
                self.swarm_metrics["memory_usage_mb"] = memory_manager.get_memory_stats().used_memory // (1024 * 1024)
                self.swarm_metrics["agent_pool_size"] = len(memory_manager.memory_pools.get('swarm_agents', {}).pool)
                
                self.logger.debug(f"Memory cleanup: removed {len(old_entries)} cache entries, {len(old_pheromones)} pheromones")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in memory cleanup process: {e}")
                await asyncio.sleep(300)
    
    async def start_swarm(self):
        """הפעלת מערכת הנחיל עם ניהול משאבים מתקדם"""
        if self.is_active:
            return
        
        self.is_active = True
        
        # Start background processes using task manager
        background_processes = [
            self._pheromone_decay_process(),
            self._swarm_coordination_process(),
            self._emergence_detection_process(),
            self._knowledge_sharing_process(),
            self._performance_monitoring_process(),
            self._memory_cleanup_process()
        ]
        
        for i, process in enumerate(background_processes):
            await self.task_manager.create_task(process, f"swarm_process_{i}")
        
        # Initialize basic swarm with resource limits
        await self._initialize_basic_swarm()
        
        self.logger.info(f"🚀 Swarm Intelligence activated with {len(self.active_agents)} initial agents")
    
    async def _initialize_basic_swarm(self):
        """יצירת נחיל בסיסי"""
        # Create initial agents based on available resources
        initial_agent_count = min(10, self.max_agents // 4)
        
        roles = [SwarmRole.QUEEN, SwarmRole.SCOUT, SwarmRole.WORKER, SwarmRole.GUARD]
        
        for i in range(initial_agent_count):
            role = roles[i % len(roles)]
            await self.create_agent(role)
        
        self.logger.info(f"Initialized basic swarm with {initial_agent_count} agents")
    
    async def _pheromone_decay_process(self):
        """תהליך דעיכת פרומונים"""
        while self.is_active:
            try:
                current_time = datetime.now()
                decayed_count = 0
                
                for pheromone in list(self.pheromone_map.values()):
                    age_minutes = (current_time - pheromone.timestamp).total_seconds() / 60
                    decay_factor = np.exp(-0.05 * age_minutes)  # 5% decay per minute
                    
                    pheromone.intensity *= decay_factor
                    decayed_count += 1
                
                self.logger.debug(f"Decayed {decayed_count} pheromones")
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                self.logger.error(f"Error in pheromone decay process: {e}")
                await asyncio.sleep(60)
    
    async def _swarm_coordination_process(self):
        """תהליך תיאום הנחיל"""
        while self.is_active:
            try:
                # Update coordination efficiency
                total_connections = sum(len(connections) for connections in self.coordination_graph.values())
                max_possible_connections = len(self.active_agents) * (len(self.active_agents) - 1)
                
                if max_possible_connections > 0:
                    self.swarm_metrics["coordination_efficiency"] = total_connections / max_possible_connections
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in swarm coordination process: {e}")
                await asyncio.sleep(30)
    
    async def _emergence_detection_process(self):
        """תהליך זיהוי התנהגות מתעוררת"""
        while self.is_active:
            try:
                # Detect emergence patterns
                patterns = await self._detect_emergence_patterns()
                
                for pattern in patterns:
                    self.emergence_patterns.append({
                        "pattern": pattern,
                        "timestamp": datetime.now(),
                        "confidence": pattern.get("confidence", 0.5)
                    })
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in emergence detection process: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_pheromone_clusters(self) -> List[Dict]:
        """ניתוח אשכולות פרומונים"""
        clusters = []
        
        if not self.pheromones:
            return clusters
        
        # Simple clustering algorithm
        processed = set()
        
        for i, pheromone in enumerate(self.pheromones):
            if i in processed:
                continue
            
            cluster_pheromones = [pheromone]
            cluster_center = pheromone.position
            
            # Find nearby pheromones
            for j, other_pheromone in enumerate(self.pheromones):
                if i != j and j not in processed:
                    distance = self._calculate_distance(pheromone.position, other_pheromone.position)
                    
                    if distance <= 5.0:  # 5km cluster radius
                        cluster_pheromones.append(other_pheromone)
                        processed.add(j)
            
            if len(cluster_pheromones) >= 3:  # Minimum cluster size
                # Calculate cluster properties
                total_intensity = sum(p.intensity for p in cluster_pheromones)
                dominant_threat = max(set(p.threat_type for p in cluster_pheromones), 
                                    key=lambda t: sum(p.intensity for p in cluster_pheromones if p.threat_type == t))
                
                clusters.append({
                    "center": cluster_center,
                    "radius": 5.0,
                    "density": total_intensity / len(cluster_pheromones),
                    "dominant_threat": dominant_threat,
                    "pheromone_count": len(cluster_pheromones),
                    "agent_count": len(set(p.depositor_id for p in cluster_pheromones))
                })
            
            processed.add(i)
        
        return clusters
    
    async def _analyze_coordination_patterns(self) -> List[Dict]:
        """ניתוח דפוסי תיאום"""
        patterns = []
        
        # Analyze agent collaboration networks
        collaboration_strength = {}
        
        for agent_id, agent in self.agents.items():
            strength = len(agent.connections) * agent.collaboration_score
            collaboration_strength[agent_id] = strength
        
        # Find highly coordinated groups
        if collaboration_strength:
            avg_strength = sum(collaboration_strength.values()) / len(collaboration_strength)
            
            highly_coordinated = [
                agent_id for agent_id, strength in collaboration_strength.items()
                if strength > avg_strength * 1.5
            ]
            
            if len(highly_coordinated) >= 5:
                patterns.append({
                    "type": "high_coordination",
                    "agent_count": len(highly_coordinated),
                    "intensity": len(highly_coordinated) / len(self.agents),
                    "avg_collaboration_score": sum(self.agents[aid].collaboration_score for aid in highly_coordinated) / len(highly_coordinated)
                })
        
        return patterns
    
    async def _store_collective_intelligence(self, pattern: Dict):
        """שמירת אינטליגנציה קולקטיבית"""
        pattern_id = f"ci_{datetime.now().timestamp()}"
        
        intelligence = CollectiveIntelligence(
            pattern_id=pattern_id,
            pattern_type=pattern["type"],
            confidence=pattern["intensity"],
            contributing_agents=set(),  # Will be populated based on pattern
            geographic_spread=[pattern.get("center", (0, 0))],
            temporal_pattern={datetime.now().hour: pattern["intensity"]}
        )
        
        self.collective_intelligence[pattern_id] = intelligence
        
        self.logger.info(f"🧠 Collective intelligence stored: {pattern['type']}")
    
    async def _calculate_threat_density_map(self) -> Dict:
        """חישוב מפת צפיפות איומים"""
        density_map = {}
        
        # Create grid-based density map
        for pheromone in self.pheromones:
            lat, lon = pheromone.position
            grid_key = (round(lat, 1), round(lon, 1))  # 0.1 degree grid
            
            if grid_key not in density_map:
                density_map[grid_key] = 0
            
            density_map[grid_key] += pheromone.intensity
        
        return density_map
    
    async def _find_optimal_scout_position(self, agent_id: str, threat_density_map: Dict) -> Optional[Tuple[float, float]]:
        """מציאת מיקום אופטימלי לסייר"""
        agent = self.agents[agent_id]
        current_lat, current_lon = agent.position
        
        # Find areas with high threat density but low scout coverage
        best_position = None
        best_score = 0
        
        for (lat, lon), density in threat_density_map.items():
            # Count nearby scouts
            nearby_scouts = sum(
                1 for other_agent in self.agents.values()
                if (other_agent.role == SwarmRole.SCOUT and 
                    self._calculate_distance((lat, lon), other_agent.position) <= 10)
            )
            
            # Score = threat density / (scout coverage + 1)
            score = density / (nearby_scouts + 1)
            
            if score > best_score:
                best_score = score
                best_position = (lat, lon)
        
        return best_position
    
    async def _optimize_role_assignments(self):
        """אופטימיזציה של הקצאת תפקידים"""
        # Promote experienced agents
        for agent in self.agents.values():
            if agent.experience > 500 and agent.role == SwarmRole.WORKER:
                if agent.threat_detection_score > 50:
                    agent.role = SwarmRole.SCOUT
                elif agent.collaboration_score > 100:
                    agent.role = SwarmRole.QUEEN
    
    async def _optimize_communication_network(self):
        """אופטימיזציה של רשת התקשורת"""
        # Remove weak connections and establish stronger ones
        for agent in self.agents.values():
            # Remove connections to inactive agents
            inactive_connections = set()
            
            for connection_id in agent.connections:
                if connection_id in self.agents:
                    other_agent = self.agents[connection_id]
                    if (datetime.now() - other_agent.last_activity).seconds > 3600:  # 1 hour
                        inactive_connections.add(connection_id)
            
            agent.connections -= inactive_connections
    
    async def _redistribute_tasks(self):
        """הפצה מחדש של משימות"""
        # Reassign tasks from overloaded agents to available ones
        for task in self.tasks.values():
            if task.status == "active" and len(task.assigned_agents) < task.required_agents:
                await self._assign_agents_to_task(task.task_id)
    
    async def cleanup(self):
        """ניקוי משאבים"""
        self.logger.info("🧹 Cleaning up Swarm Intelligence System...")
        
        # Save swarm state
        await self._save_swarm_state()
        
        self.logger.info("✅ Swarm Intelligence cleanup complete")
    
    async def _save_swarm_state(self):
        """שמירת מצב הנחיל"""
        # Implementation for saving swarm state
        pass
