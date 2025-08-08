#!/usr/bin/env python3
"""
HoneyNet Global Server - Demo Script
סקריפט הדגמה לשרת HoneyNet הגלובלי
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List
import websockets
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

console = Console()

class HoneyNetServerDemo:
    """מחלקה להדגמת השרת הגלובלי"""
    
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8000/ws"
        self.demo_clients = []
        self.demo_token = "demo_token_12345"
        
    def display_banner(self):
        """הצגת באנר הדגמה"""
        banner_text = """🍯 HoneyNet Global Server Demo 🍯
מערכת הדגמה לשרת הגלובלי
Global Server Demonstration System"""
        
        panel = Panel(
            banner_text,
            title="🌐 Server Demo",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    async def check_server_health(self) -> bool:
        """בדיקת בריאות השרת"""
        try:
            response = requests.get(f"{self.server_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                console.print("✅ Server is healthy", style="green")
                console.print(f"   Status: {data.get('status')}")
                console.print(f"   Version: {data.get('version')}")
                return True
            else:
                console.print(f"❌ Server health check failed: {response.status_code}", style="red")
                return False
        except Exception as e:
            console.print(f"❌ Cannot connect to server: {e}", style="red")
            console.print("   Make sure the server is running on localhost:8000", style="yellow")
            return False
    
    async def simulate_client_connections(self, num_clients: int = 5):
        """סימולציה של חיבורי לקוחות"""
        console.print(f"\n🔗 Simulating {num_clients} client connections...")
        
        async def connect_client(client_id: str):
            try:
                uri = f"{self.websocket_url}?client_id={client_id}&client_type=demo&region=demo_region"
                
                async with websockets.connect(uri) as websocket:
                    # Send registration
                    registration = {
                        "type": "register",
                        "client_id": client_id,
                        "client_type": "demo_client",
                        "version": "1.0.0",
                        "region": f"region_{random.randint(1, 5)}"
                    }
                    
                    await websocket.send(json.dumps(registration))
                    
                    # Wait for response
                    response = await websocket.recv()
                    console.print(f"   ✅ Client {client_id} connected")
                    
                    # Keep connection alive for demo
                    await asyncio.sleep(2)
                    
            except Exception as e:
                console.print(f"   ❌ Client {client_id} failed to connect: {e}")
        
        # Connect multiple clients
        tasks = []
        for i in range(num_clients):
            client_id = f"demo_client_{i+1}"
            tasks.append(connect_client(client_id))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def simulate_threat_reports(self, num_threats: int = 10):
        """סימולציה של דיווחי איומים"""
        console.print(f"\n🚨 Simulating {num_threats} threat reports...")
        
        threat_types = ["malware", "phishing", "ddos", "ransomware", "botnet"]
        severities = ["low", "medium", "high", "critical"]
        regions = ["US", "EU", "ASIA", "AFRICA", "OCEANIA"]
        
        for i in range(num_threats):
            threat_data = {
                "type": random.choice(threat_types),
                "severity": random.choice(severities),
                "source_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "target": f"target_{i+1}",
                "region": random.choice(regions),
                "client_id": f"demo_client_{random.randint(1, 5)}"
            }
            
            try:
                headers = {"Authorization": f"Bearer {self.demo_token}"}
                response = requests.post(
                    f"{self.server_url}/api/v1/threats/report",
                    json=threat_data,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    console.print(f"   ✅ Threat {i+1}: {threat_data['type']} ({threat_data['severity']})")
                else:
                    console.print(f"   ❌ Failed to report threat {i+1}: {response.status_code}")
                    
            except Exception as e:
                console.print(f"   ❌ Error reporting threat {i+1}: {e}")
            
            await asyncio.sleep(0.5)  # Small delay between reports
    
    async def simulate_honeypot_triggers(self, num_triggers: int = 8):
        """סימולציה של הפעלות פיתיונות"""
        console.print(f"\n🍯 Simulating {num_triggers} honeypot triggers...")
        
        honeypot_types = ["fake_file", "fake_service", "fake_credential", "fake_database", "fake_api"]
        
        for i in range(num_triggers):
            honeypot_data = {
                "honeypot_type": random.choice(honeypot_types),
                "client_id": f"demo_client_{random.randint(1, 5)}",
                "trigger_id": f"trigger_{i+1}",
                "effectiveness_score": random.uniform(0.5, 1.0),
                "attacker_fingerprint": {
                    "user_agent": f"AttackerBot_{random.randint(1, 10)}",
                    "ip_range": f"10.0.{random.randint(1, 255)}.0/24"
                },
                "region": random.choice(["US", "EU", "ASIA"])
            }
            
            try:
                headers = {"Authorization": f"Bearer {self.demo_token}"}
                response = requests.post(
                    f"{self.server_url}/api/v1/honeypots/trigger",
                    json=honeypot_data,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    console.print(f"   ✅ Honeypot {i+1}: {honeypot_data['honeypot_type']} (score: {honeypot_data['effectiveness_score']:.2f})")
                else:
                    console.print(f"   ❌ Failed to report honeypot trigger {i+1}: {response.status_code}")
                    
            except Exception as e:
                console.print(f"   ❌ Error reporting honeypot trigger {i+1}: {e}")
            
            await asyncio.sleep(0.3)
    
    async def get_global_statistics(self):
        """קבלת סטטיסטיקות גלובליות"""
        console.print("\n📊 Fetching global statistics...")
        
        try:
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            response = requests.get(
                f"{self.server_url}/api/v1/statistics/global",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {})
                
                # Create statistics table
                table = Table(title="🌐 Global Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                # Network stats
                network = stats.get("network", {})
                table.add_row("Active Nodes", str(network.get("total_active_nodes", 0)))
                table.add_row("Network Health", f"{network.get('network_health_score', 0):.2f}")
                table.add_row("Network Coverage", f"{network.get('network_coverage', 0):.2%}")
                
                # Threat stats
                threats = stats.get("threats", {})
                table.add_row("Total Threats", str(threats.get("total_detected", 0)))
                table.add_row("Blocked Threats", str(threats.get("total_blocked", 0)))
                table.add_row("Block Rate", f"{threats.get('block_rate', 0):.1f}%")
                table.add_row("Threats/Minute", str(threats.get("threats_per_minute", 0)))
                
                # Honeypot stats
                honeypots = stats.get("honeypots", {})
                table.add_row("Honeypots Triggered", str(honeypots.get("total_triggered", 0)))
                table.add_row("Avg Effectiveness", f"{honeypots.get('average_effectiveness', 0):.2f}")
                
                # Performance stats
                performance = stats.get("performance", {})
                table.add_row("Detection Accuracy", f"{performance.get('detection_accuracy', 0):.2%}")
                table.add_row("Response Time", f"{performance.get('average_response_time', 0):.3f}s")
                
                console.print(table)
                
                # Show threat breakdown
                if threats.get("by_type"):
                    console.print("\n🎯 Threat Types:")
                    for threat_type, count in threats["by_type"].items():
                        console.print(f"   • {threat_type}: {count}")
                
            else:
                console.print(f"❌ Failed to get statistics: {response.status_code}")
                
        except Exception as e:
            console.print(f"❌ Error getting statistics: {e}")
    
    async def get_threat_trends(self):
        """קבלת מגמות איומים"""
        console.print("\n📈 Fetching threat trends...")
        
        try:
            headers = {"Authorization": f"Bearer {self.demo_token}"}
            response = requests.get(
                f"{self.server_url}/api/v1/statistics/trends?hours=24",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trends = data.get("trends", [])
                
                if trends:
                    table = Table(title="📈 Threat Trends (24h)")
                    table.add_column("Threat Type", style="cyan")
                    table.add_column("Current", style="green")
                    table.add_column("Previous", style="yellow")
                    table.add_column("Trend", style="magenta")
                    table.add_column("Change", style="red")
                    
                    for trend in trends[:10]:  # Show top 10
                        trend_icon = "📈" if trend["trend_direction"] == "increasing" else "📉" if trend["trend_direction"] == "decreasing" else "➡️"
                        table.add_row(
                            trend["threat_type"],
                            str(trend["current_count"]),
                            str(trend["previous_count"]),
                            f"{trend_icon} {trend['trend_direction']}",
                            f"{trend['trend_percentage']:+.1f}%"
                        )
                    
                    console.print(table)
                else:
                    console.print("   No trend data available yet")
                    
            else:
                console.print(f"❌ Failed to get trends: {response.status_code}")
                
        except Exception as e:
            console.print(f"❌ Error getting trends: {e}")
    
    async def test_api_endpoints(self):
        """בדיקת נקודות קצה של API"""
        console.print("\n🔍 Testing API endpoints...")
        
        endpoints = [
            ("/api/v1/health", "GET"),
            ("/api/v1/status", "GET"),
            ("/api/v1/network/nodes", "GET"),
            ("/api/v1/config/global", "GET"),
        ]
        
        headers = {"Authorization": f"Bearer {self.demo_token}"}
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.server_url}{endpoint}", headers=headers, timeout=5)
                else:
                    response = requests.post(f"{self.server_url}{endpoint}", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    console.print(f"   ✅ {method} {endpoint}")
                else:
                    console.print(f"   ❌ {method} {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                console.print(f"   ❌ {method} {endpoint} - Error: {e}")
    
    async def run_full_demo(self):
        """הרצת הדגמה מלאה"""
        self.display_banner()
        
        # Check server health
        if not await self.check_server_health():
            console.print("\n❌ Server is not available. Please start the server first:", style="red")
            console.print("   python server/run_server.py", style="yellow")
            return
        
        console.print("\n🚀 Starting full demo...", style="bold green")
        
        # Test API endpoints
        await self.test_api_endpoints()
        
        # Simulate client connections
        await self.simulate_client_connections(5)
        
        # Simulate threat reports
        await self.simulate_threat_reports(15)
        
        # Simulate honeypot triggers
        await self.simulate_honeypot_triggers(10)
        
        # Wait a bit for processing
        console.print("\n⏳ Processing data...", style="yellow")
        await asyncio.sleep(3)
        
        # Get statistics
        await self.get_global_statistics()
        
        # Get trends
        await self.get_threat_trends()
        
        console.print("\n✅ Demo completed successfully!", style="bold green")
        console.print("\n📖 Next steps:", style="bold")
        console.print("   • Check the server logs for detailed information")
        console.print("   • Visit http://localhost:8000/docs for API documentation")
        console.print("   • Connect real clients to test the WebSocket functionality")
        console.print("   • Monitor the global statistics in real-time")

async def main():
    """פונקציה ראשית"""
    demo = HoneyNetServerDemo()
    
    try:
        await demo.run_full_demo()
    except KeyboardInterrupt:
        console.print("\n🛑 Demo stopped by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Demo error: {e}", style="red")

if __name__ == "__main__":
    asyncio.run(main())
