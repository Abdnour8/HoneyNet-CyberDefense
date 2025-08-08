"""
HoneyNet Honeypot System
מערכת הפחים של HoneyNet
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
import random
import string

logger = logging.getLogger(__name__)


class HoneypotSystem:
    """מערכת הפחים החכמה של HoneyNet"""
    
    def __init__(self):
        self.honeypots = {}
        self.active_traps = []
        self.honeypot_data_dir = Path("honeypots_data")
        self.honeypot_data_dir.mkdir(exist_ok=True)
        
        # Initialize honeypot types
        self.honeypot_types = {
            'file': self._create_file_honeypot,
            'network': self._create_network_honeypot,
            'database': self._create_database_honeypot,
            'credential': self._create_credential_honeypot
        }
        
        logger.info("HoneyNet Honeypot System initialized")
    
    def create_honeypot(self, honeypot_type: str, config: Dict) -> str:
        """יצירת פח חדש"""
        try:
            honeypot_id = self._generate_honeypot_id()
            
            if honeypot_type in self.honeypot_types:
                honeypot = self.honeypot_types[honeypot_type](config)
                honeypot['id'] = honeypot_id
                honeypot['type'] = honeypot_type
                honeypot['created_at'] = datetime.now().isoformat()
                honeypot['status'] = 'active'
                
                self.honeypots[honeypot_id] = honeypot
                logger.info(f"Created honeypot {honeypot_id} of type {honeypot_type}")
                return honeypot_id
            else:
                raise ValueError(f"Unknown honeypot type: {honeypot_type}")
                
        except Exception as e:
            logger.error(f"Failed to create honeypot: {e}")
            raise
    
    def _create_file_honeypot(self, config: Dict) -> Dict:
        """יצירת פח קבצים"""
        fake_files = []
        for i in range(config.get('file_count', 5)):
            filename = self._generate_fake_filename()
            filepath = self.honeypot_data_dir / filename
            
            # Create fake file content
            content = self._generate_fake_content(config.get('content_type', 'document'))
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            fake_files.append({
                'filename': filename,
                'path': str(filepath),
                'size': len(content),
                'hash': hashlib.md5(content.encode()).hexdigest()
            })
        
        return {
            'files': fake_files,
            'monitor_path': str(self.honeypot_data_dir),
            'triggers': ['file_access', 'file_modify', 'file_delete']
        }
    
    def _create_network_honeypot(self, config: Dict) -> Dict:
        """יצירת פח רשת"""
        return {
            'ports': config.get('ports', [22, 23, 80, 443]),
            'services': config.get('services', ['ssh', 'telnet', 'http', 'https']),
            'response_type': config.get('response_type', 'banner'),
            'triggers': ['connection_attempt', 'login_attempt', 'data_transfer']
        }
    
    def _create_database_honeypot(self, config: Dict) -> Dict:
        """יצירת פח מסד נתונים"""
        fake_tables = []
        for table_name in config.get('table_names', ['users', 'passwords', 'accounts']):
            fake_tables.append({
                'name': table_name,
                'columns': self._generate_fake_columns(),
                'row_count': random.randint(100, 1000)
            })
        
        return {
            'database_type': config.get('db_type', 'mysql'),
            'tables': fake_tables,
            'triggers': ['query_attempt', 'login_attempt', 'data_extraction']
        }
    
    def _create_credential_honeypot(self, config: Dict) -> Dict:
        """יצירת פח אישורים"""
        fake_credentials = []
        for i in range(config.get('credential_count', 10)):
            fake_credentials.append({
                'username': self._generate_fake_username(),
                'password': self._generate_fake_password(),
                'service': random.choice(['email', 'ftp', 'database', 'admin'])
            })
        
        return {
            'credentials': fake_credentials,
            'storage_type': config.get('storage_type', 'file'),
            'triggers': ['credential_access', 'login_attempt']
        }
    
    def _generate_honeypot_id(self) -> str:
        """יצירת מזהה ייחודי לפח"""
        return f"hp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    def _generate_fake_filename(self) -> str:
        """יצירת שם קובץ מזויף"""
        prefixes = ['passwords', 'backup', 'config', 'secret', 'private', 'admin']
        suffixes = ['txt', 'doc', 'xlsx', 'pdf', 'bak']
        return f"{random.choice(prefixes)}_{random.randint(1, 100)}.{random.choice(suffixes)}"
    
    def _generate_fake_content(self, content_type: str) -> str:
        """יצירת תוכן מזויף"""
        if content_type == 'passwords':
            content = "# Password File\n"
            for i in range(10):
                username = self._generate_fake_username()
                password = self._generate_fake_password()
                content += f"{username}:{password}\n"
            return content
        
        elif content_type == 'document':
            return f"""
Confidential Document
Created: {datetime.now().strftime('%Y-%m-%d')}

This is a fake document created by HoneyNet honeypot system.
Any access to this file will be logged and analyzed.

Project: {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])}
Status: {random.choice(['Active', 'Pending', 'Completed'])}
Priority: {random.choice(['High', 'Medium', 'Low'])}
"""
        
        return "Fake content generated by HoneyNet"
    
    def _generate_fake_username(self) -> str:
        """יצירת שם משתמש מזויף"""
        prefixes = ['admin', 'user', 'test', 'demo', 'guest']
        return f"{random.choice(prefixes)}{random.randint(1, 999)}"
    
    def _generate_fake_password(self) -> str:
        """יצירת סיסמה מזויפת"""
        length = random.randint(8, 12)
        chars = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _generate_fake_columns(self) -> List[Dict]:
        """יצירת עמודות מזויפות למסד נתונים"""
        common_columns = [
            {'name': 'id', 'type': 'int', 'primary_key': True},
            {'name': 'username', 'type': 'varchar(50)'},
            {'name': 'password', 'type': 'varchar(255)'},
            {'name': 'email', 'type': 'varchar(100)'},
            {'name': 'created_at', 'type': 'datetime'},
            {'name': 'last_login', 'type': 'datetime'},
            {'name': 'status', 'type': 'varchar(20)'}
        ]
        return random.sample(common_columns, random.randint(3, len(common_columns)))
    
    def get_honeypot(self, honeypot_id: str) -> Optional[Dict]:
        """קבלת פח לפי מזהה"""
        return self.honeypots.get(honeypot_id)
    
    def list_honeypots(self) -> List[Dict]:
        """רשימת כל הפחים"""
        return list(self.honeypots.values())
    
    def delete_honeypot(self, honeypot_id: str) -> bool:
        """מחיקת פח"""
        if honeypot_id in self.honeypots:
            honeypot = self.honeypots[honeypot_id]
            
            # Clean up files if it's a file honeypot
            if honeypot['type'] == 'file':
                for file_info in honeypot.get('files', []):
                    try:
                        os.remove(file_info['path'])
                    except FileNotFoundError:
                        pass
            
            del self.honeypots[honeypot_id]
            logger.info(f"Deleted honeypot {honeypot_id}")
            return True
        
        return False
    
    def trigger_honeypot(self, honeypot_id: str, trigger_type: str, details: Dict) -> Dict:
        """הפעלת פח (כאשר מישהו נופל בו)"""
        if honeypot_id not in self.honeypots:
            return {'success': False, 'error': 'Honeypot not found'}
        
        honeypot = self.honeypots[honeypot_id]
        
        trigger_event = {
            'honeypot_id': honeypot_id,
            'honeypot_type': honeypot['type'],
            'trigger_type': trigger_type,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'source_ip': details.get('source_ip', 'unknown'),
            'user_agent': details.get('user_agent', 'unknown')
        }
        
        # Log the trigger
        logger.warning(f"Honeypot triggered: {honeypot_id} - {trigger_type}")
        
        # Add to active traps
        self.active_traps.append(trigger_event)
        
        # Keep only last 1000 traps
        if len(self.active_traps) > 1000:
            self.active_traps = self.active_traps[-1000:]
        
        return {
            'success': True,
            'trigger_id': f"trigger_{len(self.active_traps)}",
            'event': trigger_event
        }
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות על הפחים"""
        total_honeypots = len(self.honeypots)
        active_honeypots = len([hp for hp in self.honeypots.values() if hp['status'] == 'active'])
        total_triggers = len(self.active_traps)
        
        # Count by type
        type_counts = {}
        for honeypot in self.honeypots.values():
            hp_type = honeypot['type']
            type_counts[hp_type] = type_counts.get(hp_type, 0) + 1
        
        # Recent triggers (last 24 hours)
        recent_triggers = [
            trap for trap in self.active_traps
            if (datetime.now() - datetime.fromisoformat(trap['timestamp'])).days < 1
        ]
        
        return {
            'total_honeypots': total_honeypots,
            'active_honeypots': active_honeypots,
            'total_triggers': total_triggers,
            'recent_triggers': len(recent_triggers),
            'honeypot_types': type_counts,
            'last_trigger': self.active_traps[-1] if self.active_traps else None
        }
    
    def cleanup(self):
        """ניקוי המערכת"""
        logger.info("Cleaning up honeypot system...")
        
        # Clean up all file honeypots
        for honeypot in self.honeypots.values():
            if honeypot['type'] == 'file':
                for file_info in honeypot.get('files', []):
                    try:
                        os.remove(file_info['path'])
                    except FileNotFoundError:
                        pass
        
        self.honeypots.clear()
        self.active_traps.clear()
        
        logger.info("Honeypot system cleanup completed")
