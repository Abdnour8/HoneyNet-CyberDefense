"""
HoneyNet Global Server - AI Coordinator
מתאם AI לשרת HoneyNet הגלובלי
"""

import asyncio
import logging
import json
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import pickle
import os


@dataclass
class ThreatPattern:
    """דפוס איום מזוהה"""
    pattern_id: str
    attack_type: str
    signatures: List[str]
    behavioral_markers: Dict[str, float]
    confidence: float
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int = 1
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    evolution_history: List[Dict] = field(default_factory=list)


@dataclass
class GlobalThreatIntelligence:
    """מודיעין איומים גלובלי"""
    threat_id: str
    threat_family: str
    severity_level: str
    active_campaigns: List[str]
    affected_regions: List[str]
    attack_vectors: List[str]
    indicators_of_compromise: List[str]
    mitigation_strategies: List[str]
    prediction_confidence: float
    next_wave_prediction: Optional[datetime] = None


class AICoordinator:
    """מתאם AI מרכזי לרשת HoneyNet הגלובלית"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # AI Models
        self.threat_classifier = None
        self.anomaly_detector = None
        self.pattern_clustering = None
        self.prediction_model = None
        
        # Knowledge bases
        self.threat_patterns: Dict[str, ThreatPattern] = {}
        self.global_intelligence: Dict[str, GlobalThreatIntelligence] = {}
        
        # Statistics
        self.total_threats_analyzed = 0
        self.patterns_discovered = 0
        self.predictions_made = 0
        self.accuracy_score = 0.0
        
        # Configuration
        self.model_update_interval = 3600  # 1 hour
        self.pattern_similarity_threshold = 0.85
        self.anomaly_threshold = 0.7
        
        self.logger.info("🧠 AI Coordinator initialized")
    
    async def initialize(self):
        """אתחול מערכת AI"""
        try:
            self.logger.info("🚀 Initializing AI systems...")
            
            # Load or create models
            await self._load_or_create_models()
            
            # Load existing patterns
            await self._load_threat_patterns()
            
            # Load global intelligence
            await self._load_global_intelligence()
            
            # Start background tasks
            asyncio.create_task(self._periodic_model_update())
            asyncio.create_task(self._pattern_evolution_analysis())
            asyncio.create_task(self._global_threat_prediction())
            
            self.logger.info("✅ AI Coordinator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize AI Coordinator: {e}")
            raise
    
    async def analyze_global_threat(self, threat_data: Dict, source_client: str) -> Dict:
        """ניתוח איום ברמה גלובלית"""
        self.logger.info(f"🔍 Analyzing global threat from {source_client}")
        
        try:
            # Extract features from threat data
            features = await self._extract_threat_features(threat_data)
            
            # Classify threat using ML
            classification = await self._classify_threat(features)
            
            # Detect anomalies
            anomaly_score = await self._detect_anomaly(features)
            
            # Match against known patterns
            pattern_matches = await self._match_threat_patterns(features)
            
            # Generate threat DNA
            threat_dna = await self._generate_threat_dna(threat_data, features)
            
            # Update global intelligence
            await self._update_global_intelligence(threat_dna, classification)
            
            # Create analysis result
            analysis_result = {
                "threat_id": threat_dna["id"],
                "classification": classification,
                "anomaly_score": anomaly_score,
                "pattern_matches": pattern_matches,
                "threat_dna": threat_dna,
                "severity": await self._calculate_threat_severity(classification, anomaly_score, pattern_matches),
                "global_impact_prediction": await self._predict_global_impact(threat_dna),
                "recommended_actions": await self._generate_recommendations(classification, anomaly_score),
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence": await self._calculate_analysis_confidence(classification, anomaly_score, pattern_matches)
            }
            
            self.total_threats_analyzed += 1
            
            self.logger.info(
                f"✅ Threat analysis complete: {analysis_result['severity']} "
                f"(confidence: {analysis_result['confidence']:.2f})"
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing threat: {e}")
            return {
                "error": "Analysis failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_honeypot_trigger(self, honeypot_data: Dict) -> Dict:
        """ניתוח הפעלת פיתיון"""
        self.logger.info(f"🍯 Analyzing honeypot trigger: {honeypot_data.get('honeypot_type', 'unknown')}")
        
        try:
            # Extract honeypot features
            features = await self._extract_honeypot_features(honeypot_data)
            
            # Analyze attack behavior
            behavior_analysis = await self._analyze_attack_behavior(features)
            
            # Generate attacker fingerprint
            attacker_fingerprint = await self._generate_attacker_fingerprint(honeypot_data)
            
            # Check against known attackers
            known_attacker = await self._match_known_attacker(attacker_fingerprint)
            
            # Calculate honeypot effectiveness
            effectiveness_score = await self._calculate_honeypot_effectiveness(honeypot_data)
            
            # Generate new honeypot recommendations
            honeypot_recommendations = await self._generate_honeypot_recommendations(behavior_analysis)
            
            analysis_result = {
                "trigger_id": f"trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(honeypot_data)) % 10000}",
                "honeypot_type": honeypot_data.get("honeypot_type", "unknown"),
                "behavior_analysis": behavior_analysis,
                "attacker_fingerprint": attacker_fingerprint,
                "known_attacker": known_attacker,
                "effectiveness_score": effectiveness_score,
                "honeypot_recommendations": honeypot_recommendations,
                "should_update_network": effectiveness_score > 0.7 or known_attacker is not None,
                "points": int(effectiveness_score * 100),
                "global_learning": await self._extract_global_learning(behavior_analysis),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # Update honeypot intelligence
            await self._update_honeypot_intelligence(analysis_result)
            
            self.logger.info(
                f"✅ Honeypot analysis complete: effectiveness {effectiveness_score:.2f}"
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing honeypot trigger: {e}")
            return {
                "error": "Honeypot analysis failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def predict_future_threats(self, time_horizon_hours: int = 24) -> List[Dict]:
        """חיזוי איומים עתידיים"""
        self.logger.info(f"🔮 Predicting threats for next {time_horizon_hours} hours")
        
        try:
            predictions = []
            
            # Analyze current threat patterns
            current_patterns = await self._analyze_current_threat_patterns()
            
            # Use ML model for predictions
            if self.prediction_model:
                for pattern in current_patterns:
                    prediction = await self._predict_pattern_evolution(pattern, time_horizon_hours)
                    if prediction["confidence"] > 0.6:
                        predictions.append(prediction)
            
            # Sort by confidence and impact
            predictions.sort(key=lambda x: x["confidence"] * x["impact_score"], reverse=True)
            
            self.predictions_made += len(predictions)
            
            self.logger.info(f"🔮 Generated {len(predictions)} threat predictions")
            
            return predictions[:10]  # Return top 10 predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting future threats: {e}")
            return []
    
    async def generate_global_defense_strategy(self) -> Dict:
        """יצירת אסטרטגיית הגנה גלובלית"""
        self.logger.info("🛡️ Generating global defense strategy")
        
        try:
            # Analyze current threat landscape
            threat_landscape = await self._analyze_threat_landscape()
            
            # Identify vulnerabilities
            vulnerabilities = await self._identify_global_vulnerabilities()
            
            # Generate defense recommendations
            defense_recommendations = await self._generate_defense_recommendations(
                threat_landscape, vulnerabilities
            )
            
            # Calculate resource allocation
            resource_allocation = await self._calculate_optimal_resource_allocation()
            
            strategy = {
                "strategy_id": f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "threat_landscape": threat_landscape,
                "identified_vulnerabilities": vulnerabilities,
                "defense_recommendations": defense_recommendations,
                "resource_allocation": resource_allocation,
                "priority_actions": await self._prioritize_defense_actions(defense_recommendations),
                "effectiveness_prediction": await self._predict_strategy_effectiveness(defense_recommendations),
                "generated_at": datetime.now().isoformat(),
                "valid_until": (datetime.now() + timedelta(hours=12)).isoformat()
            }
            
            self.logger.info("✅ Global defense strategy generated")
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error generating defense strategy: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """בדיקת בריאות מערכת AI"""
        try:
            # Check model availability
            models_healthy = all([
                self.threat_classifier is not None,
                self.anomaly_detector is not None,
                self.pattern_clustering is not None
            ])
            
            # Check data integrity
            data_healthy = len(self.threat_patterns) > 0
            
            # Check recent activity
            activity_healthy = self.total_threats_analyzed > 0
            
            return models_healthy and data_healthy and activity_healthy
            
        except Exception as e:
            self.logger.error(f"AI health check failed: {e}")
            return False
    
    async def cleanup(self):
        """ניקוי משאבי AI"""
        self.logger.info("🧹 Cleaning up AI Coordinator...")
        
        try:
            # Save models and data
            await self._save_threat_patterns()
            await self._save_global_intelligence()
            await self._save_models()
            
            self.logger.info("✅ AI Coordinator cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Error during AI cleanup: {e}")
    
    # Private methods
    
    async def _load_or_create_models(self):
        """טעינה או יצירת מודלי ML"""
        models_dir = "models/ai_coordinator"
        os.makedirs(models_dir, exist_ok=True)
        
        try:
            # Load existing models
            if os.path.exists(f"{models_dir}/threat_classifier.pkl"):
                with open(f"{models_dir}/threat_classifier.pkl", "rb") as f:
                    self.threat_classifier = pickle.load(f)
                self.logger.info("✅ Loaded existing threat classifier")
            else:
                # Create new classifier (simplified for demo)
                self.threat_classifier = self._create_threat_classifier()
                self.logger.info("🆕 Created new threat classifier")
            
            # Load or create anomaly detector
            if os.path.exists(f"{models_dir}/anomaly_detector.pkl"):
                with open(f"{models_dir}/anomaly_detector.pkl", "rb") as f:
                    self.anomaly_detector = pickle.load(f)
                self.logger.info("✅ Loaded existing anomaly detector")
            else:
                self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
                self.logger.info("🆕 Created new anomaly detector")
            
            # Load or create clustering model
            self.pattern_clustering = DBSCAN(eps=0.5, min_samples=3)
            
        except Exception as e:
            self.logger.error(f"Error loading/creating models: {e}")
            # Create fallback models
            self.threat_classifier = self._create_threat_classifier()
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.pattern_clustering = DBSCAN(eps=0.5, min_samples=3)
    
    def _create_threat_classifier(self):
        """יצירת מסווג איומים פשוט"""
        # Simplified classifier for demo
        return {
            "model_type": "rule_based",
            "rules": {
                "malware": ["virus", "trojan", "worm", "ransomware"],
                "phishing": ["fake", "credential", "login", "bank"],
                "network": ["scan", "probe", "ddos", "injection"],
                "social": ["engineering", "manipulation", "deception"]
            }
        }
    
    async def _extract_threat_features(self, threat_data: Dict) -> Dict:
        """חילוץ תכונות מנתוני איום"""
        features = {
            "source_ip": threat_data.get("source_ip", ""),
            "target_port": threat_data.get("target_port", 0),
            "payload_size": len(str(threat_data.get("payload", ""))),
            "timestamp_hour": datetime.now().hour,
            "has_encryption": "encrypt" in str(threat_data).lower(),
            "has_obfuscation": "obfuscat" in str(threat_data).lower(),
            "connection_count": threat_data.get("connection_count", 1),
            "geographic_region": threat_data.get("region", "unknown")
        }
        
        return features
    
    async def _classify_threat(self, features: Dict) -> Dict:
        """סיווג איום"""
        if not self.threat_classifier:
            return {"type": "unknown", "confidence": 0.0}
        
        # Simple rule-based classification for demo
        threat_text = str(features).lower()
        
        for threat_type, keywords in self.threat_classifier["rules"].items():
            matches = sum(1 for keyword in keywords if keyword in threat_text)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                return {"type": threat_type, "confidence": confidence}
        
        return {"type": "unknown", "confidence": 0.0}
    
    async def _detect_anomaly(self, features: Dict) -> float:
        """זיהוי חריגות"""
        try:
            # Convert features to numeric array
            feature_vector = [
                features.get("target_port", 0),
                features.get("payload_size", 0),
                features.get("timestamp_hour", 0),
                int(features.get("has_encryption", False)),
                int(features.get("has_obfuscation", False)),
                features.get("connection_count", 1)
            ]
            
            # Simple anomaly scoring
            anomaly_score = 0.0
            
            # Check for unusual ports
            if features.get("target_port", 0) > 60000:
                anomaly_score += 0.3
            
            # Check for large payloads
            if features.get("payload_size", 0) > 10000:
                anomaly_score += 0.2
            
            # Check for unusual timing
            if features.get("timestamp_hour", 12) in [2, 3, 4]:  # 2-4 AM
                anomaly_score += 0.1
            
            return min(anomaly_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error detecting anomaly: {e}")
            return 0.0
    
    async def _match_threat_patterns(self, features: Dict) -> List[Dict]:
        """התאמת דפוסי איום"""
        matches = []
        
        for pattern_id, pattern in self.threat_patterns.items():
            similarity = await self._calculate_pattern_similarity(features, pattern)
            
            if similarity > self.pattern_similarity_threshold:
                matches.append({
                    "pattern_id": pattern_id,
                    "similarity": similarity,
                    "attack_type": pattern.attack_type,
                    "confidence": pattern.confidence
                })
        
        return sorted(matches, key=lambda x: x["similarity"], reverse=True)
    
    async def _calculate_pattern_similarity(self, features: Dict, pattern: ThreatPattern) -> float:
        """חישוב דמיון לדפוס"""
        # Simplified similarity calculation
        similarity_score = 0.0
        total_features = 0
        
        for marker, value in pattern.behavioral_markers.items():
            if marker in features:
                feature_value = features[marker]
                if isinstance(feature_value, (int, float)) and isinstance(value, (int, float)):
                    # Numeric similarity
                    max_val = max(abs(feature_value), abs(value), 1)
                    similarity_score += 1.0 - abs(feature_value - value) / max_val
                else:
                    # String similarity
                    similarity_score += 1.0 if str(feature_value).lower() == str(value).lower() else 0.0
                total_features += 1
        
        return similarity_score / max(total_features, 1)
    
    async def _generate_threat_dna(self, threat_data: Dict, features: Dict) -> Dict:
        """יצירת DNA של איום"""
        dna_string = json.dumps({
            "features": features,
            "patterns": sorted(threat_data.get("patterns", [])),
            "behaviors": sorted(threat_data.get("behaviors", []))
        }, sort_keys=True)
        
        dna_hash = hashlib.sha256(dna_string.encode()).hexdigest()[:16]
        
        return {
            "id": f"dna_{dna_hash}",
            "hash": dna_hash,
            "features": features,
            "generation_time": datetime.now().isoformat(),
            "source_data": threat_data
        }
    
    async def _periodic_model_update(self):
        """עדכון תקופתי של מודלים"""
        while True:
            try:
                await asyncio.sleep(self.model_update_interval)
                
                self.logger.info("🔄 Starting periodic model update...")
                
                # Retrain models with new data
                await self._retrain_models()
                
                # Update accuracy metrics
                await self._update_accuracy_metrics()
                
                self.logger.info("✅ Periodic model update complete")
                
            except Exception as e:
                self.logger.error(f"Error in periodic model update: {e}")
    
    async def _retrain_models(self):
        """אימון מחדש של מודלים"""
        # Implementation for model retraining
        pass
    
    async def _update_accuracy_metrics(self):
        """עדכון מדדי דיוק"""
        # Implementation for accuracy calculation
        self.accuracy_score = 0.95  # Placeholder
    
    # Additional helper methods would continue here...
    # For brevity, I'm including key methods but not all implementation details
    
    async def _load_threat_patterns(self):
        """טעינת דפוסי איום"""
        patterns_file = "data/threat_patterns.json"
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, "r", encoding="utf-8") as f:
                    patterns_data = json.load(f)
                    # Convert to ThreatPattern objects
                    # Implementation details...
                self.logger.info(f"✅ Loaded {len(self.threat_patterns)} threat patterns")
            except Exception as e:
                self.logger.error(f"Error loading threat patterns: {e}")
    
    async def _save_threat_patterns(self):
        """שמירת דפוסי איום"""
        os.makedirs("data", exist_ok=True)
        try:
            patterns_data = {}
            for pattern_id, pattern in self.threat_patterns.items():
                patterns_data[pattern_id] = {
                    "pattern_id": pattern.pattern_id,
                    "attack_type": pattern.attack_type,
                    "signatures": pattern.signatures,
                    "behavioral_markers": pattern.behavioral_markers,
                    "confidence": pattern.confidence,
                    "first_seen": pattern.first_seen.isoformat(),
                    "last_seen": pattern.last_seen.isoformat(),
                    "occurrence_count": pattern.occurrence_count
                }
            
            with open("data/threat_patterns.json", "w", encoding="utf-8") as f:
                json.dump(patterns_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"✅ Saved {len(self.threat_patterns)} threat patterns")
        except Exception as e:
            self.logger.error(f"Error saving threat patterns: {e}")
    
    async def _load_global_intelligence(self):
        """טעינת מודיעין גלובלי"""
        # Implementation for loading global intelligence
        pass
    
    async def _save_global_intelligence(self):
        """שמירת מודיעין גלובלי"""
        # Implementation for saving global intelligence
        pass
    
    async def _save_models(self):
        """שמירת מודלים"""
        models_dir = "models/ai_coordinator"
        os.makedirs(models_dir, exist_ok=True)
        
        try:
            if self.threat_classifier:
                with open(f"{models_dir}/threat_classifier.pkl", "wb") as f:
                    pickle.dump(self.threat_classifier, f)
            
            if self.anomaly_detector:
                with open(f"{models_dir}/anomaly_detector.pkl", "wb") as f:
                    pickle.dump(self.anomaly_detector, f)
                    
            self.logger.info("✅ Models saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving models: {e}")
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות AI"""
        return {
            "total_threats_analyzed": self.total_threats_analyzed,
            "patterns_discovered": len(self.threat_patterns),
            "predictions_made": self.predictions_made,
            "accuracy_score": self.accuracy_score,
            "models_loaded": {
                "threat_classifier": self.threat_classifier is not None,
                "anomaly_detector": self.anomaly_detector is not None,
                "pattern_clustering": self.pattern_clustering is not None
            }
        }
