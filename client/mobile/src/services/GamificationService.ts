/**
 * Gamification Service for HoneyNet Mobile
 * שירות גיימיפיקציה לאפליקציית HoneyNet לנייד
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { HoneyNetService } from './HoneyNetService';

export interface PlayerStats {
  playerId: string;
  level: number;
  totalPoints: number;
  threatsDetected: number;
  honeypotsTriggered: number;
  currentLeague: string;
  achievements: Achievement[];
  nftBadges: NFTBadge[];
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlockedAt: Date;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  points: number;
}

export interface NFTBadge {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  mintedAt: Date;
  rarity: string;
  attributes: Record<string, any>;
}

export interface Leaderboard {
  players: LeaderboardEntry[];
  userRank: number;
  totalPlayers: number;
}

export interface LeaderboardEntry {
  playerId: string;
  playerName: string;
  level: number;
  points: number;
  rank: number;
  avatar?: string;
}

class GamificationServiceClass {
  private playerStats: PlayerStats | null = null;
  private achievements: Achievement[] = [];
  private leaderboard: Leaderboard | null = null;

  async initializePlayer(playerId: string): Promise<PlayerStats> {
    try {
      // Try to load existing player data
      const savedStats = await AsyncStorage.getItem(`player_stats_${playerId}`);
      
      if (savedStats) {
        this.playerStats = JSON.parse(savedStats);
      } else {
        // Create new player
        this.playerStats = {
          playerId,
          level: 1,
          totalPoints: 0,
          threatsDetected: 0,
          honeypotsTriggered: 0,
          currentLeague: 'Bronze',
          achievements: [],
          nftBadges: []
        };
        
        await this.savePlayerStats();
      }

      return this.playerStats;
    } catch (error) {
      console.error('Error initializing player:', error);
      throw error;
    }
  }

  async recordThreatDetection(threatType: string, severity: string): Promise<void> {
    if (!this.playerStats) return;

    try {
      // Calculate points based on threat severity
      const points = this.calculateThreatPoints(threatType, severity);
      
      this.playerStats.threatsDetected += 1;
      this.playerStats.totalPoints += points;
      
      // Check for level up
      await this.checkLevelUp();
      
      // Check for achievements
      await this.checkAchievements('threat_detection', {
        threatType,
        severity,
        totalDetected: this.playerStats.threatsDetected
      });
      
      await this.savePlayerStats();
      
      // Send to server
      await this.syncWithServer();
      
    } catch (error) {
      console.error('Error recording threat detection:', error);
    }
  }

  async recordHoneypotTrigger(honeypotType: string, attackerInfo: any): Promise<void> {
    if (!this.playerStats) return;

    try {
      const points = this.calculateHoneypotPoints(honeypotType, attackerInfo);
      
      this.playerStats.honeypotsTriggered += 1;
      this.playerStats.totalPoints += points;
      
      await this.checkLevelUp();
      await this.checkAchievements('honeypot_trigger', {
        honeypotType,
        attackerInfo,
        totalTriggered: this.playerStats.honeypotsTriggered
      });
      
      await this.savePlayerStats();
      await this.syncWithServer();
      
    } catch (error) {
      console.error('Error recording honeypot trigger:', error);
    }
  }

  async getPlayerStats(): Promise<PlayerStats | null> {
    return this.playerStats;
  }

  async getAchievements(): Promise<Achievement[]> {
    return this.playerStats?.achievements || [];
  }

  async getLeaderboard(league?: string): Promise<Leaderboard> {
    try {
      // Get leaderboard from server
      const response = await HoneyNetService.getLeaderboard(league);
      this.leaderboard = response;
      return this.leaderboard;
    } catch (error) {
      console.error('Error getting leaderboard:', error);
      return {
        players: [],
        userRank: 0,
        totalPlayers: 0
      };
    }
  }

  async claimReward(rewardId: string): Promise<boolean> {
    try {
      const response = await HoneyNetService.claimReward(rewardId);
      
      if (response.success) {
        // Update local stats with reward
        if (response.reward.type === 'points') {
          this.playerStats!.totalPoints += response.reward.amount;
        } else if (response.reward.type === 'nft') {
          this.playerStats!.nftBadges.push(response.reward.nft);
        }
        
        await this.savePlayerStats();
      }
      
      return response.success;
    } catch (error) {
      console.error('Error claiming reward:', error);
      return false;
    }
  }

  private calculateThreatPoints(threatType: string, severity: string): number {
    const basePoints = {
      'low': 10,
      'medium': 25,
      'high': 50,
      'critical': 100
    };

    const typeMultiplier = {
      'malware': 1.2,
      'phishing': 1.1,
      'ddos': 1.3,
      'brute_force': 1.0,
      'sql_injection': 1.4,
      'xss': 1.1
    };

    const base = basePoints[severity as keyof typeof basePoints] || 10;
    const multiplier = typeMultiplier[threatType as keyof typeof typeMultiplier] || 1.0;
    
    return Math.round(base * multiplier);
  }

  private calculateHoneypotPoints(honeypotType: string, attackerInfo: any): number {
    const basePoints = 30;
    
    // Bonus for new attacker
    const newAttackerBonus = attackerInfo.isNew ? 20 : 0;
    
    // Bonus for sophisticated attack
    const sophisticationBonus = attackerInfo.sophistication === 'high' ? 25 : 0;
    
    return basePoints + newAttackerBonus + sophisticationBonus;
  }

  private async checkLevelUp(): Promise<void> {
    if (!this.playerStats) return;

    const requiredPoints = this.getRequiredPointsForLevel(this.playerStats.level + 1);
    
    if (this.playerStats.totalPoints >= requiredPoints) {
      this.playerStats.level += 1;
      
      // Award level up achievement
      await this.unlockAchievement({
        id: `level_${this.playerStats.level}`,
        name: `Level ${this.playerStats.level}`,
        description: `Reached level ${this.playerStats.level}`,
        icon: 'level-up',
        unlockedAt: new Date(),
        rarity: this.playerStats.level >= 50 ? 'legendary' : 
               this.playerStats.level >= 25 ? 'epic' :
               this.playerStats.level >= 10 ? 'rare' : 'common',
        points: this.playerStats.level * 10
      });

      // Update league if necessary
      await this.updateLeague();
    }
  }

  private getRequiredPointsForLevel(level: number): number {
    // Exponential growth: level^2 * 100
    return level * level * 100;
  }

  private async updateLeague(): Promise<void> {
    if (!this.playerStats) return;

    const leagues = [
      { name: 'Bronze', minLevel: 1 },
      { name: 'Silver', minLevel: 10 },
      { name: 'Gold', minLevel: 25 },
      { name: 'Platinum', minLevel: 50 },
      { name: 'Diamond', minLevel: 75 },
      { name: 'Master', minLevel: 100 }
    ];

    const currentLeague = leagues
      .reverse()
      .find(league => this.playerStats!.level >= league.minLevel);

    if (currentLeague && currentLeague.name !== this.playerStats.currentLeague) {
      const oldLeague = this.playerStats.currentLeague;
      this.playerStats.currentLeague = currentLeague.name;

      // Award league promotion achievement
      await this.unlockAchievement({
        id: `league_${currentLeague.name.toLowerCase()}`,
        name: `${currentLeague.name} League`,
        description: `Promoted to ${currentLeague.name} League`,
        icon: 'trophy',
        unlockedAt: new Date(),
        rarity: currentLeague.name === 'Master' ? 'legendary' : 'epic',
        points: 500
      });
    }
  }

  private async checkAchievements(eventType: string, eventData: any): Promise<void> {
    const achievementChecks = [
      // Threat detection achievements
      {
        condition: eventType === 'threat_detection' && eventData.totalDetected === 1,
        achievement: {
          id: 'first_threat',
          name: 'First Blood',
          description: 'Detected your first threat',
          icon: 'shield-check',
          rarity: 'common' as const,
          points: 50
        }
      },
      {
        condition: eventType === 'threat_detection' && eventData.totalDetected === 10,
        achievement: {
          id: 'threat_hunter',
          name: 'Threat Hunter',
          description: 'Detected 10 threats',
          icon: 'crosshairs',
          rarity: 'rare' as const,
          points: 200
        }
      },
      {
        condition: eventType === 'threat_detection' && eventData.totalDetected === 100,
        achievement: {
          id: 'cyber_guardian',
          name: 'Cyber Guardian',
          description: 'Detected 100 threats',
          icon: 'shield',
          rarity: 'epic' as const,
          points: 1000
        }
      },
      // Honeypot achievements
      {
        condition: eventType === 'honeypot_trigger' && eventData.totalTriggered === 1,
        achievement: {
          id: 'first_catch',
          name: 'First Catch',
          description: 'Caught your first attacker',
          icon: 'bug-report',
          rarity: 'common' as const,
          points: 75
        }
      },
      {
        condition: eventType === 'honeypot_trigger' && eventData.totalTriggered === 25,
        achievement: {
          id: 'honey_master',
          name: 'Honey Master',
          description: 'Triggered 25 honeypots',
          icon: 'hive',
          rarity: 'epic' as const,
          points: 750
        }
      }
    ];

    for (const check of achievementChecks) {
      if (check.condition) {
        await this.unlockAchievement({
          ...check.achievement,
          unlockedAt: new Date()
        });
      }
    }
  }

  private async unlockAchievement(achievement: Achievement): Promise<void> {
    if (!this.playerStats) return;

    // Check if already unlocked
    const alreadyUnlocked = this.playerStats.achievements.some(a => a.id === achievement.id);
    if (alreadyUnlocked) return;

    this.playerStats.achievements.push(achievement);
    this.playerStats.totalPoints += achievement.points;

    // Show notification
    // NotificationService.showAchievement(achievement);
  }

  private async savePlayerStats(): Promise<void> {
    if (!this.playerStats) return;

    try {
      await AsyncStorage.setItem(
        `player_stats_${this.playerStats.playerId}`,
        JSON.stringify(this.playerStats)
      );
    } catch (error) {
      console.error('Error saving player stats:', error);
    }
  }

  private async syncWithServer(): Promise<void> {
    if (!this.playerStats) return;

    try {
      await HoneyNetService.syncPlayerStats(this.playerStats);
    } catch (error) {
      console.error('Error syncing with server:', error);
      // Continue offline - sync will happen later
    }
  }

  async cleanup(): Promise<void> {
    // Save final state
    await this.savePlayerStats();
    
    // Clear memory
    this.playerStats = null;
    this.achievements = [];
    this.leaderboard = null;
  }
}

export const GamificationService = new GamificationServiceClass();
