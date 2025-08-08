/**
 * Gamification Screen for HoneyNet Mobile
 * מסך גיימיפיקציה לאפליקציית HoneyNet לנייד
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Dimensions,
  Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { GamificationService, PlayerStats, Achievement, Leaderboard } from '../services/GamificationService';
import { Colors } from '../constants/Colors';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';

const { width } = Dimensions.get('window');

export const GamificationScreen: React.FC = () => {
  const [playerStats, setPlayerStats] = useState<PlayerStats | null>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [leaderboard, setLeaderboard] = useState<Leaderboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'achievements' | 'leaderboard'>('profile');

  useFocusEffect(
    useCallback(() => {
      loadGamificationData();
    }, [])
  );

  const loadGamificationData = async () => {
    try {
      setLoading(true);
      
      const [stats, achievementsList, leaderboardData] = await Promise.all([
        GamificationService.getPlayerStats(),
        GamificationService.getAchievements(),
        GamificationService.getLeaderboard()
      ]);

      setPlayerStats(stats);
      setAchievements(achievementsList);
      setLeaderboard(leaderboardData);
    } catch (error) {
      console.error('Error loading gamification data:', error);
      Alert.alert('Error', 'Failed to load gamification data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadGamificationData();
    setRefreshing(false);
  };

  const renderTabButton = (tab: typeof activeTab, title: string, icon: string) => (
    <TouchableOpacity
      style={[styles.tabButton, activeTab === tab && styles.activeTabButton]}
      onPress={() => setActiveTab(tab)}
    >
      <Icon name={icon} size={20} color={activeTab === tab ? Colors.primary : Colors.textSecondary} />
      <Text style={[styles.tabButtonText, activeTab === tab && styles.activeTabButtonText]}>
        {title}
      </Text>
    </TouchableOpacity>
  );

  const renderPlayerProfile = () => {
    if (!playerStats) return null;

    const nextLevelPoints = Math.pow(playerStats.level + 1, 2) * 100;
    const currentLevelPoints = Math.pow(playerStats.level, 2) * 100;
    const progressToNextLevel = (playerStats.totalPoints - currentLevelPoints) / (nextLevelPoints - currentLevelPoints);

    return (
      <View>
        {/* Player Level Card */}
        <Card style={styles.levelCard}>
          <View style={styles.levelHeader}>
            <View style={styles.levelBadge}>
              <Text style={styles.levelNumber}>{playerStats.level}</Text>
            </View>
            <View style={styles.levelInfo}>
              <Text style={styles.playerName}>Cyber Guardian</Text>
              <Text style={styles.leagueName}>{playerStats.currentLeague} League</Text>
            </View>
          </View>
          
          <View style={styles.progressSection}>
            <Text style={styles.progressLabel}>
              Progress to Level {playerStats.level + 1}
            </Text>
            <ProgressBar 
              progress={progressToNextLevel} 
              color={Colors.primary}
              style={styles.progressBar}
            />
            <Text style={styles.progressText}>
              {playerStats.totalPoints - currentLevelPoints} / {nextLevelPoints - currentLevelPoints} XP
            </Text>
          </View>
        </Card>

        {/* Stats Cards */}
        <View style={styles.statsGrid}>
          <Card style={styles.statCard}>
            <Icon name="shield-check" size={32} color={Colors.success} />
            <Text style={styles.statNumber}>{playerStats.threatsDetected}</Text>
            <Text style={styles.statLabel}>Threats Detected</Text>
          </Card>
          
          <Card style={styles.statCard}>
            <Icon name="bug" size={32} color={Colors.warning} />
            <Text style={styles.statNumber}>{playerStats.honeypotsTriggered}</Text>
            <Text style={styles.statLabel}>Honeypots Triggered</Text>
          </Card>
        </View>

        <View style={styles.statsGrid}>
          <Card style={styles.statCard}>
            <Icon name="star" size={32} color={Colors.primary} />
            <Text style={styles.statNumber}>{playerStats.totalPoints}</Text>
            <Text style={styles.statLabel}>Total Points</Text>
          </Card>
          
          <Card style={styles.statCard}>
            <Icon name="trophy" size={32} color={Colors.accent} />
            <Text style={styles.statNumber}>{playerStats.achievements.length}</Text>
            <Text style={styles.statLabel}>Achievements</Text>
          </Card>
        </View>

        {/* NFT Badges */}
        {playerStats.nftBadges.length > 0 && (
          <Card style={styles.nftSection}>
            <Text style={styles.sectionTitle}>🎖️ NFT Security Badges</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {playerStats.nftBadges.map((badge, index) => (
                <View key={index} style={styles.nftBadge}>
                  <View style={styles.nftImage}>
                    <Text style={styles.nftEmoji}>🛡️</Text>
                  </View>
                  <Text style={styles.nftName}>{badge.name}</Text>
                  <Text style={styles.nftRarity}>{badge.rarity}</Text>
                </View>
              ))}
            </ScrollView>
          </Card>
        )}
      </View>
    );
  };

  const renderAchievements = () => (
    <View>
      <Text style={styles.sectionTitle}>🏆 Achievements</Text>
      {achievements.map((achievement, index) => (
        <Card key={index} style={styles.achievementCard}>
          <View style={styles.achievementHeader}>
            <View style={[styles.achievementIcon, { backgroundColor: getRarityColor(achievement.rarity) }]}>
              <Icon name="trophy" size={24} color={Colors.white} />
            </View>
            <View style={styles.achievementInfo}>
              <Text style={styles.achievementName}>{achievement.name}</Text>
              <Text style={styles.achievementDescription}>{achievement.description}</Text>
              <Text style={styles.achievementPoints}>+{achievement.points} XP</Text>
            </View>
          </View>
          <Text style={styles.achievementDate}>
            Unlocked: {new Date(achievement.unlockedAt).toLocaleDateString()}
          </Text>
        </Card>
      ))}
      
      {achievements.length === 0 && (
        <Card style={styles.emptyCard}>
          <Icon name="trophy-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No achievements yet</Text>
          <Text style={styles.emptySubtext}>Start detecting threats to unlock achievements!</Text>
        </Card>
      )}
    </View>
  );

  const renderLeaderboard = () => (
    <View>
      <Text style={styles.sectionTitle}>🥇 Global Leaderboard</Text>
      
      {leaderboard?.userRank && (
        <Card style={styles.userRankCard}>
          <Text style={styles.userRankText}>Your Rank: #{leaderboard.userRank}</Text>
          <Text style={styles.userRankSubtext}>out of {leaderboard.totalPlayers} players</Text>
        </Card>
      )}

      {leaderboard?.players.map((player, index) => (
        <Card key={index} style={styles.leaderboardCard}>
          <View style={styles.leaderboardRank}>
            <Text style={styles.rankNumber}>#{player.rank}</Text>
          </View>
          <View style={styles.leaderboardInfo}>
            <Text style={styles.leaderboardName}>{player.playerName}</Text>
            <Text style={styles.leaderboardLevel}>Level {player.level}</Text>
          </View>
          <View style={styles.leaderboardPoints}>
            <Text style={styles.pointsNumber}>{player.points}</Text>
            <Text style={styles.pointsLabel}>XP</Text>
          </View>
        </Card>
      ))}

      {(!leaderboard || leaderboard.players.length === 0) && (
        <Card style={styles.emptyCard}>
          <Icon name="podium" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>Leaderboard unavailable</Text>
          <Text style={styles.emptySubtext}>Connect to the network to see rankings</Text>
        </Card>
      )}
    </View>
  );

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary': return '#FFD700';
      case 'epic': return '#9C27B0';
      case 'rare': return '#2196F3';
      default: return Colors.textSecondary;
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner />
        <Text style={styles.loadingText}>Loading gamification data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('profile', 'Profile', 'account')}
        {renderTabButton('achievements', 'Achievements', 'trophy')}
        {renderTabButton('leaderboard', 'Leaderboard', 'podium')}
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {activeTab === 'profile' && renderPlayerProfile()}
        {activeTab === 'achievements' && renderAchievements()}
        {activeTab === 'leaderboard' && renderLeaderboard()}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: Colors.background,
  },
  loadingText: {
    marginTop: 16,
    color: Colors.textSecondary,
    fontSize: 16,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: Colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  activeTabButton: {
    backgroundColor: Colors.primary + '20',
  },
  tabButtonText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: Colors.textSecondary,
  },
  activeTabButtonText: {
    color: Colors.primary,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  levelCard: {
    marginBottom: 16,
    padding: 20,
  },
  levelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  levelBadge: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  levelNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.white,
  },
  levelInfo: {
    flex: 1,
  },
  playerName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 4,
  },
  leagueName: {
    fontSize: 16,
    color: Colors.textSecondary,
  },
  progressSection: {
    marginTop: 16,
  },
  progressLabel: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 8,
  },
  progressBar: {
    marginBottom: 8,
  },
  progressText: {
    fontSize: 12,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 16,
  },
  statCard: {
    flex: 1,
    padding: 16,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.text,
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  nftSection: {
    marginTop: 16,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  nftBadge: {
    alignItems: 'center',
    marginRight: 16,
    width: 80,
  },
  nftImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  nftEmoji: {
    fontSize: 24,
  },
  nftName: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.text,
    textAlign: 'center',
    marginBottom: 2,
  },
  nftRarity: {
    fontSize: 10,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  achievementCard: {
    marginBottom: 12,
    padding: 16,
  },
  achievementHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  achievementIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  achievementInfo: {
    flex: 1,
  },
  achievementName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 2,
  },
  achievementDescription: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  achievementPoints: {
    fontSize: 12,
    color: Colors.primary,
    fontWeight: '500',
  },
  achievementDate: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  userRankCard: {
    marginBottom: 16,
    padding: 16,
    backgroundColor: Colors.primary + '10',
    alignItems: 'center',
  },
  userRankText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.primary,
    marginBottom: 4,
  },
  userRankSubtext: {
    fontSize: 14,
    color: Colors.textSecondary,
  },
  leaderboardCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    padding: 16,
  },
  leaderboardRank: {
    width: 40,
    alignItems: 'center',
    marginRight: 16,
  },
  rankNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
  },
  leaderboardInfo: {
    flex: 1,
  },
  leaderboardName: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
  },
  leaderboardLevel: {
    fontSize: 14,
    color: Colors.textSecondary,
  },
  leaderboardPoints: {
    alignItems: 'flex-end',
  },
  pointsNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  pointsLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  emptyCard: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.textSecondary,
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
});
