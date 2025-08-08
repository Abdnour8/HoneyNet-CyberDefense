"""
External Services Integration for HoneyNet
Integrates with third-party services for enhanced functionality
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    """Configuration for external service"""
    name: str
    api_key: str
    base_url: str
    enabled: bool = True
    rate_limit: int = 100  # requests per minute

class ExternalServicesManager:
    """Manages integration with external services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.services = {}
        self.session = None
        self._setup_services()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _setup_services(self):
        """Setup available external services"""
        
        # Error Tracking - Sentry
        if os.getenv('SENTRY_DSN'):
            self.services['sentry'] = ServiceConfig(
                name='Sentry',
                api_key=os.getenv('SENTRY_DSN'),
                base_url='https://sentry.io/api/0/',
                enabled=True
            )
        
        # Analytics - Google Analytics
        if os.getenv('GOOGLE_ANALYTICS_ID'):
            self.services['google_analytics'] = ServiceConfig(
                name='Google Analytics',
                api_key=os.getenv('GOOGLE_ANALYTICS_ID'),
                base_url='https://www.google-analytics.com/mp/collect',
                enabled=True
            )
        
        # Analytics - Mixpanel
        if os.getenv('MIXPANEL_TOKEN'):
            self.services['mixpanel'] = ServiceConfig(
                name='Mixpanel',
                api_key=os.getenv('MIXPANEL_TOKEN'),
                base_url='https://api.mixpanel.com/',
                enabled=True
            )
        
        # Notifications - Slack
        if os.getenv('SLACK_WEBHOOK_URL'):
            self.services['slack'] = ServiceConfig(
                name='Slack',
                api_key=os.getenv('SLACK_WEBHOOK_URL'),
                base_url=os.getenv('SLACK_WEBHOOK_URL'),
                enabled=True
            )
        
        # Email - SendGrid
        if os.getenv('SENDGRID_API_KEY'):
            self.services['sendgrid'] = ServiceConfig(
                name='SendGrid',
                api_key=os.getenv('SENDGRID_API_KEY'),
                base_url='https://api.sendgrid.com/v3/',
                enabled=True
            )
        
        # Geolocation - IPGeolocation
        if os.getenv('IPGEOLOCATION_API_KEY'):
            self.services['ipgeolocation'] = ServiceConfig(
                name='IPGeolocation',
                api_key=os.getenv('IPGEOLOCATION_API_KEY'),
                base_url='https://api.ipgeolocation.io/',
                enabled=True
            )
        
        # Threat Intelligence - VirusTotal
        if os.getenv('VIRUSTOTAL_API_KEY'):
            self.services['virustotal'] = ServiceConfig(
                name='VirusTotal',
                api_key=os.getenv('VIRUSTOTAL_API_KEY'),
                base_url='https://www.virustotal.com/vtapi/v2/',
                enabled=True
            )

class AnalyticsService:
    """Analytics service for tracking usage and events"""
    
    def __init__(self, services_manager: ExternalServicesManager):
        self.services = services_manager
        self.logger = logging.getLogger(__name__)
    
    async def track_event(self, event_name: str, properties: Dict[str, Any], user_id: str = None):
        """Track an event across all analytics services"""
        
        # Google Analytics 4
        if 'google_analytics' in self.services.services:
            await self._track_ga4_event(event_name, properties, user_id)
        
        # Mixpanel
        if 'mixpanel' in self.services.services:
            await self._track_mixpanel_event(event_name, properties, user_id)
    
    async def _track_ga4_event(self, event_name: str, properties: Dict[str, Any], user_id: str):
        """Track event in Google Analytics 4"""
        try:
            config = self.services.services['google_analytics']
            
            payload = {
                'client_id': user_id or 'anonymous',
                'events': [{
                    'name': event_name,
                    'params': properties
                }]
            }
            
            url = f"{config.base_url}?measurement_id={config.api_key}&api_secret={os.getenv('GA_API_SECRET')}"
            
            async with self.services.session.post(url, json=payload) as response:
                if response.status == 204:
                    self.logger.debug(f"GA4 event tracked: {event_name}")
                else:
                    self.logger.warning(f"GA4 tracking failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"GA4 tracking error: {e}")
    
    async def _track_mixpanel_event(self, event_name: str, properties: Dict[str, Any], user_id: str):
        """Track event in Mixpanel"""
        try:
            config = self.services.services['mixpanel']
            
            event_data = {
                'event': event_name,
                'properties': {
                    **properties,
                    'token': config.api_key,
                    'distinct_id': user_id or 'anonymous',
                    'time': int(datetime.now().timestamp())
                }
            }
            
            url = f"{config.base_url}track"
            
            async with self.services.session.post(url, json=[event_data]) as response:
                if response.status == 200:
                    self.logger.debug(f"Mixpanel event tracked: {event_name}")
                else:
                    self.logger.warning(f"Mixpanel tracking failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Mixpanel tracking error: {e}")

class NotificationService:
    """Notification service for alerts and messages"""
    
    def __init__(self, services_manager: ExternalServicesManager):
        self.services = services_manager
        self.logger = logging.getLogger(__name__)
    
    async def send_alert(self, title: str, message: str, severity: str = 'info'):
        """Send alert through all configured notification channels"""
        
        # Slack
        if 'slack' in self.services.services:
            await self._send_slack_message(title, message, severity)
        
        # Email via SendGrid
        if 'sendgrid' in self.services.services:
            await self._send_email_alert(title, message, severity)
    
    async def _send_slack_message(self, title: str, message: str, severity: str):
        """Send message to Slack"""
        try:
            config = self.services.services['slack']
            
            color_map = {
                'info': '#36a64f',
                'warning': '#ff9500',
                'error': '#ff0000',
                'critical': '#8b0000'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map.get(severity, '#36a64f'),
                    'title': f"🛡️ HoneyNet Alert: {title}",
                    'text': message,
                    'footer': 'HoneyNet Security System',
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            async with self.services.session.post(config.base_url, json=payload) as response:
                if response.status == 200:
                    self.logger.debug(f"Slack alert sent: {title}")
                else:
                    self.logger.warning(f"Slack alert failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Slack notification error: {e}")
    
    async def _send_email_alert(self, title: str, message: str, severity: str):
        """Send email alert via SendGrid"""
        try:
            config = self.services.services['sendgrid']
            
            payload = {
                'personalizations': [{
                    'to': [{'email': os.getenv('ADMIN_EMAIL', 'admin@honeynet.com')}],
                    'subject': f"🛡️ HoneyNet Alert: {title}"
                }],
                'from': {'email': 'alerts@honeynet.com', 'name': 'HoneyNet Security'},
                'content': [{
                    'type': 'text/html',
                    'value': f"""
                    <h2>HoneyNet Security Alert</h2>
                    <p><strong>Severity:</strong> {severity.upper()}</p>
                    <p><strong>Title:</strong> {title}</p>
                    <p><strong>Message:</strong></p>
                    <p>{message}</p>
                    <hr>
                    <p><small>Sent by HoneyNet Security System at {datetime.now().isoformat()}</small></p>
                    """
                }]
            }
            
            headers = {'Authorization': f'Bearer {config.api_key}'}
            url = f"{config.base_url}mail/send"
            
            async with self.services.session.post(url, json=payload, headers=headers) as response:
                if response.status == 202:
                    self.logger.debug(f"Email alert sent: {title}")
                else:
                    self.logger.warning(f"Email alert failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Email notification error: {e}")

class ThreatIntelligenceService:
    """Threat intelligence from external sources"""
    
    def __init__(self, services_manager: ExternalServicesManager):
        self.services = services_manager
        self.logger = logging.getLogger(__name__)
    
    async def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Check IP reputation across threat intelligence sources"""
        results = {}
        
        # VirusTotal
        if 'virustotal' in self.services.services:
            vt_result = await self._check_virustotal_ip(ip_address)
            results['virustotal'] = vt_result
        
        # IP Geolocation
        if 'ipgeolocation' in self.services.services:
            geo_result = await self._get_ip_geolocation(ip_address)
            results['geolocation'] = geo_result
        
        return results
    
    async def _check_virustotal_ip(self, ip_address: str) -> Dict[str, Any]:
        """Check IP in VirusTotal"""
        try:
            config = self.services.services['virustotal']
            
            url = f"{config.base_url}ip-address/report"
            params = {
                'apikey': config.api_key,
                'ip': ip_address
            }
            
            async with self.services.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'malicious': data.get('detected_urls', []),
                        'reputation': data.get('verbose_msg', 'Unknown')
                    }
                else:
                    return {'error': f'VirusTotal API error: {response.status}'}
                    
        except Exception as e:
            self.logger.error(f"VirusTotal IP check error: {e}")
            return {'error': str(e)}
    
    async def _get_ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """Get IP geolocation information"""
        try:
            config = self.services.services['ipgeolocation']
            
            url = f"{config.base_url}ipgeo"
            params = {
                'apiKey': config.api_key,
                'ip': ip_address
            }
            
            async with self.services.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'country': data.get('country_name'),
                        'city': data.get('city'),
                        'isp': data.get('isp'),
                        'threat_types': data.get('threat_types', [])
                    }
                else:
                    return {'error': f'IPGeolocation API error: {response.status}'}
                    
        except Exception as e:
            self.logger.error(f"IP Geolocation error: {e}")
            return {'error': str(e)}

# Usage example and integration
async def initialize_external_services():
    """Initialize external services"""
    async with ExternalServicesManager() as services:
        analytics = AnalyticsService(services)
        notifications = NotificationService(services)
        threat_intel = ThreatIntelligenceService(services)
        
        return {
            'analytics': analytics,
            'notifications': notifications,
            'threat_intelligence': threat_intel
        }
