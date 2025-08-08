"""
HoneyNet Smart Honeypots Module
מודול הפיתיונות החכמים של HoneyNet
"""

from .smart_honeypot import SmartHoneypot, HoneypotManager
from .fake_assets import FakeAssetGenerator
from .trap_detector import TrapDetector

__all__ = ["SmartHoneypot", "HoneypotManager", "FakeAssetGenerator", "TrapDetector"]
