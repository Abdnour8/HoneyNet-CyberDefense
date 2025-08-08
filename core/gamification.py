"""
HoneyNet Gamification System
מערכת גיימיפיקציה למוטיבציה של משתמשים
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import random


class BadgeType(Enum):
    """סוגי תגים"""
    THREAT_HUNTER = "threat_hunter"
    HONEYPOT_MASTER = "honeypot_master"
    NETWORK_GUARDIAN = "network_guardian"
    AI_TRAINER = "ai_trainer"
    GLOBAL_DEFENDER = "global_defender"
    QUANTUM_PROTECTOR = "quantum_protector"
    BLOCKCHAIN_VALIDATOR = "blockchain_validator"
    SWARM_COORDINATOR = "swarm_coordinator"


class LeagueLevel(Enum):
    """רמות ליגה"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    LEGEND = "legend"


@dataclass
class Achievement:
    """הישג"""
    id: str
    name: str
    description: str
    badge_type: BadgeType
    points: int
    rarity: str  # common, rare, epic, legendary
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0
    max_progress: float = 100.0
    nft_token_id: Optional[str] = None


@dataclass
class PlayerStats:
    """סטטיסטיקות שחקן"""
    user_id: str
    username: str
    level: int = 1
    experience_points: int = 0
    total_points: int = 0
    league: LeagueLevel = LeagueLevel.BRONZE
    
    # Combat stats
    threats_detected: int = 0
    threats_blocked: int = 0
    honeypots_triggered: int = 0
    false_positives: int = 0
    accuracy_rate: float = 0.0
    
    # Achievements
    achievements: List[Achievement] = field(default_factory=list)
    badges: List[BadgeType] = field(default_factory=list)
    
    # Social
    guild_id: Optional[str] = None
    friends: List[str] = field(default_factory=list)
    reputation: int = 1000
    
    # Time tracking
    join_date: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    total_playtime: int = 0  # minutes
    
    # Streaks
    daily_streak: int = 0
    weekly_streak: int = 0
    best_streak: int = 0


@dataclass
class CyberDefenseLeague:
    """ליגת הגנה סייבר"""
    league_id: str
    name: str
    level: LeagueLevel
    season_start: datetime
    season_end: datetime
    participants: List[str] = field(default_factory=list)
    leaderboard: List[Tuple[str, int]] = field(default_factory=list)
    prizes: Dict[str, str] = field(default_factory=dict)
    active: bool = True


@dataclass
class NFTSecurityBadge:
    """תג אבטחה NFT"""
    token_id: str
    owner_id: str
    badge_type: BadgeType
    achievement_id: str
    rarity: str
    mint_date: datetime
    metadata: Dict = field(default_factory=dict)
    blockchain_hash: Optional[str] = None
    verified: bool = False


class GamificationEngine:
    """מנוע גיימיפיקציה"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Player data
        self.players: Dict[str, PlayerStats] = {}
        self.achievements_catalog: Dict[str, Achievement] = {}
        self.leagues: Dict[str, CyberDefenseLeague] = {}
        self.nft_badges: Dict[str, NFTSecurityBadge] = {}
        
        # Game configuration
        self.level_thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]
        self.league_thresholds = {
            LeagueLevel.BRONZE: 0,
            LeagueLevel.SILVER: 500,
            LeagueLevel.GOLD: 1500,
            LeagueLevel.PLATINUM: 3000,
            LeagueLevel.DIAMOND: 5000,
            LeagueLevel.MASTER: 8000,
            LeagueLevel.GRANDMASTER: 12000,
            LeagueLevel.LEGEND: 20000
        }
        
        # Initialize achievements
        self._initialize_achievements()
        
        self.logger.info("🎮 Gamification Engine initialized")
    
    def _initialize_achievements(self):
        """אתחול הישגים"""
        achievements = [
            # Threat Detection Achievements
            Achievement("first_threat", "First Contact", "Detect your first threat", 
                       BadgeType.THREAT_HUNTER, 50, "common"),
            Achievement("threat_hunter_10", "Threat Hunter", "Detect 10 threats", 
                       BadgeType.THREAT_HUNTER, 200, "common"),
            Achievement("threat_hunter_100", "Cyber Sentinel", "Detect 100 threats", 
                       BadgeType.THREAT_HUNTER, 1000, "rare"),
            Achievement("threat_hunter_1000", "Digital Guardian", "Detect 1000 threats", 
                       BadgeType.THREAT_HUNTER, 5000, "epic"),
            
            # Honeypot Achievements
            Achievement("honeypot_master", "Honeypot Master", "Deploy 50 successful honeypots", 
                       BadgeType.HONEYPOT_MASTER, 800, "rare"),
            Achievement("trap_lord", "Trap Lord", "Catch 100 attackers in honeypots", 
                       BadgeType.HONEYPOT_MASTER, 2000, "epic"),
            
            # Network Achievements
            Achievement("network_defender", "Network Defender", "Block 50 attacks", 
                       BadgeType.NETWORK_GUARDIAN, 500, "common"),
            Achievement("fortress_builder", "Fortress Builder", "Maintain 99% uptime for 30 days", 
                       BadgeType.NETWORK_GUARDIAN, 1500, "rare"),
            
            # AI Training Achievements
            Achievement("ai_trainer", "AI Trainer", "Help train AI models with 100 samples", 
                       BadgeType.AI_TRAINER, 1000, "rare"),
            Achievement("machine_whisperer", "Machine Whisperer", "Achieve 95% AI accuracy", 
                       BadgeType.AI_TRAINER, 3000, "epic"),
            
            # Global Achievements
            Achievement("global_defender", "Global Defender", "Share threat intel globally 100 times", 
                       BadgeType.GLOBAL_DEFENDER, 1200, "rare"),
            Achievement("world_guardian", "World Guardian", "Help protect 10 different countries", 
                       BadgeType.GLOBAL_DEFENDER, 5000, "legendary"),
            
            # Advanced Tech Achievements
            Achievement("quantum_pioneer", "Quantum Pioneer", "Deploy quantum-resistant honeypots", 
                       BadgeType.QUANTUM_PROTECTOR, 2500, "epic"),
            Achievement("blockchain_validator", "Blockchain Validator", "Validate 100 threat records", 
                       BadgeType.BLOCKCHAIN_VALIDATOR, 1800, "rare"),
            Achievement("swarm_leader", "Swarm Leader", "Coordinate 50 swarm intelligence operations", 
                       BadgeType.SWARM_COORDINATOR, 3500, "legendary"),
            
            # Special Achievements
            Achievement("perfect_week", "Perfect Week", "Zero false positives for 7 days", 
                       BadgeType.NETWORK_GUARDIAN, 800, "rare"),
            Achievement("night_owl", "Night Owl", "Detect threats during night hours (2-6 AM)", 
                       BadgeType.THREAT_HUNTER, 300, "common"),
            Achievement("speed_demon", "Speed Demon", "Block threat within 1 second of detection", 
                       BadgeType.NETWORK_GUARDIAN, 600, "rare"),
        ]
        
        for achievement in achievements:
            self.achievements_catalog[achievement.id] = achievement
    
    async def register_player(self, user_id: str, username: str) -> PlayerStats:
        """רישום שחקן חדש"""
        if user_id in self.players:
            return self.players[user_id]
        
        player = PlayerStats(
            user_id=user_id,
            username=username,
            join_date=datetime.now(),
            last_active=datetime.now()
        )
        
        self.players[user_id] = player
        
        # Award first login achievement
        await self._award_achievement(user_id, "first_contact")
        
        self.logger.info(f"🎮 New player registered: {username}")
        return player
    
    async def record_threat_detection(self, user_id: str, threat_data: Dict) -> Dict:
        """רישום זיהוי איום"""
        if user_id not in self.players:
            return {"error": "Player not found"}
        
        player = self.players[user_id]
        player.threats_detected += 1
        player.last_active = datetime.now()
        
        # Award points based on threat severity
        severity = threat_data.get("severity", "medium")
        points = {"low": 10, "medium": 25, "high": 50, "critical": 100}.get(severity, 25)
        
        await self._award_points(user_id, points)
        
        # Check for achievements
        await self._check_threat_achievements(user_id)
        
        # Update accuracy
        await self._update_accuracy(user_id, True)
        
        return {
            "points_awarded": points,
            "total_threats": player.threats_detected,
            "level": player.level,
            "achievements_unlocked": []
        }
    
    async def record_honeypot_trigger(self, user_id: str, honeypot_data: Dict) -> Dict:
        """רישום הפעלת פיתיון"""
        if user_id not in self.players:
            return {"error": "Player not found"}
        
        player = self.players[user_id]
        player.honeypots_triggered += 1
        player.last_active = datetime.now()
        
        # Award points based on effectiveness
        effectiveness = honeypot_data.get("effectiveness_score", 0.5)
        points = int(effectiveness * 75)  # 0-75 points
        
        await self._award_points(user_id, points)
        
        # Check for honeypot achievements
        await self._check_honeypot_achievements(user_id)
        
        return {
            "points_awarded": points,
            "total_honeypots": player.honeypots_triggered,
            "level": player.level
        }
    
    async def record_false_positive(self, user_id: str) -> Dict:
        """רישום false positive"""
        if user_id not in self.players:
            return {"error": "Player not found"}
        
        player = self.players[user_id]
        player.false_positives += 1
        
        # Deduct points for false positive
        await self._deduct_points(user_id, 15)
        
        # Update accuracy
        await self._update_accuracy(user_id, False)
        
        return {
            "points_deducted": 15,
            "false_positives": player.false_positives,
            "accuracy_rate": player.accuracy_rate
        }
    
    async def get_player_profile(self, user_id: str) -> Dict:
        """קבלת פרופיל שחקן"""
        if user_id not in self.players:
            return {"error": "Player not found"}
        
        player = self.players[user_id]
        
        # Calculate next level progress
        current_level_threshold = self.level_thresholds[min(player.level - 1, len(self.level_thresholds) - 1)]
        next_level_threshold = self.level_thresholds[min(player.level, len(self.level_thresholds) - 1)]
        level_progress = (player.experience_points - current_level_threshold) / (next_level_threshold - current_level_threshold)
        
        return {
            "user_id": player.user_id,
            "username": player.username,
            "level": player.level,
            "experience_points": player.experience_points,
            "total_points": player.total_points,
            "league": player.league.value,
            "level_progress": min(level_progress, 1.0),
            "next_level_points": next_level_threshold - player.experience_points,
            "stats": {
                "threats_detected": player.threats_detected,
                "threats_blocked": player.threats_blocked,
                "honeypots_triggered": player.honeypots_triggered,
                "false_positives": player.false_positives,
                "accuracy_rate": player.accuracy_rate,
                "daily_streak": player.daily_streak,
                "best_streak": player.best_streak
            },
            "achievements": [
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "points": achievement.points,
                    "rarity": achievement.rarity,
                    "unlocked_at": achievement.unlocked_at.isoformat() if achievement.unlocked_at else None
                }
                for achievement in player.achievements
            ],
            "badges": [badge.value for badge in player.badges],
            "reputation": player.reputation,
            "join_date": player.join_date.isoformat(),
            "total_playtime": player.total_playtime
        }
    
    async def get_leaderboard(self, league: Optional[LeagueLevel] = None, limit: int = 100) -> List[Dict]:
        """קבלת לוח תוצאות"""
        players_list = list(self.players.values())
        
        # Filter by league if specified
        if league:
            players_list = [p for p in players_list if p.league == league]
        
        # Sort by total points
        players_list.sort(key=lambda p: p.total_points, reverse=True)
        
        leaderboard = []
        for i, player in enumerate(players_list[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "user_id": player.user_id,
                "username": player.username,
                "level": player.level,
                "total_points": player.total_points,
                "league": player.league.value,
                "threats_detected": player.threats_detected,
                "accuracy_rate": player.accuracy_rate,
                "badges_count": len(player.badges),
                "achievements_count": len(player.achievements)
            })
        
        return leaderboard
    
    async def create_nft_badge(self, user_id: str, achievement_id: str) -> Optional[NFTSecurityBadge]:
        """יצירת תג NFT"""
        if user_id not in self.players:
            return None
        
        if achievement_id not in self.achievements_catalog:
            return None
        
        achievement = self.achievements_catalog[achievement_id]
        player = self.players[user_id]
        
        # Generate unique token ID
        token_data = f"{user_id}_{achievement_id}_{datetime.now().timestamp()}"
        token_id = hashlib.sha256(token_data.encode()).hexdigest()[:16]
        
        # Create NFT badge
        nft_badge = NFTSecurityBadge(
            token_id=token_id,
            owner_id=user_id,
            badge_type=achievement.badge_type,
            achievement_id=achievement_id,
            rarity=achievement.rarity,
            mint_date=datetime.now(),
            metadata={
                "achievement_name": achievement.name,
                "achievement_description": achievement.description,
                "player_username": player.username,
                "player_level": player.level,
                "mint_timestamp": datetime.now().isoformat(),
                "rarity": achievement.rarity,
                "points_value": achievement.points
            }
        )
        
        # Store NFT
        self.nft_badges[token_id] = nft_badge
        
        # Link to achievement
        for player_achievement in player.achievements:
            if player_achievement.id == achievement_id:
                player_achievement.nft_token_id = token_id
                break
        
        self.logger.info(f"🎨 NFT Badge created: {token_id} for {player.username}")
        
        return nft_badge
    
    async def start_cyber_league(self, league_name: str, level: LeagueLevel, duration_days: int = 30) -> CyberDefenseLeague:
        """התחלת ליגת סייבר"""
        league_id = f"league_{datetime.now().timestamp()}"
        
        league = CyberDefenseLeague(
            league_id=league_id,
            name=league_name,
            level=level,
            season_start=datetime.now(),
            season_end=datetime.now() + timedelta(days=duration_days),
            prizes={
                "1st": "Legendary NFT Badge + 10,000 points",
                "2nd": "Epic NFT Badge + 5,000 points",
                "3rd": "Rare NFT Badge + 2,500 points",
                "top_10": "Special Achievement Badge"
            }
        )
        
        self.leagues[league_id] = league
        
        self.logger.info(f"🏆 New Cyber Defense League started: {league_name}")
        
        return league
    
    # Private helper methods
    
    async def _award_points(self, user_id: str, points: int):
        """הענקת נקודות"""
        player = self.players[user_id]
        player.experience_points += points
        player.total_points += points
        
        # Check for level up
        await self._check_level_up(user_id)
        
        # Check for league promotion
        await self._check_league_promotion(user_id)
    
    async def _deduct_points(self, user_id: str, points: int):
        """ניכוי נקודות"""
        player = self.players[user_id]
        player.total_points = max(0, player.total_points - points)
        player.experience_points = max(0, player.experience_points - points)
    
    async def _check_level_up(self, user_id: str):
        """בדיקת עליית רמה"""
        player = self.players[user_id]
        
        while (player.level < len(self.level_thresholds) and 
               player.experience_points >= self.level_thresholds[player.level]):
            player.level += 1
            self.logger.info(f"🎉 {player.username} leveled up to level {player.level}!")
    
    async def _check_league_promotion(self, user_id: str):
        """בדיקת עליית ליגה"""
        player = self.players[user_id]
        
        for league_level, threshold in self.league_thresholds.items():
            if player.total_points >= threshold and player.league.value < league_level.value:
                player.league = league_level
                self.logger.info(f"🏆 {player.username} promoted to {league_level.value} league!")
    
    async def _award_achievement(self, user_id: str, achievement_id: str):
        """הענקת הישג"""
        if achievement_id not in self.achievements_catalog:
            return
        
        player = self.players[user_id]
        achievement = self.achievements_catalog[achievement_id]
        
        # Check if already unlocked
        if any(a.id == achievement_id for a in player.achievements):
            return
        
        # Award achievement
        unlocked_achievement = Achievement(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            badge_type=achievement.badge_type,
            points=achievement.points,
            rarity=achievement.rarity,
            unlocked_at=datetime.now()
        )
        
        player.achievements.append(unlocked_achievement)
        
        # Add badge if not already have
        if achievement.badge_type not in player.badges:
            player.badges.append(achievement.badge_type)
        
        # Award points
        await self._award_points(user_id, achievement.points)
        
        # Create NFT for rare+ achievements
        if achievement.rarity in ["rare", "epic", "legendary"]:
            await self.create_nft_badge(user_id, achievement_id)
        
        self.logger.info(f"🏅 Achievement unlocked: {achievement.name} for {player.username}")
    
    async def _check_threat_achievements(self, user_id: str):
        """בדיקת הישגי זיהוי איומים"""
        player = self.players[user_id]
        
        if player.threats_detected == 1:
            await self._award_achievement(user_id, "first_threat")
        elif player.threats_detected == 10:
            await self._award_achievement(user_id, "threat_hunter_10")
        elif player.threats_detected == 100:
            await self._award_achievement(user_id, "threat_hunter_100")
        elif player.threats_detected == 1000:
            await self._award_achievement(user_id, "threat_hunter_1000")
    
    async def _check_honeypot_achievements(self, user_id: str):
        """בדיקת הישגי פיתיונות"""
        player = self.players[user_id]
        
        if player.honeypots_triggered == 50:
            await self._award_achievement(user_id, "honeypot_master")
        elif player.honeypots_triggered == 100:
            await self._award_achievement(user_id, "trap_lord")
    
    async def _update_accuracy(self, user_id: str, correct: bool):
        """עדכון דיוק"""
        player = self.players[user_id]
        
        total_detections = player.threats_detected + player.false_positives
        if total_detections > 0:
            player.accuracy_rate = player.threats_detected / total_detections
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות מערכת"""
        return {
            "total_players": len(self.players),
            "total_achievements": len(self.achievements_catalog),
            "total_nft_badges": len(self.nft_badges),
            "active_leagues": len([l for l in self.leagues.values() if l.active]),
            "total_points_awarded": sum(p.total_points for p in self.players.values()),
            "average_level": sum(p.level for p in self.players.values()) / len(self.players) if self.players else 0
        }
