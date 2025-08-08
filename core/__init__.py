"""
HoneyNet Core Module
מודול הליבה של HoneyNet
"""

# Core modules - basic functionality
try:
    from .defense_engine import DefenseEngine
except ImportError:
    DefenseEngine = None

try:
    from .threat_analyzer import ThreatAnalyzer
except ImportError:
    ThreatAnalyzer = None

# Advanced modules - optional
try:
    from .gamification import GamificationEngine
except ImportError:
    GamificationEngine = None

try:
    from .blockchain_ledger import BlockchainThreatLedger as BlockchainLedger
except ImportError:
    BlockchainLedger = None

try:
    from .swarm_intelligence import SwarmIntelligenceSystem as SwarmIntelligence
except ImportError:
    SwarmIntelligence = None

try:
    from .quantum_honeypots import QuantumResistantHoneypots as QuantumHoneypots
except ImportError:
    QuantumHoneypots = None

try:
    from .edge_computing import EdgeComputingOrchestrator
except ImportError:
    EdgeComputingOrchestrator = None

try:
    from .digital_twin import DigitalTwinEngine
except ImportError:
    DigitalTwinEngine = None

__all__ = [
    "DefenseEngine", 
    "ThreatAnalyzer", 
    "GamificationEngine",
    "BlockchainLedger",
    "SwarmIntelligence", 
    "QuantumHoneypots",
    "EdgeComputingOrchestrator",
    "DigitalTwinEngine"
]
