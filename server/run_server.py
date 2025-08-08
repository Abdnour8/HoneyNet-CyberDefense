#!/usr/bin/env python3
"""
HoneyNet Global Server - Startup Script
סקריפט הפעלה לשרת HoneyNet הגלובלי
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

console = Console()

def setup_logging():
    """הגדרת לוגים"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('server/logs/honeynet_server.log', encoding='utf-8')
        ]
    )

def create_directories():
    """יצירת תיקיות נדרשות"""
    directories = [
        'server/logs',
        'server/data',
        'server/temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def check_requirements():
    """בדיקת דרישות מערכת"""
    try:
        import fastapi
        import uvicorn
        import redis
        import numpy
        import tensorflow
        console.print("✅ כל הדרישות מותקנות", style="green")
        return True
    except ImportError as e:
        console.print(f"❌ חסרה דרישה: {e}", style="red")
        console.print("הרץ: pip install -r server/requirements.txt", style="yellow")
        return False

def display_banner():
    """הצגת באנר הפתיחה"""
    banner_text = Text()
    banner_text.append("🍯 HoneyNet Global Server 🍯\n", style="bold yellow")
    banner_text.append("מערכת הגנה קולקטיבית גלובלית\n", style="cyan")
    banner_text.append("Global Collective Defense System\n", style="cyan")
    banner_text.append("Version 1.0.0", style="dim")
    
    panel = Panel(
        banner_text,
        title="🌐 HoneyNet Global Coordination Server",
        border_style="bright_blue",
        padding=(1, 2)
    )
    
    console.print(panel)

def display_server_info():
    """הצגת מידע השרת"""
    info_text = Text()
    info_text.append("🚀 Server Information:\n", style="bold")
    info_text.append("• Host: 0.0.0.0\n", style="white")
    info_text.append("• Port: 8000\n", style="white")
    info_text.append("• WebSocket: ws://localhost:8000/ws\n", style="white")
    info_text.append("• API Docs: http://localhost:8000/docs\n", style="white")
    info_text.append("• Health Check: http://localhost:8000/api/v1/health\n", style="white")
    info_text.append("\n📊 Available Services:\n", style="bold")
    info_text.append("• Global Analytics\n", style="green")
    info_text.append("• AI Threat Coordinator\n", style="green")
    info_text.append("• WebSocket Connection Manager\n", style="green")
    info_text.append("• REST API Endpoints\n", style="green")
    
    panel = Panel(
        info_text,
        title="📡 Server Configuration",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(panel)

def main():
    """פונקציה ראשית"""
    try:
        # Display banner
        display_banner()
        
        # Setup logging
        setup_logging()
        console.print("📝 Logging configured", style="green")
        
        # Create directories
        create_directories()
        console.print("📁 Directories created", style="green")
        
        # Check requirements
        if not check_requirements():
            console.print("❌ Requirements check failed. Exiting...", style="red")
            sys.exit(1)
        
        # Display server info
        display_server_info()
        
        # Start server
        console.print("\n🚀 Starting HoneyNet Global Server...", style="bold yellow")
        
        # Run with uvicorn
        uvicorn.run(
            "server.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            ws_ping_interval=30,
            ws_ping_timeout=10
        )
        
    except KeyboardInterrupt:
        console.print("\n🛑 Server stopped by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Server error: {e}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
