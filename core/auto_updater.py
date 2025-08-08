"""
HoneyNet Auto Updater
מערכת עדכונים אוטומטיים למשתמשים אמיתיים
"""

import asyncio
import logging
import json
import aiohttp
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import zipfile
import shutil


class UpdateType(Enum):
    """סוגי עדכונים"""
    SECURITY = "security"
    FEATURE = "feature"
    BUGFIX = "bugfix"
    CRITICAL = "critical"


class UpdateStatus(Enum):
    """סטטוס עדכון"""
    AVAILABLE = "available"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class UpdateInfo:
    """מידע על עדכון"""
    version: str
    update_type: UpdateType
    title: str
    description: str
    download_url: str
    file_size: int
    checksum: str
    release_date: datetime
    is_critical: bool = False
    requires_restart: bool = False


class AutoUpdater:
    """מערכת עדכונים אוטומטיים"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.update_server_url = self.config.get("update_server_url", "https://api.honeynet.com/updates")
        self.current_version = self.config.get("current_version", "1.0.0")
        self.auto_update_enabled = self.config.get("auto_update_enabled", True)
        self.auto_install_security = self.config.get("auto_install_security", True)
        self.check_interval_hours = self.config.get("check_interval_hours", 6)
        
        # State
        self.available_updates: List[UpdateInfo] = []
        self.update_history: List[Dict[str, Any]] = []
        self.last_check: Optional[datetime] = None
        self.is_updating = False
        
        # Paths
        self.updates_dir = "updates"
        self.backup_dir = "backups"
        os.makedirs(self.updates_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.logger.info("🔄 Auto Updater initialized")
    
    async def check_for_updates(self) -> List[UpdateInfo]:
        """בדיקת עדכונים זמינים"""
        if not self.auto_update_enabled:
            return []
        
        self.logger.info("🔍 Checking for updates...")
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "User-Agent": f"HoneyNet/{self.current_version}",
                    "X-Current-Version": self.current_version
                }
                
                async with session.get(f"{self.update_server_url}/check", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        updates = []
                        
                        for update_data in data.get("updates", []):
                            update = UpdateInfo(
                                version=update_data["version"],
                                update_type=UpdateType(update_data["type"]),
                                title=update_data["title"],
                                description=update_data["description"],
                                download_url=update_data["download_url"],
                                file_size=update_data["file_size"],
                                checksum=update_data["checksum"],
                                release_date=datetime.fromisoformat(update_data["release_date"]),
                                is_critical=update_data.get("is_critical", False),
                                requires_restart=update_data.get("requires_restart", False)
                            )
                            updates.append(update)
                        
                        self.available_updates = updates
                        self.last_check = datetime.now()
                        
                        if updates:
                            self.logger.info(f"📦 Found {len(updates)} available updates")
                        else:
                            self.logger.info("✅ No updates available")
                        
                        return updates
                    
                    elif response.status == 204:
                        # No updates available
                        self.available_updates = []
                        self.last_check = datetime.now()
                        self.logger.info("✅ No updates available")
                        return []
                    
                    else:
                        self.logger.error(f"Update check failed: HTTP {response.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return []
    
    async def download_update(self, update: UpdateInfo) -> bool:
        """הורדת עדכון"""
        self.logger.info(f"⬇️ Downloading update {update.version}...")
        
        try:
            filename = f"update_{update.version}.zip"
            filepath = os.path.join(self.updates_dir, filename)
            
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(update.download_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Verify checksum
                        actual_checksum = hashlib.sha256(content).hexdigest()
                        if actual_checksum != update.checksum:
                            self.logger.error(f"Checksum mismatch for update {update.version}")
                            return False
                        
                        # Save file
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        self.logger.info(f"✅ Downloaded update {update.version}")
                        return True
                    else:
                        self.logger.error(f"Download failed: HTTP {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error downloading update {update.version}: {e}")
            return False
    
    def create_backup(self) -> bool:
        """יצירת גיבוי לפני עדכון"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{self.current_version}_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup of current installation
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # Backup core files
                for root, dirs, files in os.walk("core"):
                    for file in files:
                        if file.endswith(('.py', '.json', '.txt')):
                            file_path = os.path.join(root, file)
                            backup_zip.write(file_path)
                
                # Backup config files
                for root, dirs, files in os.walk("config"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        backup_zip.write(file_path)
                
                # Backup main files
                for file in ["requirements.txt", "setup.py", "README.md"]:
                    if os.path.exists(file):
                        backup_zip.write(file)
            
            self.logger.info(f"💾 Created backup: {backup_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    async def install_update(self, update: UpdateInfo) -> bool:
        """התקנת עדכון"""
        self.logger.info(f"🔧 Installing update {update.version}...")
        
        try:
            filename = f"update_{update.version}.zip"
            filepath = os.path.join(self.updates_dir, filename)
            
            if not os.path.exists(filepath):
                self.logger.error(f"Update file not found: {filepath}")
                return False
            
            # Create backup before installation
            if not self.create_backup():
                self.logger.error("Failed to create backup, aborting update")
                return False
            
            # Extract and install update
            with zipfile.ZipFile(filepath, 'r') as update_zip:
                update_zip.extractall("temp_update")
            
            # Copy files to their destinations
            temp_dir = "temp_update"
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, temp_dir)
                        dst_path = rel_path
                        
                        # Create directory if needed
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(src_path, dst_path)
                
                # Cleanup temp directory
                shutil.rmtree(temp_dir)
            
            # Update version info
            self.current_version = update.version
            
            # Record update in history
            self.update_history.append({
                "version": update.version,
                "type": update.update_type.value,
                "installed_at": datetime.now().isoformat(),
                "status": "completed"
            })
            
            self.logger.info(f"✅ Successfully installed update {update.version}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error installing update {update.version}: {e}")
            
            # Record failed update
            self.update_history.append({
                "version": update.version,
                "type": update.update_type.value,
                "installed_at": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            
            return False
    
    async def auto_update_process(self):
        """תהליך עדכון אוטומטי"""
        if self.is_updating:
            return
        
        self.is_updating = True
        
        try:
            # Check for updates
            updates = await self.check_for_updates()
            
            for update in updates:
                should_install = False
                
                # Auto-install critical updates
                if update.is_critical:
                    should_install = True
                    self.logger.info(f"🚨 Critical update {update.version} will be auto-installed")
                
                # Auto-install security updates if enabled
                elif update.update_type == UpdateType.SECURITY and self.auto_install_security:
                    should_install = True
                    self.logger.info(f"🔒 Security update {update.version} will be auto-installed")
                
                if should_install:
                    # Download update
                    if await self.download_update(update):
                        # Install update
                        if await self.install_update(update):
                            self.logger.info(f"🎉 Update {update.version} completed successfully")
                            
                            if update.requires_restart:
                                self.logger.warning("⚠️ System restart required for update to take effect")
                        else:
                            self.logger.error(f"❌ Failed to install update {update.version}")
                    else:
                        self.logger.error(f"❌ Failed to download update {update.version}")
        
        finally:
            self.is_updating = False
    
    async def start_auto_updater(self):
        """התחלת מערכת עדכונים אוטומטיים"""
        if not self.auto_update_enabled:
            self.logger.info("Auto-updater is disabled")
            return
        
        self.logger.info(f"🚀 Starting auto-updater (check interval: {self.check_interval_hours}h)")
        
        while True:
            try:
                await self.auto_update_process()
                await asyncio.sleep(self.check_interval_hours * 3600)  # Convert hours to seconds
            
            except Exception as e:
                self.logger.error(f"Error in auto-updater: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    def get_update_status(self) -> Dict[str, Any]:
        """קבלת סטטוס עדכונים"""
        return {
            "current_version": self.current_version,
            "auto_update_enabled": self.auto_update_enabled,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "available_updates": len(self.available_updates),
            "is_updating": self.is_updating,
            "updates": [
                {
                    "version": update.version,
                    "type": update.update_type.value,
                    "title": update.title,
                    "is_critical": update.is_critical,
                    "requires_restart": update.requires_restart,
                    "release_date": update.release_date.isoformat()
                }
                for update in self.available_updates
            ],
            "update_history": self.update_history[-10:]  # Last 10 updates
        }
    
    def cleanup_old_files(self):
        """ניקוי קבצים ישנים"""
        try:
            # Clean old update files (keep last 5)
            update_files = sorted([
                f for f in os.listdir(self.updates_dir) 
                if f.startswith("update_") and f.endswith(".zip")
            ])
            
            if len(update_files) > 5:
                for old_file in update_files[:-5]:
                    os.remove(os.path.join(self.updates_dir, old_file))
                    self.logger.info(f"🗑️ Removed old update file: {old_file}")
            
            # Clean old backups (keep last 10)
            backup_files = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith("backup_") and f.endswith(".zip")
            ])
            
            if len(backup_files) > 10:
                for old_backup in backup_files[:-10]:
                    os.remove(os.path.join(self.backup_dir, old_backup))
                    self.logger.info(f"🗑️ Removed old backup: {old_backup}")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {e}")


# Global auto updater instance
_auto_updater = None

def get_auto_updater(config: Dict[str, Any] = None) -> AutoUpdater:
    """קבלת instance של מערכת העדכונים"""
    global _auto_updater
    if _auto_updater is None:
        _auto_updater = AutoUpdater(config)
    return _auto_updater
