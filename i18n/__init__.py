"""
HoneyNet Internationalization System
מערכת בינאום של HoneyNet
"""

import json
import os
from typing import Dict, Optional
from functools import lru_cache

class I18nManager:
    """מנהל הבינאום של המערכת"""
    
    def __init__(self):
        self.current_language = 'he'  # Default to Hebrew
        self.translations = {}
        self.supported_languages = [
            'he', 'en', 'ar', 'es', 'fr', 'de', 'ru', 'zh', 'ja', 'ko',
            'pt', 'it', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'tr', 'hi',
            'th', 'vi', 'id', 'ms', 'tl', 'sw', 'am', 'yo', 'ig', 'ha'
        ]
        self.load_translations()
    
    def load_translations(self):
        """טוען את כל התרגומים"""
        base_dir = os.path.dirname(__file__)
        
        for lang in self.supported_languages:
            try:
                lang_file = os.path.join(base_dir, 'languages', f'{lang}.json')
                if os.path.exists(lang_file):
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    # Create default translation file
                    self.create_default_translation(lang)
            except Exception as e:
                print(f"Error loading language {lang}: {e}")
                self.translations[lang] = {}
    
    def create_default_translation(self, lang_code: str):
        """יוצר קובץ תרגום ברירת מחדל"""
        base_translations = {
            'app_name': 'HoneyNet',
            'app_subtitle': 'Global Cyber Defense Platform',
            'dashboard': 'Dashboard',
            'threats': 'Threats',
            'honeypots': 'Honeypots',
            'analytics': 'Analytics',
            'settings': 'Settings',
            'gamification': 'Gamification',
            'blockchain': 'Blockchain',
            'swarm_intelligence': 'Swarm Intelligence',
            'quantum_security': 'Quantum Security',
            'edge_computing': 'Edge Computing',
            'digital_twins': 'Digital Twins',
            'connected': 'Connected',
            'disconnected': 'Disconnected',
            'refresh': 'Refresh',
            'status': 'Status',
            'active': 'Active',
            'inactive': 'Inactive',
            'total_threats': 'Total Threats',
            'active_honeypots': 'Active Honeypots',
            'network_health': 'Network Health',
            'global_stats': 'Global Statistics',
            'threat_detection': 'Threat Detection',
            'real_time_monitoring': 'Real-time Monitoring',
            'advanced_features': 'Advanced Features',
            'server_info': 'Server Information',
            'connection_status': 'Connection Status',
            'last_updated': 'Last Updated',
            'loading': 'Loading...',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            'info': 'Information'
        }
        
        # Language-specific translations
        translations_map = {
            'he': {
                'app_name': 'HoneyNet',
                'app_subtitle': 'פלטפורמת הגנה סייברית גלובלית',
                'dashboard': 'לוח בקרה',
                'threats': 'איומים',
                'honeypots': 'כוורות דבש',
                'analytics': 'אנליטיקה',
                'settings': 'הגדרות',
                'gamification': 'גיימיפיקציה',
                'blockchain': 'בלוקצ\'יין',
                'swarm_intelligence': 'נחיל חכם',
                'quantum_security': 'אבטחה קוונטית',
                'edge_computing': 'מחשוב קצה',
                'digital_twins': 'תאומים דיגיטליים',
                'connected': 'מחובר',
                'disconnected': 'מנותק',
                'refresh': 'רענן',
                'status': 'סטטוס',
                'active': 'פעיל',
                'inactive': 'לא פעיל',
                'total_threats': 'סה"כ איומים',
                'active_honeypots': 'כוורות פעילות',
                'network_health': 'בריאות הרשת',
                'global_stats': 'סטטיסטיקות גלובליות',
                'threat_detection': 'זיהוי איומים',
                'real_time_monitoring': 'ניטור בזמן אמת',
                'advanced_features': 'תכונות מתקדמות',
                'server_info': 'מידע שרת',
                'connection_status': 'סטטוס חיבור',
                'last_updated': 'עודכן לאחרונה',
                'loading': 'טוען...',
                'error': 'שגיאה',
                'success': 'הצלחה',
                'warning': 'אזהרה',
                'info': 'מידע'
            },
            'ar': {
                'app_name': 'HoneyNet',
                'app_subtitle': 'منصة الدفاع السيبراني العالمية',
                'dashboard': 'لوحة القيادة',
                'threats': 'التهديدات',
                'honeypots': 'أواني العسل',
                'analytics': 'التحليلات',
                'settings': 'الإعدادات',
                'gamification': 'التلعيب',
                'blockchain': 'البلوك تشين',
                'swarm_intelligence': 'الذكاء الجماعي',
                'quantum_security': 'الأمان الكمي',
                'edge_computing': 'الحوسبة الطرفية',
                'digital_twins': 'التوائم الرقمية',
                'connected': 'متصل',
                'disconnected': 'غير متصل',
                'refresh': 'تحديث',
                'status': 'الحالة',
                'active': 'نشط',
                'inactive': 'غير نشط'
            },
            'en': base_translations,
            'es': {
                'app_subtitle': 'Plataforma Global de Defensa Cibernética',
                'dashboard': 'Panel de Control',
                'threats': 'Amenazas',
                'honeypots': 'Honeypots',
                'analytics': 'Analíticas',
                'settings': 'Configuración',
                'gamification': 'Gamificación',
                'blockchain': 'Blockchain',
                'swarm_intelligence': 'Inteligencia de Enjambre',
                'quantum_security': 'Seguridad Cuántica',
                'edge_computing': 'Computación en el Borde',
                'digital_twins': 'Gemelos Digitales',
                'connected': 'Conectado',
                'disconnected': 'Desconectado',
                'refresh': 'Actualizar'
            },
            'fr': {
                'app_subtitle': 'Plateforme Globale de Défense Cybernétique',
                'dashboard': 'Tableau de Bord',
                'threats': 'Menaces',
                'honeypots': 'Pots de Miel',
                'analytics': 'Analytiques',
                'settings': 'Paramètres',
                'gamification': 'Gamification',
                'blockchain': 'Blockchain',
                'swarm_intelligence': 'Intelligence d\'Essaim',
                'quantum_security': 'Sécurité Quantique',
                'edge_computing': 'Informatique de Périphérie',
                'digital_twins': 'Jumeaux Numériques',
                'connected': 'Connecté',
                'disconnected': 'Déconnecté',
                'refresh': 'Actualiser'
            }
        }
        
        # Use language-specific translations or fall back to base
        lang_translations = translations_map.get(lang_code, base_translations)
        final_translations = {**base_translations, **lang_translations}
        
        # Create directory if it doesn't exist
        lang_dir = os.path.join(os.path.dirname(__file__), 'languages')
        os.makedirs(lang_dir, exist_ok=True)
        
        # Save translation file
        lang_file = os.path.join(lang_dir, f'{lang_code}.json')
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(final_translations, f, ensure_ascii=False, indent=2)
        
        self.translations[lang_code] = final_translations
    
    def set_language(self, lang_code: str):
        """מגדיר את השפה הנוכחית"""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            return True
        return False
    
    def get_language(self) -> str:
        """מחזיר את השפה הנוכחית"""
        return self.current_language
    
    def translate(self, key: str, lang_code: Optional[str] = None) -> str:
        """מתרגם מפתח לשפה הנוכחית או לשפה שצוינה"""
        target_lang = lang_code or self.current_language
        
        if target_lang not in self.translations:
            target_lang = 'en'  # Fallback to English
        
        return self.translations[target_lang].get(key, key)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """מחזיר רשימת השפות הנתמכות"""
        return {
            'he': 'עברית',
            'en': 'English',
            'ar': 'العربية',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'ru': 'Русский',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'pt': 'Português',
            'it': 'Italiano',
            'nl': 'Nederlands',
            'sv': 'Svenska',
            'no': 'Norsk',
            'da': 'Dansk',
            'fi': 'Suomi',
            'pl': 'Polski',
            'tr': 'Türkçe',
            'hi': 'हिन्दी',
            'th': 'ไทย',
            'vi': 'Tiếng Việt',
            'id': 'Bahasa Indonesia',
            'ms': 'Bahasa Melayu',
            'tl': 'Filipino',
            'sw': 'Kiswahili',
            'am': 'አማርኛ',
            'yo': 'Yorùbá',
            'ig': 'Igbo',
            'ha': 'Hausa'
        }

# Global instance
i18n = I18nManager()

def t(key: str, lang_code: Optional[str] = None) -> str:
    """פונקציה קצרה לתרגום"""
    return i18n.translate(key, lang_code)

def set_language(lang_code: str) -> bool:
    """פונקציה קצרה להגדרת שפה"""
    return i18n.set_language(lang_code)

def get_language() -> str:
    """פונקציה קצרה לקבלת השפה הנוכחית"""
    return i18n.get_language()

def get_supported_languages() -> Dict[str, str]:
    """פונקציה קצרה לקבלת השפות הנתמכות"""
    return i18n.get_supported_languages()
