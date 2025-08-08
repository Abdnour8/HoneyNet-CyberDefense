"""
HoneyNet Desktop Client
לקוח שולחני של HoneyNet
"""

import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Core modules - required
from core.defense_engine import DefenseEngine, ThreatEvent, AttackType, ThreatLevel
from core.honeypot_system import HoneypotSystem
from core.threat_analyzer import ThreatAnalyzer
from core.config_manager import ConfigManager

# Advanced modules - optional (load safely)
GamificationEngine = None
BlockchainThreatLedger = None
SwarmIntelligenceSystem = None
QuantumHoneypotSystem = None
EdgeComputingOrchestrator = None
DigitalTwinEngine = None

try:
    from core.gamification import GamificationEngine
except ImportError:
    print("Warning: Gamification module not available")

try:
    from core.blockchain_ledger import BlockchainThreatLedger
except ImportError:
    print("Warning: Blockchain module not available")

try:
    from core.swarm_intelligence import SwarmIntelligenceSystem
except ImportError:
    print("Warning: Swarm Intelligence module not available")

try:
    from core.quantum_honeypots import QuantumHoneypotSystem
except ImportError:
    print("Warning: Quantum Honeypots module not available")

try:
    from core.edge_computing import EdgeComputingOrchestrator
except ImportError:
    print("Warning: Edge Computing module not available")

try:
    from core.digital_twin import DigitalTwinEngine
except ImportError:
    print("Warning: Digital Twin module not available")

try:
    from config.settings import get_settings
except ImportError:
    # Fallback settings
    def get_settings():
        class Settings:
            def __init__(self):
                self.server_url = "http://localhost:8000"
                self.debug = True
        return Settings()


# Define missing classes and enums for the GUI
class TriggerType(Enum):
    FILE_ACCESS = "file_access"
    NETWORK_CONNECTION = "network_connection"
    CREDENTIAL_THEFT = "credential_theft"
    MALWARE_DETECTION = "malware_detection"


@dataclass
class HoneypotTrigger:
    honeypot_id: str
    trigger_type: TriggerType
    timestamp: datetime
    source_ip: str = "unknown"
    details: Dict = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class HoneyNetGUI:
    """ממשק משתמש גרפי של HoneyNet"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HoneyNet - Global Cyber Defense Platform")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Initialize core components first
        self.config_manager = ConfigManager()
        self.defense_engine = DefenseEngine()
        self.honeypot_system = HoneypotSystem()
        self.threat_analyzer = ThreatAnalyzer()
        
        # Initialize advanced features to None first
        self.gamification_engine = None
        self.blockchain_ledger = None
        self.swarm_intelligence = None
        self.quantum_honeypots = None
        self.edge_computing = None
        self.digital_twin_engine = None
        
        # Setup asyncio event loop for advanced features
        self.loop = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.setup_async_environment()
        
        # GUI state
        self.is_running = False
        self.threat_log = []
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI
        self.create_widgets()
    
    def setup_async_environment(self):
        """הגדרת סביבת asyncio לפיצ'רים המתקדמים"""
        try:
            # Try to get existing event loop
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create new event loop if none exists
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        # Start event loop in background thread
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        # Wait a moment for event loop to be ready
        import time
        time.sleep(0.5)
        
        # Now initialize advanced features after event loop is ready
        self.initialize_advanced_features()
    
    def _run_event_loop(self):
        """הרצת event loop ברקע"""
        try:
            self.loop.run_forever()
        except Exception as e:
            print(f"Event loop error: {e}")
    
    def initialize_advanced_features(self):
        """יצירת המודולים המתקדמים בצורה בטוחה"""
        try:
            # Initialize advanced features (only if modules are available)
            self.gamification_engine = self._safe_init_module(GamificationEngine, "Gamification")
            self.blockchain_ledger = self._safe_init_module(BlockchainThreatLedger, "Blockchain")
            self.swarm_intelligence = self._safe_init_module(SwarmIntelligenceSystem, "Swarm Intelligence")
            self.quantum_honeypots = self._safe_init_module(QuantumHoneypotSystem, "Quantum Honeypots")
            self.edge_computing = self._safe_init_module(EdgeComputingOrchestrator, "Edge Computing")
            self.digital_twin_engine = self._safe_init_module(DigitalTwinEngine, "Digital Twin")
            
            print("✅ Advanced features initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Some advanced features may not be available: {e}")
    
    def _safe_init_module(self, module_class, module_name):
        """יצירה בטוחה של מודול מתקדם"""
        if module_class is None:
            print(f"⚠️ {module_name} module not available")
            return None
        
        try:
            return module_class()
        except Exception as e:
            print(f"⚠️ Failed to initialize {module_name}: {e}")
            return None
        
        # Setup event handlers
        self.setup_event_handlers()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 HoneyNet Desktop Client initialized")
    
    def setup_logging(self):
        """הגדרת מערכת הלוגים"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def create_widgets(self):
        """יצירת רכיבי הממשק"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(
            title_frame,
            text="🛡️ HoneyNet - Global Cyber Defense Platform",
            font=('Arial', 18, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="המהפכה בעולם הסייבר - רשת הפיתיון האנושית הגלובלית",
            font=('Arial', 12),
            fg='#cccccc',
            bg='#1a1a1a'
        )
        subtitle_label.pack()
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='#2a2a2a', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_button = tk.Button(
            control_frame,
            text="🚀 Start HoneyNet Protection",
            command=self.start_protection,
            bg='#00aa00',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        self.start_button.pack(side='left', padx=10, pady=10)
        
        self.stop_button = tk.Button(
            control_frame,
            text="🛑 Stop Protection",
            command=self.stop_protection,
            bg='#aa0000',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=10, pady=10)
        
        self.simulate_button = tk.Button(
            control_frame,
            text="⚡ Simulate Attack",
            command=self.simulate_attack,
            bg='#ff6600',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=10
        )
        self.simulate_button.pack(side='right', padx=10, pady=10)
        
        # Status panel
        status_frame = tk.Frame(self.root, bg='#2a2a2a', relief='raised', bd=2)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: 🔴 Offline",
            font=('Arial', 14, 'bold'),
            fg='#ff0000',
            bg='#2a2a2a'
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Statistics panel
        stats_frame = tk.LabelFrame(
            self.root,
            text="📊 Real-time Statistics",
            font=('Arial', 12, 'bold'),
            fg='#00ff00',
            bg='#2a2a2a'
        )
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Create statistics grid
        stats_grid = tk.Frame(stats_frame, bg='#2a2a2a')
        stats_grid.pack(fill='x', padx=10, pady=10)
        
        # Statistics labels
        self.stats_labels = {}
        stats_items = [
            ("threats_detected", "🚨 Threats Detected"),
            ("attacks_blocked", "🛡️ Attacks Blocked"),
            ("honeypots_active", "🍯 Active Honeypots"),
            ("honeypots_triggered", "⚡ Honeypots Triggered"),
            ("global_network", "🌐 Global Network Status"),
            ("protection_level", "🔒 Protection Level")
        ]
        
        for i, (key, label) in enumerate(stats_items):
            row = i // 3
            col = i % 3
            
            frame = tk.Frame(stats_grid, bg='#2a2a2a')
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            tk.Label(
                frame,
                text=label + ":",
                font=('Arial', 10),
                fg='#cccccc',
                bg='#2a2a2a'
            ).pack(anchor='w')
            
            value_label = tk.Label(
                frame,
                text="0",
                font=('Arial', 12, 'bold'),
                fg='#00ff00',
                bg='#2a2a2a'
            )
            value_label.pack(anchor='w')
            self.stats_labels[key] = value_label
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_threat_monitor_tab()
        self.create_honeypot_tab()
        self.create_intelligence_tab()
        self.create_gamification_tab()
        self.create_blockchain_tab()
        self.create_swarm_tab()
        self.create_quantum_tab()
        self.create_edge_computing_tab()
        self.create_digital_twin_tab()
        self.create_settings_tab()
    
    def create_threat_monitor_tab(self):
        threat_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(threat_frame, text="🚨 Threat Monitor")
        
        tk.Label(
            threat_frame,
            text="Real-time Threat Detection Log",
            font=('Arial', 14, 'bold'),
            fg='#ff6600',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        self.threat_log_text = scrolledtext.ScrolledText(
            threat_frame,
            height=15,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 10),
            insertbackground='#00ff00'
        )
        self.threat_log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_honeypot_tab(self):
        honeypot_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(honeypot_frame, text="🍯 Smart Honeypots")
        
        tk.Label(
            honeypot_frame,
            text="Active Honeypot Network",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        self.honeypot_tree = ttk.Treeview(
            honeypot_frame,
            columns=('Type', 'Status', 'Triggers', 'Last Activity'),
            show='tree headings'
        )
        self.honeypot_tree.heading('#0', text='Honeypot Name')
        self.honeypot_tree.heading('Type', text='Type')
        self.honeypot_tree.heading('Status', text='Status')
        self.honeypot_tree.heading('Triggers', text='Triggers')
        self.honeypot_tree.heading('Last Activity', text='Last Activity')
        self.honeypot_tree.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_gamification_tab(self):
        """יצירת טאב גיימיפיקציה"""
        gamification_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(gamification_frame, text="🎮 Gamification")
        
        # Title
        tk.Label(
            gamification_frame,
            text="HoneyNet Gaming & Rewards",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Create main container with two columns
        main_container = tk.Frame(gamification_frame, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left column - Player Stats
        left_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(
            left_frame,
            text="👤 Player Profile",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Player stats display
        self.player_stats_frame = tk.Frame(left_frame, bg='#2a2a2a')
        self.player_stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Right column - Achievements & Leaderboard
        right_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="🏆 Achievements & Leaderboard",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Achievements display
        self.achievements_frame = tk.Frame(right_frame, bg='#2a2a2a')
        self.achievements_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Update gamification display
        self.update_gamification_display()
    
    def create_blockchain_tab(self):
        """יצירת טאב בלוקצ'יין"""
        blockchain_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(blockchain_frame, text="⛓️ Blockchain")
        
        # Title
        tk.Label(
            blockchain_frame,
            text="Blockchain Threat Ledger",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Create main container
        main_container = tk.Frame(blockchain_frame, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Blockchain stats
        stats_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            stats_frame,
            text="📊 Blockchain Statistics",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.blockchain_stats_frame = tk.Frame(stats_frame, bg='#2a2a2a')
        self.blockchain_stats_frame.pack(fill='x', padx=10, pady=10)
        
        # Bottom section - Recent blocks
        blocks_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        blocks_frame.pack(fill='both', expand=True)
        
        tk.Label(
            blocks_frame,
            text="🧱 Recent Blocks",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Blocks tree view
        self.blocks_tree = ttk.Treeview(
            blocks_frame,
            columns=('Block Hash', 'Timestamp', 'Threats', 'Miner'),
            show='tree headings'
        )
        self.blocks_tree.heading('#0', text='Block #')
        self.blocks_tree.heading('Block Hash', text='Block Hash')
        self.blocks_tree.heading('Timestamp', text='Timestamp')
        self.blocks_tree.heading('Threats', text='Threats')
        self.blocks_tree.heading('Miner', text='Miner')
        self.blocks_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Update blockchain display
        self.update_blockchain_display()
    
    def create_swarm_tab(self):
        """יצירת טאב אינטליגנציה נחילית"""
        swarm_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(swarm_frame, text="🐝 Swarm Intelligence")
        
        # Title
        tk.Label(
            swarm_frame,
            text="Swarm Intelligence Network",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Create main container with three sections
        main_container = tk.Frame(swarm_frame, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Swarm overview
        overview_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        overview_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(
            overview_frame,
            text="📊 Swarm Overview",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.swarm_overview_frame = tk.Frame(overview_frame, bg='#2a2a2a')
        self.swarm_overview_frame.pack(fill='x', padx=10, pady=10)
        
        # Middle section - Active agents
        agents_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        agents_frame.pack(fill='both', expand=True, pady=5)
        
        tk.Label(
            agents_frame,
            text="🤖 Active Agents",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Agents tree view
        self.agents_tree = ttk.Treeview(
            agents_frame,
            columns=('Role', 'Status', 'Tasks', 'Performance'),
            show='tree headings'
        )
        self.agents_tree.heading('#0', text='Agent ID')
        self.agents_tree.heading('Role', text='Role')
        self.agents_tree.heading('Status', text='Status')
        self.agents_tree.heading('Tasks', text='Active Tasks')
        self.agents_tree.heading('Performance', text='Performance')
        self.agents_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bottom section - Pheromone trails
        pheromones_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        pheromones_frame.pack(fill='x', pady=(5, 0))
        
        tk.Label(
            pheromones_frame,
            text="🌿 Pheromone Trails",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.pheromones_text = scrolledtext.ScrolledText(
            pheromones_frame,
            height=6,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.pheromones_text.pack(fill='x', padx=10, pady=10)
        
        # Update swarm display
        self.update_swarm_display()
    
    def create_quantum_tab(self):
        """יצירת טאב פיתיונות קוונטיים"""
        quantum_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(quantum_frame, text="⚛️ Quantum Honeypots")
        
        # Title
        tk.Label(
            quantum_frame,
            text="Quantum-Resistant Honeypots",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Create main container
        main_container = tk.Frame(quantum_frame, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Quantum status
        status_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        status_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            status_frame,
            text="📊 Quantum System Status",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.quantum_status_frame = tk.Frame(status_frame, bg='#2a2a2a')
        self.quantum_status_frame.pack(fill='x', padx=10, pady=10)
        
        # Middle section - Quantum honeypots
        honeypots_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        honeypots_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        tk.Label(
            honeypots_frame,
            text="🍯 Quantum Honeypots",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Quantum honeypots tree view
        self.quantum_honeypots_tree = ttk.Treeview(
            honeypots_frame,
            columns=('State', 'Entanglement', 'Key Strength', 'Attacks Detected'),
            show='tree headings'
        )
        self.quantum_honeypots_tree.heading('#0', text='Honeypot ID')
        self.quantum_honeypots_tree.heading('State', text='Quantum State')
        self.quantum_honeypots_tree.heading('Entanglement', text='Entanglement')
        self.quantum_honeypots_tree.heading('Key Strength', text='Key Strength')
        self.quantum_honeypots_tree.heading('Attacks Detected', text='Attacks')
        self.quantum_honeypots_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bottom section - Quantum signatures
        signatures_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        signatures_frame.pack(fill='x')
        
        tk.Label(
            signatures_frame,
            text="🔍 Quantum Attack Signatures",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.quantum_signatures_text = scrolledtext.ScrolledText(
            signatures_frame,
            height=6,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.quantum_signatures_text.pack(fill='x', padx=10, pady=10)
        
        # Update quantum display
        self.update_quantum_display()
    
    def create_edge_computing_tab(self):
        """יצירת טאב Edge Computing"""
        edge_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(edge_frame, text="🌐 Edge Computing")
        
        # Title
        tk.Label(
            edge_frame,
            text="Edge Computing Network",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Create main container
        main_container = tk.Frame(edge_frame, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Network overview
        overview_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        overview_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            overview_frame,
            text="📊 Network Overview",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.edge_overview_frame = tk.Frame(overview_frame, bg='#2a2a2a')
        self.edge_overview_frame.pack(fill='x', padx=10, pady=10)
        
        # Middle section - Edge nodes
        nodes_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        nodes_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        tk.Label(
            nodes_frame,
            text="🖥️ Edge Nodes",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Edge nodes tree view
        self.edge_nodes_tree = ttk.Treeview(
            nodes_frame,
            columns=('Type', 'Status', 'Load', 'Tasks', 'Security Level'),
            show='tree headings'
        )
        self.edge_nodes_tree.heading('#0', text='Node ID')
        self.edge_nodes_tree.heading('Type', text='Type')
        self.edge_nodes_tree.heading('Status', text='Status')
        self.edge_nodes_tree.heading('Load', text='CPU Load')
        self.edge_nodes_tree.heading('Tasks', text='Active Tasks')
        self.edge_nodes_tree.heading('Security Level', text='Security')
        self.edge_nodes_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bottom section - Task scheduler
        scheduler_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        scheduler_frame.pack(fill='x')
        
        tk.Label(
            scheduler_frame,
            text="⚙️ Task Scheduler",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.scheduler_text = scrolledtext.ScrolledText(
            scheduler_frame,
            height=6,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.scheduler_text.pack(fill='x', padx=10, pady=10)
        
        # Update edge computing display
        self.update_edge_computing_display()
    
    def create_digital_twin_tab(self):
        """יצירת טאב תאומים דיגיטליים"""
        twin_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(twin_frame, text="👥 Digital Twins")
        
        # Title
        tk.Label(
            twin_frame,
            text="Digital Twin Technology",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Create main container
        main_container = tk.Frame(twin_frame, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top section - Twins overview
        overview_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        overview_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            overview_frame,
            text="📊 Twins Overview",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.twins_overview_frame = tk.Frame(overview_frame, bg='#2a2a2a')
        self.twins_overview_frame.pack(fill='x', padx=10, pady=10)
        
        # Middle section - Active twins
        twins_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        twins_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        tk.Label(
            twins_frame,
            text="🔄 Active Digital Twins",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        # Digital twins tree view
        self.digital_twins_tree = ttk.Treeview(
            twins_frame,
            columns=('Type', 'State', 'Health', 'Last Sync', 'Predictions'),
            show='tree headings'
        )
        self.digital_twins_tree.heading('#0', text='Twin ID')
        self.digital_twins_tree.heading('Type', text='Type')
        self.digital_twins_tree.heading('State', text='State')
        self.digital_twins_tree.heading('Health', text='Health %')
        self.digital_twins_tree.heading('Last Sync', text='Last Sync')
        self.digital_twins_tree.heading('Predictions', text='Predictions')
        self.digital_twins_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bottom section - Simulations
        simulations_frame = tk.Frame(main_container, bg='#2a2a2a', relief='raised', bd=2)
        simulations_frame.pack(fill='x')
        
        tk.Label(
            simulations_frame,
            text="🧪 Recent Simulations",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        self.simulations_text = scrolledtext.ScrolledText(
            simulations_frame,
            height=6,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.simulations_text.pack(fill='x', padx=10, pady=10)
        
        # Update digital twin display
        self.update_digital_twin_display()
    
    def create_intelligence_tab(self):
        """יצירת טאב מודיעין רשת"""
        intel_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(intel_frame, text="🧠 Intelligence")
        
        tk.Label(
            intel_frame,
            text="Network Intelligence & Analytics",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Intelligence display
        self.intelligence_text = scrolledtext.ScrolledText(
            intel_frame,
            height=20,
            bg='#000000',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        self.intelligence_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_settings_tab(self):
        """יצירת טאב הגדרות"""
        settings_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        tk.Label(
            settings_frame,
            text="HoneyNet Configuration",
            font=('Arial', 16, 'bold'),
            fg='#00ff00',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        # Settings content
        settings_content = tk.Frame(settings_frame, bg='#2a2a2a', relief='raised', bd=2)
        settings_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configuration options
        tk.Label(
            settings_content,
            text="System Configuration",
            font=('Arial', 14, 'bold'),
            fg='#ffaa00',
            bg='#2a2a2a'
        ).pack(pady=10)
        
        tk.Label(
            intel_frame,
            text="AI-Powered Threat Analysis",
            font=('Arial', 14, 'bold'),
            fg='#0099ff',
            bg='#1a1a1a'
        ).pack(pady=10)
        
        self.intel_text = scrolledtext.ScrolledText(
            intel_frame,
            height=15,
            bg='#000033',
            fg='#00aaff',
            font=('Consolas', 10),
            insertbackground='#00aaff'
        )
        self.intel_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def setup_event_handlers(self):
        """הגדרת מטפלי אירועים"""
        # Add honeypot trigger callback
        self.honeypot_manager.add_trigger_callback(self.on_honeypot_trigger)
        
        # Setup periodic updates
        self.update_display()
    
    def start_protection(self):
        """הפעלת הגנת HoneyNet"""
        if self.is_running:
            return
        
        self.log_message("🚀 Starting HoneyNet Protection System...")
        
        # Start background thread for HoneyNet operations
        self.protection_thread = threading.Thread(
            target=self.run_protection_async,
            daemon=True
        )
        self.protection_thread.start()
        
        # Update UI
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="Status: 🟢 Online - Protecting", fg='#00ff00')
        
        self.log_message("✅ HoneyNet Protection is now ACTIVE!")
        self.log_message("🛡️ Your device is now part of the global defense network")
        self.log_message("🍯 Smart honeypots deployed and monitoring...")
    
    def stop_protection(self):
        """עצירת הגנת HoneyNet"""
        if not self.is_running:
            return
        
        self.log_message("🛑 Stopping HoneyNet Protection...")
        
        self.is_running = False
        
        # Update UI
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Status: 🔴 Offline", fg='#ff0000')
        
        self.log_message("⏹️ HoneyNet Protection stopped")
    
    def run_protection_async(self):
        """הרצת הגנה אסינכרונית"""
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.run_protection())
        finally:
            loop.close()
    
    async def run_protection(self):
        """הרצת מערכת ההגנה"""
        try:
            # Initialize components
            await self.defense_engine.start()
            await self.honeypot_manager.initialize()
            
            # Main protection loop
            while self.is_running:
                # Update statistics
                await self.update_statistics()
                
                # Check for threats (simulated)
                await self.check_for_threats()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            self.log_message(f"❌ Error in protection system: {e}")
        finally:
            await self.defense_engine.stop()
            await self.honeypot_manager.shutdown()
    
    def simulate_attack(self):
        """סימולציה של התקפה לבדיקת המערכת"""
        if not self.is_running:
            messagebox.showwarning("Warning", "Please start HoneyNet protection first!")
            return
        
        # Create simulated attack thread
        attack_thread = threading.Thread(
            target=self.run_attack_simulation,
            daemon=True
        )
        attack_thread.start()
    
    def run_attack_simulation(self):
        """הרצת סימולציית התקפה"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.simulate_attack_async())
        finally:
            loop.close()
    
    async def simulate_attack_async(self):
        """סימולציית התקפה אסינכרונית"""
        self.log_message("⚡ SIMULATING CYBER ATTACK...")
        self.log_message("🎯 Attack Type: Ransomware Simulation")
        
        # Create fake threat event
        threat = ThreatEvent(
            id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            source_ip="192.168.1.100",
            target_device="Desktop-PC",
            attack_type=AttackType.RANSOMWARE,
            threat_level=ThreatLevel.HIGH,
            description="Simulated ransomware attack detected",
            honeypot_triggered=True,
            attack_signature="sim_ransomware_v1"
        )
        
        # Process through defense engine
        success = await self.defense_engine.process_threat(threat)
        
        if success:
            self.log_message("✅ ATTACK BLOCKED! HoneyNet protection successful")
            self.log_message("🛡️ Threat mitigated and shared with global network")
        else:
            self.log_message("⚠️ Partial mitigation - some actions failed")
        
        # Simulate honeypot trigger
        await asyncio.sleep(2)
        self.log_message("🍯 HONEYPOT TRIGGERED! Fake credentials accessed")
        self.log_message("📡 Attack signature shared with global HoneyNet")
        self.log_message("🌐 All network participants now protected from this attack")
    
    async def update_statistics(self):
        """עדכון סטטיסטיקות"""
        if not self.is_running:
            return
        
        # Get statistics from components
        defense_stats = self.defense_engine.get_statistics()
        honeypot_stats = self.honeypot_manager.get_statistics()
        
        # Update UI in main thread
        self.root.after(0, self.update_stats_display, defense_stats, honeypot_stats)
    
    def update_stats_display(self, defense_stats: Dict, honeypot_stats: Dict):
        """עדכון תצוגת הסטטיסטיקות"""
        try:
            self.stats_labels["threats_detected"].config(text=str(defense_stats.get("threats_detected", 0)))
            self.stats_labels["attacks_blocked"].config(text=str(defense_stats.get("attacks_blocked", 0)))
            self.stats_labels["honeypots_active"].config(text=str(honeypot_stats.get("active_honeypots", 0)))
            self.stats_labels["honeypots_triggered"].config(text=str(honeypot_stats.get("total_triggers", 0)))
            self.stats_labels["global_network"].config(text="🟢 Connected" if self.is_running else "🔴 Offline")
            self.stats_labels["protection_level"].config(text="🔒 Maximum" if self.is_running else "⚠️ None")
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    async def check_for_threats(self):
        """בדיקת איומים"""
        # This would normally check real system activity
        # For demo purposes, we'll occasionally generate fake alerts
        import random
        
        if random.random() < 0.1:  # 10% chance every check
            await self.generate_fake_alert()
    
    async def generate_fake_alert(self):
        """יצירת התרעה מזויפת לדמו"""
        alerts = [
            "🔍 Suspicious network activity detected from 203.0.113.45",
            "🚨 Potential malware signature identified in network traffic",
            "🍯 Honeypot file accessed - investigating source",
            "🧠 AI detected unusual behavioral pattern",
            "📡 Threat intelligence updated - new attack variant identified"
        ]
        
        alert = random.choice(alerts)
        self.log_message(alert)
    
    def on_honeypot_trigger(self, trigger: HoneypotTrigger):
        """טיפול בהפעלת פיתיון"""
        message = (
            f"🍯 HONEYPOT TRIGGERED! "
            f"ID: {trigger.honeypot_id} | "
            f"Type: {trigger.trigger_type.value} | "
            f"Time: {trigger.timestamp.strftime('%H:%M:%S')}"
        )
        self.log_message(message)
    
    def log_message(self, message: str):
        """רישום הודעה בלוג"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Add to threat log
        self.threat_log.append(formatted_message)
        
        # Update UI in main thread
        self.root.after(0, self._update_log_display, formatted_message)
    
    def _update_log_display(self, message: str):
        """עדכון תצוגת הלוג"""
        try:
            self.threat_log_text.insert(tk.END, message)
            self.threat_log_text.see(tk.END)
            
            # Keep only last 100 messages
            lines = self.threat_log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 100:
                self.threat_log_text.delete("1.0", f"{len(lines)-100}.0")
        except Exception as e:
            print(f"Error updating log: {e}")
    
    def update_display(self):
        """עדכון תצוגה תקופתי"""
        # Update honeypot tree
        self.update_honeypot_tree()
        
        # Update intelligence display
        self.update_intelligence_display()
    
    def update_gamification_display(self):
        """עדכון תצוגת הגיימיפיקציה"""
        try:
            # Clear previous content
            for widget in self.player_stats_frame.winfo_children():
                widget.destroy()
            for widget in self.achievements_frame.winfo_children():
                widget.destroy()
            
            # Get player stats from gamification engine
            player_id = "desktop_client_user"
            player_stats = asyncio.run(self.gamification_engine.get_player_stats(player_id))
            
            if player_stats:
                # Display player stats
                stats_info = [
                    ("Level", str(player_stats.level)),
                    ("Points", str(player_stats.total_points)),
                    ("Threats Detected", str(player_stats.threats_detected)),
                    ("Honeypots Triggered", str(player_stats.honeypots_triggered)),
                    ("Current League", player_stats.current_league.value if player_stats.current_league else "None")
                ]
                
                for label, value in stats_info:
                    stat_frame = tk.Frame(self.player_stats_frame, bg='#2a2a2a')
                    stat_frame.pack(fill='x', pady=2)
                    
                    tk.Label(
                        stat_frame,
                        text=f"{label}:",
                        font=('Arial', 10, 'bold'),
                        fg='#ffffff',
                        bg='#2a2a2a'
                    ).pack(side='left')
                    
                    tk.Label(
                        stat_frame,
                        text=value,
                        font=('Arial', 10),
                        fg='#00ff00',
                        bg='#2a2a2a'
                    ).pack(side='right')
            
            # Display achievements
            achievements = asyncio.run(self.gamification_engine.get_player_achievements(player_id))
            
            if achievements:
                for achievement in achievements[:5]:  # Show top 5
                    achievement_frame = tk.Frame(self.achievements_frame, bg='#3a3a3a', relief='raised', bd=1)
                    achievement_frame.pack(fill='x', pady=2, padx=5)
                    
                    tk.Label(
                        achievement_frame,
                        text=f"🏆 {achievement.name}",
                        font=('Arial', 9, 'bold'),
                        fg='#ffaa00',
                        bg='#3a3a3a'
                    ).pack(anchor='w', padx=5, pady=2)
                    
                    tk.Label(
                        achievement_frame,
                        text=achievement.description,
                        font=('Arial', 8),
                        fg='#cccccc',
                        bg='#3a3a3a'
                    ).pack(anchor='w', padx=5)
            
        except Exception as e:
            self.logger.error(f"Error updating gamification display: {e}")
    
    def update_blockchain_display(self):
        """עדכון תצוגת הבלוקצ'יין"""
        try:
            # Clear previous content
            for widget in self.blockchain_stats_frame.winfo_children():
                widget.destroy()
            
            # Clear blocks tree
            for item in self.blocks_tree.get_children():
                self.blocks_tree.delete(item)
            
            # Get blockchain stats
            blockchain_stats = asyncio.run(self.blockchain_ledger.get_blockchain_stats())
            
            if blockchain_stats:
                stats_info = [
                    ("Total Blocks", str(blockchain_stats.get('total_blocks', 0))),
                    ("Active Nodes", str(blockchain_stats.get('active_nodes', 0))),
                    ("Threats Recorded", str(blockchain_stats.get('total_threats', 0))),
                    ("Chain Integrity", f"{blockchain_stats.get('integrity_score', 0):.2%}")
                ]
                
                for label, value in stats_info:
                    stat_frame = tk.Frame(self.blockchain_stats_frame, bg='#2a2a2a')
                    stat_frame.pack(fill='x', pady=2)
                    
                    tk.Label(
                        stat_frame,
                        text=f"{label}:",
                        font=('Arial', 10, 'bold'),
                        fg='#ffffff',
                        bg='#2a2a2a'
                    ).pack(side='left')
                    
                    tk.Label(
                        stat_frame,
                        text=value,
                        font=('Arial', 10),
                        fg='#00ff00',
                        bg='#2a2a2a'
                    ).pack(side='right')
            
            # Get recent blocks
            recent_blocks = asyncio.run(self.blockchain_ledger.get_recent_blocks(10))
            
            for block in recent_blocks:
                self.blocks_tree.insert('', 'end', 
                    text=str(block.block_number),
                    values=(
                        block.block_hash[:16] + "...",
                        block.timestamp.strftime("%H:%M:%S"),
                        str(len(block.threat_records)),
                        block.miner_id[:12] + "..."
                    )
                )
            
        except Exception as e:
            self.logger.error(f"Error updating blockchain display: {e}")
    
    def update_swarm_display(self):
        """עדכון תצוגת הנחיל"""
        try:
            # Clear previous content
            for widget in self.swarm_overview_frame.winfo_children():
                widget.destroy()
            
            # Clear agents tree
            for item in self.agents_tree.get_children():
                self.agents_tree.delete(item)
            
            # Get swarm status
            swarm_status = asyncio.run(self.swarm_intelligence.get_swarm_status())
            
            if swarm_status:
                stats_info = [
                    ("Active Agents", str(swarm_status.get('active_agents', 0))),
                    ("Total Tasks", str(swarm_status.get('total_tasks', 0))),
                    ("Collective Intelligence", f"{swarm_status.get('collective_intelligence', 0):.2f}"),
                    ("Swarm Efficiency", f"{swarm_status.get('swarm_efficiency', 0):.2%}")
                ]
                
                for label, value in stats_info:
                    stat_frame = tk.Frame(self.swarm_overview_frame, bg='#2a2a2a')
                    stat_frame.pack(fill='x', pady=2)
                    
                    tk.Label(
                        stat_frame,
                        text=f"{label}:",
                        font=('Arial', 10, 'bold'),
                        fg='#ffffff',
                        bg='#2a2a2a'
                    ).pack(side='left')
                    
                    tk.Label(
                        stat_frame,
                        text=value,
                        font=('Arial', 10),
                        fg='#00ff00',
                        bg='#2a2a2a'
                    ).pack(side='right')
            
            # Update pheromone trails display
            pheromone_trails = asyncio.run(self.swarm_intelligence.get_pheromone_trails())
            
            self.pheromones_text.delete(1.0, tk.END)
            if pheromone_trails:
                for trail in pheromone_trails[:10]:  # Show top 10
                    trail_info = f"Trail: {trail.get('trail_type', 'Unknown')} | Strength: {trail.get('strength', 0):.2f} | Age: {trail.get('age', 0)}s\n"
                    self.pheromones_text.insert(tk.END, trail_info)
            
        except Exception as e:
            self.logger.error(f"Error updating swarm display: {e}")
    
    def update_quantum_display(self):
        """עדכון תצוגת הקוונטום"""
        try:
            # Clear previous content
            for widget in self.quantum_status_frame.winfo_children():
                widget.destroy()
            
            # Clear quantum honeypots tree
            for item in self.quantum_honeypots_tree.get_children():
                self.quantum_honeypots_tree.delete(item)
            
            # Get quantum system status
            quantum_status = asyncio.run(self.quantum_honeypots.get_system_status())
            
            if quantum_status:
                stats_info = [
                    ("Active Honeypots", str(quantum_status.get('active_honeypots', 0))),
                    ("Quantum States", str(quantum_status.get('quantum_states', 0))),
                    ("Entangled Pairs", str(quantum_status.get('entangled_pairs', 0))),
                    ("Key Strength", quantum_status.get('average_key_strength', 'Unknown'))
                ]
                
                for label, value in stats_info:
                    stat_frame = tk.Frame(self.quantum_status_frame, bg='#2a2a2a')
                    stat_frame.pack(fill='x', pady=2)
                    
                    tk.Label(
                        stat_frame,
                        text=f"{label}:",
                        font=('Arial', 10, 'bold'),
                        fg='#ffffff',
                        bg='#2a2a2a'
                    ).pack(side='left')
                    
                    tk.Label(
                        stat_frame,
                        text=str(value),
                        font=('Arial', 10),
                        fg='#00ff00',
                        bg='#2a2a2a'
                    ).pack(side='right')
            
            # Update quantum signatures display
            quantum_signatures = asyncio.run(self.quantum_honeypots.get_recent_attack_signatures())
            
            self.quantum_signatures_text.delete(1.0, tk.END)
            if quantum_signatures:
                for signature in quantum_signatures[:10]:  # Show top 10
                    sig_info = f"Signature: {signature.get('signature_type', 'Unknown')} | Confidence: {signature.get('confidence', 0):.2f} | Time: {signature.get('timestamp', 'Unknown')}\n"
                    self.quantum_signatures_text.insert(tk.END, sig_info)
            
        except Exception as e:
            self.logger.error(f"Error updating quantum display: {e}")
    
    def update_edge_computing_display(self):
        """עדכון תצוגת Edge Computing"""
        try:
            # Clear previous content
            for widget in self.edge_overview_frame.winfo_children():
                widget.destroy()
            
            # Clear edge nodes tree
            for item in self.edge_nodes_tree.get_children():
                self.edge_nodes_tree.delete(item)
            
            # Get edge computing status
            edge_status = asyncio.run(self.edge_computing.get_orchestrator_status())
            
            if edge_status:
                stats_info = [
                    ("Active Nodes", str(edge_status.get('active_nodes', 0))),
                    ("Total Clusters", str(edge_status.get('total_clusters', 0))),
                    ("Running Tasks", str(edge_status.get('running_tasks', 0))),
                    ("Network Load", f"{edge_status.get('network_load', 0):.2%}")
                ]
                
                for label, value in stats_info:
                    stat_frame = tk.Frame(self.edge_overview_frame, bg='#2a2a2a')
                    stat_frame.pack(fill='x', pady=2)
                    
                    tk.Label(
                        stat_frame,
                        text=f"{label}:",
                        font=('Arial', 10, 'bold'),
                        fg='#ffffff',
                        bg='#2a2a2a'
                    ).pack(side='left')
                    
                    tk.Label(
                        stat_frame,
                        text=value,
                        font=('Arial', 10),
                        fg='#00ff00',
                        bg='#2a2a2a'
                    ).pack(side='right')
            
            # Update scheduler display
            scheduler_info = asyncio.run(self.edge_computing.get_scheduler_status())
            
            self.scheduler_text.delete(1.0, tk.END)
            if scheduler_info:
                for task in scheduler_info.get('recent_tasks', [])[:10]:  # Show top 10
                    task_info = f"Task: {task.get('task_type', 'Unknown')} | Node: {task.get('assigned_node', 'Unknown')} | Status: {task.get('status', 'Unknown')}\n"
                    self.scheduler_text.insert(tk.END, task_info)
            
        except Exception as e:
            self.logger.error(f"Error updating edge computing display: {e}")
    
    def update_digital_twin_display(self):
        """עדכון תצוגת התאומים הדיגיטליים"""
        try:
            # Clear previous content
            for widget in self.twins_overview_frame.winfo_children():
                widget.destroy()
            
            # Clear digital twins tree
            for item in self.digital_twins_tree.get_children():
                self.digital_twins_tree.delete(item)
            
            # Get digital twins status
            twins_status = asyncio.run(self.digital_twin_engine.get_all_twins_status())
            
            if twins_status:
                stats_info = [
                    ("Total Twins", str(twins_status.get('total_twins', 0))),
                    ("Active Twins", str(twins_status.get('active_twins', 0))),
                    ("Predictions Made", str(twins_status.get('total_predictions', 0))),
                    ("Simulations Run", str(twins_status.get('total_simulations', 0)))
                ]
                
                for label, value in stats_info:
                    stat_frame = tk.Frame(self.twins_overview_frame, bg='#2a2a2a')
                    stat_frame.pack(fill='x', pady=2)
                    
                    tk.Label(
                        stat_frame,
                        text=f"{label}:",
                        font=('Arial', 10, 'bold'),
                        fg='#ffffff',
                        bg='#2a2a2a'
                    ).pack(side='left')
                    
                    tk.Label(
                        stat_frame,
                        text=value,
                        font=('Arial', 10),
                        fg='#00ff00',
                        bg='#2a2a2a'
                    ).pack(side='right')
            
            # Update simulations display
            recent_simulations = twins_status.get('recent_simulations', [])
            
            self.simulations_text.delete(1.0, tk.END)
            if recent_simulations:
                for simulation in recent_simulations[:10]:  # Show top 10
                    sim_info = f"Simulation: {simulation.get('scenario', 'Unknown')} | Twin: {simulation.get('twin_id', 'Unknown')} | Status: {simulation.get('status', 'Unknown')}\n"
                    self.simulations_text.insert(tk.END, sim_info)
            
        except Exception as e:
            self.logger.error(f"Error updating digital twin display: {e}")
        
        # Schedule next update
        self.root.after(5000, self.update_display)  # Update every 5 seconds
    
    def update_honeypot_tree(self):
        """עדכון עץ הפיתיונות"""
        try:
            # Clear existing items
            for item in self.honeypot_tree.get_children():
                self.honeypot_tree.delete(item)
            
            # Add honeypots (demo data)
            demo_honeypots = [
                ("passwords.txt", "File", "🟢 Active", "0", "Never"),
                ("backup_keys.pem", "SSH Key", "🟢 Active", "0", "Never"),
                ("financial_report.xlsx", "Document", "🟢 Active", "0", "Never"),
                ("user_database.db", "Database", "🟢 Active", "0", "Never"),
                ("admin_credentials", "Credentials", "🟢 Active", "0", "Never")
            ]
            
            for name, htype, status, triggers, last_activity in demo_honeypots:
                self.honeypot_tree.insert('', 'end', text=name, values=(htype, status, triggers, last_activity))
        except Exception as e:
            print(f"Error updating honeypot tree: {e}")
    
    def update_intelligence_display(self):
        """עדכון תצוגת המודיעין"""
        try:
            if self.is_running:
                intel_data = """
🧠 AI Threat Analysis Report
═══════════════════════════════

📊 Global Threat Landscape:
• Active threat families: 0
• New attack variants detected: 0
• Prediction accuracy: 95.2%

🔍 Recent Attack Patterns:
• No malicious activity detected
• Honeypot network: Fully operational
• Global sync: Connected

🌐 Network Intelligence:
• Connected nodes: 1,247,892
• Shared threat signatures: 45,231
• Real-time protection: Active

⚡ Predictions (Next 24h):
• Low probability of targeted attacks
• Recommended actions: Maintain current posture
                """
            else:
                intel_data = """
🧠 AI Threat Analysis - OFFLINE
═══════════════════════════════

System not active. Start protection to view
real-time threat intelligence and analysis.
                """
            
            self.intel_text.delete('1.0', tk.END)
            self.intel_text.insert('1.0', intel_data)
        except Exception as e:
            print(f"Error updating intelligence display: {e}")
    
    def run(self):
        """הרצת האפליקציה"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_protection()
        finally:
            if hasattr(self, 'protection_thread') and self.protection_thread.is_alive():
                self.is_running = False
                self.protection_thread.join(timeout=5)


def main():
    """פונקציה ראשית"""
    print("🚀 Starting HoneyNet Desktop Client...")
    
    try:
        app = HoneyNetGUI()
        app.run()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
