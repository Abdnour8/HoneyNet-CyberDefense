"""
HoneyNet Threat Analyzer
מנתח איומים מבוסס AI של HoneyNet
"""

import asyncio
import logging
import hashlib
import json
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, Counter

from config.settings import get_settings
from config.security import MALICIOUS_PATTERNS
from core.defense_engine import ThreatEvent, AttackType, ThreatLevel


class AnalysisResult(Enum):
    """תוצאות ניתוח"""
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    CRITICAL = "critical"


@dataclass
class AttackDNA:
    """DNA של התקפה - החתימה הגנטית"""
    signature: str
    attack_type: AttackType
    patterns: List[str]
    behavioral_markers: Dict[str, float]
    source_fingerprint: str
    confidence_score: float
    first_seen: datetime
    last_seen: datetime
    variant_count: int = 1
    evolution_history: List[str] = field(default_factory=list)


@dataclass
class ThreatIntelligence:
    """מודיעין איומים"""
    threat_id: str
    attack_family: str
    known_variants: List[str]
    iocs: List[str]  # Indicators of Compromise
    ttps: List[str]  # Tactics, Techniques, and Procedures
    attribution: Optional[str]
    severity: ThreatLevel
    mitigation_strategies: List[str]


class ThreatAnalyzer:
    """מנתח איומים מתקדם עם AI"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Attack DNA database
        self.attack_dna_db: Dict[str, AttackDNA] = {}
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        
        # ML Models (simplified for demo)
        self.behavioral_model = None
        self.pattern_recognition_model = None
        
        # Analysis statistics
        self.stats = {
            "total_analyzed": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "accuracy_rate": 0.0,
            "unique_attack_families": 0
        }
        
        # Known attack patterns
        self.malicious_patterns = MALICIOUS_PATTERNS
        self.behavioral_thresholds = {
            "file_access_rate": 10.0,  # files per minute
            "network_connections": 50,
            "process_spawning": 5,
            "registry_modifications": 20
        }
        
        self.logger.info("🧠 Threat Analyzer initialized")
    
    async def analyze_threat(self, event_data: Dict) -> Tuple[AnalysisResult, float, Dict]:
        """ניתוח איום מקיף"""
        self.logger.info(f"🔍 Analyzing potential threat: {event_data.get('source', 'unknown')}")
        
        analysis_results = {}
        confidence_scores = []
        
        # 1. Pattern-based analysis
        pattern_result, pattern_confidence = await self._analyze_patterns(event_data)
        analysis_results["pattern_analysis"] = pattern_result
        confidence_scores.append(pattern_confidence)
        
        # 2. Behavioral analysis
        behavior_result, behavior_confidence = await self._analyze_behavior(event_data)
        analysis_results["behavioral_analysis"] = behavior_result
        confidence_scores.append(behavior_confidence)
        
        # 3. DNA matching
        dna_result, dna_confidence = await self._match_attack_dna(event_data)
        analysis_results["dna_matching"] = dna_result
        confidence_scores.append(dna_confidence)
        
        # 4. Threat intelligence correlation
        intel_result, intel_confidence = await self._correlate_threat_intelligence(event_data)
        analysis_results["intelligence_correlation"] = intel_result
        confidence_scores.append(intel_confidence)
        
        # 5. ML-based analysis (simplified)
        ml_result, ml_confidence = await self._ml_analysis(event_data)
        analysis_results["ml_analysis"] = ml_result
        confidence_scores.append(ml_confidence)
        
        # Calculate final result
        final_confidence = np.mean(confidence_scores)
        final_result = self._determine_final_result(analysis_results, final_confidence)
        
        # Update statistics
        self.stats["total_analyzed"] += 1
        if final_result in [AnalysisResult.MALICIOUS, AnalysisResult.CRITICAL]:
            self.stats["threats_detected"] += 1
        
        # Generate or update attack DNA if malicious
        if final_result in [AnalysisResult.MALICIOUS, AnalysisResult.CRITICAL]:
            await self._generate_or_update_attack_dna(event_data, analysis_results)
        
        self.logger.info(
            f"✅ Analysis complete: {final_result.value} "
            f"(confidence: {final_confidence:.2f})"
        )
        
        return final_result, final_confidence, analysis_results
    
    async def _analyze_patterns(self, event_data: Dict) -> Tuple[AnalysisResult, float]:
        """ניתוח דפוסים זדוניים"""
        malicious_score = 0
        total_patterns = len(self.malicious_patterns)
        
        # Check event data against known malicious patterns
        event_text = json.dumps(event_data).lower()
        
        for pattern in self.malicious_patterns:
            if re.search(pattern, event_text):
                malicious_score += 1
                self.logger.debug(f"🚨 Malicious pattern detected: {pattern}")
        
        confidence = malicious_score / total_patterns if total_patterns > 0 else 0
        
        if confidence > 0.7:
            return AnalysisResult.CRITICAL, confidence
        elif confidence > 0.4:
            return AnalysisResult.MALICIOUS, confidence
        elif confidence > 0.2:
            return AnalysisResult.SUSPICIOUS, confidence
        else:
            return AnalysisResult.BENIGN, confidence
    
    async def _analyze_behavior(self, event_data: Dict) -> Tuple[AnalysisResult, float]:
        """ניתוח התנהגותי"""
        suspicious_behaviors = 0
        total_behaviors = len(self.behavioral_thresholds)
        
        # Check behavioral indicators
        for behavior, threshold in self.behavioral_thresholds.items():
            if behavior in event_data:
                value = event_data[behavior]
                if isinstance(value, (int, float)) and value > threshold:
                    suspicious_behaviors += 1
                    self.logger.debug(f"🚨 Suspicious behavior: {behavior} = {value}")
        
        confidence = suspicious_behaviors / total_behaviors if total_behaviors > 0 else 0
        
        # Additional behavioral checks
        if "rapid_file_access" in event_data and event_data["rapid_file_access"]:
            confidence += 0.3
        
        if "unusual_network_activity" in event_data and event_data["unusual_network_activity"]:
            confidence += 0.2
        
        if "privilege_escalation" in event_data and event_data["privilege_escalation"]:
            confidence += 0.4
        
        confidence = min(confidence, 1.0)  # Cap at 1.0
        
        if confidence > 0.8:
            return AnalysisResult.CRITICAL, confidence
        elif confidence > 0.6:
            return AnalysisResult.MALICIOUS, confidence
        elif confidence > 0.3:
            return AnalysisResult.SUSPICIOUS, confidence
        else:
            return AnalysisResult.BENIGN, confidence
    
    async def _match_attack_dna(self, event_data: Dict) -> Tuple[AnalysisResult, float]:
        """התאמת DNA של התקפה"""
        if not self.attack_dna_db:
            return AnalysisResult.BENIGN, 0.0
        
        # Generate signature for current event
        event_signature = self._generate_event_signature(event_data)
        
        best_match_confidence = 0.0
        best_match_result = AnalysisResult.BENIGN
        
        # Compare against known attack DNA
        for dna_signature, attack_dna in self.attack_dna_db.items():
            similarity = self._calculate_signature_similarity(event_signature, dna_signature)
            
            if similarity > best_match_confidence:
                best_match_confidence = similarity
                
                if similarity > 0.9:
                    best_match_result = AnalysisResult.CRITICAL
                elif similarity > 0.7:
                    best_match_result = AnalysisResult.MALICIOUS
                elif similarity > 0.5:
                    best_match_result = AnalysisResult.SUSPICIOUS
        
        if best_match_confidence > 0.5:
            self.logger.info(f"🧬 DNA match found: {best_match_confidence:.2f} similarity")
        
        return best_match_result, best_match_confidence
    
    async def _correlate_threat_intelligence(self, event_data: Dict) -> Tuple[AnalysisResult, float]:
        """מתאם מודיעין איומים"""
        if not self.threat_intelligence:
            return AnalysisResult.BENIGN, 0.0
        
        # Extract IOCs from event
        event_iocs = self._extract_iocs(event_data)
        
        max_confidence = 0.0
        result = AnalysisResult.BENIGN
        
        for threat_id, intel in self.threat_intelligence.items():
            # Check IOC overlap
            ioc_overlap = len(set(event_iocs) & set(intel.iocs))
            if ioc_overlap > 0:
                confidence = min(ioc_overlap / len(intel.iocs), 1.0)
                
                if confidence > max_confidence:
                    max_confidence = confidence
                    
                    if intel.severity == ThreatLevel.CRITICAL:
                        result = AnalysisResult.CRITICAL
                    elif intel.severity == ThreatLevel.HIGH:
                        result = AnalysisResult.MALICIOUS
                    elif intel.severity == ThreatLevel.MEDIUM:
                        result = AnalysisResult.SUSPICIOUS
        
        return result, max_confidence
    
    async def _ml_analysis(self, event_data: Dict) -> Tuple[AnalysisResult, float]:
        """ניתוח מבוסס למידת מכונה (מפושט לדמו)"""
        # Simplified ML analysis - in production this would use trained models
        
        # Feature extraction
        features = self._extract_features(event_data)
        
        # Simple scoring based on feature weights
        risk_score = 0.0
        
        if features.get("has_suspicious_files", False):
            risk_score += 0.3
        
        if features.get("network_anomaly", False):
            risk_score += 0.2
        
        if features.get("process_injection", False):
            risk_score += 0.4
        
        if features.get("registry_tampering", False):
            risk_score += 0.3
        
        if features.get("encryption_activity", False):
            risk_score += 0.5
        
        # Normalize score
        confidence = min(risk_score, 1.0)
        
        if confidence > 0.8:
            return AnalysisResult.CRITICAL, confidence
        elif confidence > 0.6:
            return AnalysisResult.MALICIOUS, confidence
        elif confidence > 0.3:
            return AnalysisResult.SUSPICIOUS, confidence
        else:
            return AnalysisResult.BENIGN, confidence
    
    def _determine_final_result(
        self, 
        analysis_results: Dict, 
        confidence: float
    ) -> AnalysisResult:
        """קביעת תוצאה סופית"""
        # Count votes from different analysis methods
        votes = Counter()
        
        for method, result in analysis_results.items():
            if isinstance(result, AnalysisResult):
                votes[result] += 1
        
        # Get majority vote
        if votes:
            majority_result = votes.most_common(1)[0][0]
            
            # Adjust based on confidence
            if confidence > 0.9 and majority_result != AnalysisResult.BENIGN:
                return AnalysisResult.CRITICAL
            elif confidence > 0.7:
                return majority_result
            elif confidence > 0.5 and majority_result in [AnalysisResult.MALICIOUS, AnalysisResult.CRITICAL]:
                return AnalysisResult.SUSPICIOUS
            else:
                return majority_result
        
        return AnalysisResult.BENIGN
    
    async def _generate_or_update_attack_dna(self, event_data: Dict, analysis_results: Dict):
        """יצירה או עדכון DNA של התקפה"""
        signature = self._generate_event_signature(event_data)
        
        if signature in self.attack_dna_db:
            # Update existing DNA
            dna = self.attack_dna_db[signature]
            dna.last_seen = datetime.now()
            dna.variant_count += 1
            dna.evolution_history.append(json.dumps(event_data, sort_keys=True))
            
            self.logger.info(f"🧬 Updated attack DNA: {signature}")
        else:
            # Create new DNA
            attack_type = self._determine_attack_type(event_data)
            patterns = self._extract_patterns(event_data)
            behavioral_markers = self._extract_behavioral_markers(event_data)
            
            dna = AttackDNA(
                signature=signature,
                attack_type=attack_type,
                patterns=patterns,
                behavioral_markers=behavioral_markers,
                source_fingerprint=self._generate_source_fingerprint(event_data),
                confidence_score=0.8,  # Initial confidence
                first_seen=datetime.now(),
                last_seen=datetime.now()
            )
            
            self.attack_dna_db[signature] = dna
            self.stats["unique_attack_families"] += 1
            
            self.logger.info(f"🧬 Created new attack DNA: {signature}")
    
    def _generate_event_signature(self, event_data: Dict) -> str:
        """יצירת חתימה לאירוע"""
        # Create a normalized representation of the event
        normalized_data = {
            "attack_patterns": sorted(event_data.get("patterns", [])),
            "behavioral_indicators": sorted(event_data.get("behaviors", [])),
            "file_operations": sorted(event_data.get("file_ops", [])),
            "network_activity": event_data.get("network", {})
        }
        
        signature_string = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()[:16]
    
    def _calculate_signature_similarity(self, sig1: str, sig2: str) -> float:
        """חישוב דמיון בין חתימות"""
        # Simple similarity based on common characters (in production use more sophisticated methods)
        common_chars = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return common_chars / max(len(sig1), len(sig2))
    
    def _extract_iocs(self, event_data: Dict) -> List[str]:
        """חילוץ אינדיקטורים של פשרה"""
        iocs = []
        
        # Extract IP addresses
        if "source_ip" in event_data:
            iocs.append(event_data["source_ip"])
        
        # Extract file hashes
        if "file_hash" in event_data:
            iocs.append(event_data["file_hash"])
        
        # Extract domains
        if "domains" in event_data:
            iocs.extend(event_data["domains"])
        
        return iocs
    
    def _extract_features(self, event_data: Dict) -> Dict[str, bool]:
        """חילוץ תכונות לניתוח ML"""
        return {
            "has_suspicious_files": "suspicious_files" in event_data,
            "network_anomaly": event_data.get("network_anomaly", False),
            "process_injection": event_data.get("process_injection", False),
            "registry_tampering": event_data.get("registry_changes", False),
            "encryption_activity": event_data.get("encryption_detected", False)
        }
    
    def _determine_attack_type(self, event_data: Dict) -> AttackType:
        """קביעת סוג התקפה"""
        if "ransomware" in str(event_data).lower():
            return AttackType.RANSOMWARE
        elif "phishing" in str(event_data).lower():
            return AttackType.PHISHING
        elif "malware" in str(event_data).lower():
            return AttackType.MALWARE
        elif "sql" in str(event_data).lower():
            return AttackType.SQL_INJECTION
        elif "script" in str(event_data).lower():
            return AttackType.XSS
        else:
            return AttackType.UNKNOWN
    
    def _extract_patterns(self, event_data: Dict) -> List[str]:
        """חילוץ דפוסים מהאירוע"""
        patterns = []
        event_str = json.dumps(event_data).lower()
        
        for pattern in self.malicious_patterns:
            if re.search(pattern, event_str):
                patterns.append(pattern)
        
        return patterns
    
    def _extract_behavioral_markers(self, event_data: Dict) -> Dict[str, float]:
        """חילוץ סמנים התנהגותיים"""
        markers = {}
        
        for behavior, threshold in self.behavioral_thresholds.items():
            if behavior in event_data:
                value = event_data[behavior]
                if isinstance(value, (int, float)):
                    markers[behavior] = value / threshold  # Normalized score
        
        return markers
    
    def _generate_source_fingerprint(self, event_data: Dict) -> str:
        """יצירת טביעת אצבע למקור"""
        source_data = {
            "ip": event_data.get("source_ip", ""),
            "user_agent": event_data.get("user_agent", ""),
            "system_info": event_data.get("system_info", {})
        }
        
        fingerprint_string = json.dumps(source_data, sort_keys=True)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()[:12]
    
    async def predict_future_attacks(self, time_horizon_hours: int = 24) -> List[Dict]:
        """חיזוי התקפות עתידיות"""
        predictions = []
        
        # Analyze attack patterns and trends
        for signature, dna in self.attack_dna_db.items():
            if dna.variant_count > 1:  # Evolving attacks
                # Simple prediction based on evolution rate
                evolution_rate = dna.variant_count / max(
                    (dna.last_seen - dna.first_seen).days, 1
                )
                
                if evolution_rate > 0.5:  # High evolution rate
                    prediction = {
                        "attack_family": dna.attack_type.value,
                        "predicted_time": datetime.now() + timedelta(
                            hours=time_horizon_hours * (1 - evolution_rate)
                        ),
                        "confidence": min(evolution_rate, 0.9),
                        "predicted_targets": ["high_value_assets"],
                        "mitigation_priority": "high" if evolution_rate > 0.8 else "medium"
                    }
                    predictions.append(prediction)
        
        return sorted(predictions, key=lambda x: x["confidence"], reverse=True)
    
    def get_attack_intelligence_report(self) -> Dict:
        """קבלת דוח מודיעין התקפות"""
        return {
            "total_attack_families": len(self.attack_dna_db),
            "most_active_attacks": [
                {
                    "signature": sig,
                    "attack_type": dna.attack_type.value,
                    "variant_count": dna.variant_count,
                    "last_seen": dna.last_seen.isoformat()
                }
                for sig, dna in sorted(
                    self.attack_dna_db.items(),
                    key=lambda x: x[1].variant_count,
                    reverse=True
                )[:10]
            ],
            "threat_trends": self._analyze_threat_trends(),
            "statistics": self.stats
        }
    
    def _analyze_threat_trends(self) -> Dict:
        """ניתוח מגמות איומים"""
        # Simple trend analysis
        attack_types = Counter()
        recent_attacks = 0
        
        for dna in self.attack_dna_db.values():
            attack_types[dna.attack_type.value] += dna.variant_count
            
            if (datetime.now() - dna.last_seen).days <= 7:
                recent_attacks += 1
        
        return {
            "dominant_attack_types": dict(attack_types.most_common(5)),
            "recent_activity": recent_attacks,
            "trend_direction": "increasing" if recent_attacks > len(self.attack_dna_db) * 0.3 else "stable"
        }
