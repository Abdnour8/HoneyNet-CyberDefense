/**
 * Blockchain Screen for HoneyNet Mobile
 * מסך בלוקצ'יין לאפליקציית HoneyNet לנייד
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  FlatList,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { BlockchainService, BlockchainStats, Block, ThreatRecord, MiningReward } from '../services/BlockchainService';
import { Colors } from '../constants/Colors';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Card } from '../components/Card';

export const BlockchainScreen: React.FC = () => {
  const [stats, setStats] = useState<BlockchainStats | null>(null);
  const [recentBlocks, setRecentBlocks] = useState<Block[]>([]);
  const [miningRewards, setMiningRewards] = useState<MiningReward[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'blocks' | 'mining'>('overview');
  const [isConnected, setIsConnected] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadBlockchainData();
    }, [])
  );

  const loadBlockchainData = async () => {
    try {
      setLoading(true);
      
      const [blockchainStats, blocks, rewards] = await Promise.all([
        BlockchainService.getBlockchainStats(),
        BlockchainService.getRecentBlocks(20),
        BlockchainService.getMiningRewards()
      ]);

      setStats(blockchainStats);
      setRecentBlocks(blocks);
      setMiningRewards(rewards);
      setIsConnected(BlockchainService.getConnectionStatus());
    } catch (error) {
      console.error('Error loading blockchain data:', error);
      Alert.alert('Error', 'Failed to load blockchain data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadBlockchainData();
    setRefreshing(false);
  };

  const handleStartMining = async () => {
    try {
      const success = await BlockchainService.startMining();
      if (success) {
        Alert.alert('Success', 'Mining started successfully');
        await loadBlockchainData();
      } else {
        Alert.alert('Error', 'Failed to start mining');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to start mining');
    }
  };

  const handleStopMining = async () => {
    try {
      const success = await BlockchainService.stopMining();
      if (success) {
        Alert.alert('Success', 'Mining stopped');
        await loadBlockchainData();
      } else {
        Alert.alert('Error', 'Failed to stop mining');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to stop mining');
    }
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

  const renderOverview = () => {
    if (!stats) return null;

    return (
      <View>
        {/* Connection Status */}
        <Card style={styles.statusCard}>
          <View style={styles.statusHeader}>
            <Icon 
              name={isConnected ? "check-circle" : "alert-circle"} 
              size={24} 
              color={isConnected ? Colors.success : Colors.error} 
            />
            <Text style={styles.statusText}>
              {isConnected ? 'Connected to Blockchain Network' : 'Offline Mode'}
            </Text>
          </View>
          <Text style={styles.nodeIdText}>
            Node ID: {BlockchainService.getNodeId().substring(0, 16)}...
          </Text>
        </Card>

        {/* Blockchain Stats */}
        <Card style={styles.statsCard}>
          <Text style={styles.cardTitle}>📊 Blockchain Statistics</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.totalBlocks}</Text>
              <Text style={styles.statLabel}>Total Blocks</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.activeNodes}</Text>
              <Text style={styles.statLabel}>Active Nodes</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.totalThreats}</Text>
              <Text style={styles.statLabel}>Threats Recorded</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{(stats.integrityScore * 100).toFixed(1)}%</Text>
              <Text style={styles.statLabel}>Chain Integrity</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{stats.networkHashRate.toFixed(2)}</Text>
              <Text style={styles.statLabel}>Hash Rate (H/s)</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>
                {new Date(stats.lastBlockTime).toLocaleTimeString()}
              </Text>
              <Text style={styles.statLabel}>Last Block</Text>
            </View>
          </View>
        </Card>

        {/* Quick Actions */}
        <Card style={styles.actionsCard}>
          <Text style={styles.cardTitle}>⚡ Quick Actions</Text>
          
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => Alert.alert('Submit Threat', 'This would open threat submission form')}
          >
            <Icon name="shield-alert" size={24} color={Colors.primary} />
            <Text style={styles.actionButtonText}>Submit Threat Record</Text>
            <Icon name="chevron-right" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => Alert.alert('Verify Chain', 'Chain verification started')}
          >
            <Icon name="check-decagram" size={24} color={Colors.success} />
            <Text style={styles.actionButtonText}>Verify Chain Integrity</Text>
            <Icon name="chevron-right" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>
        </Card>
      </View>
    );
  };

  const renderBlockItem = ({ item }: { item: Block }) => (
    <Card style={styles.blockCard}>
      <View style={styles.blockHeader}>
        <View style={styles.blockNumber}>
          <Text style={styles.blockNumberText}>#{item.blockNumber}</Text>
        </View>
        <View style={styles.blockInfo}>
          <Text style={styles.blockHash}>
            {item.blockHash.substring(0, 16)}...
          </Text>
          <Text style={styles.blockTime}>
            {new Date(item.timestamp).toLocaleString()}
          </Text>
        </View>
      </View>
      
      <View style={styles.blockDetails}>
        <View style={styles.blockDetail}>
          <Icon name="shield-bug" size={16} color={Colors.textSecondary} />
          <Text style={styles.blockDetailText}>
            {item.threatRecords.length} threats
          </Text>
        </View>
        
        <View style={styles.blockDetail}>
          <Icon name="account" size={16} color={Colors.textSecondary} />
          <Text style={styles.blockDetailText}>
            Miner: {item.minerId.substring(0, 8)}...
          </Text>
        </View>
      </View>
    </Card>
  );

  const renderBlocks = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>🧱 Recent Blocks</Text>
      
      {recentBlocks.length > 0 ? (
        <FlatList
          data={recentBlocks}
          renderItem={renderBlockItem}
          keyExtractor={(item) => item.blockHash}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="cube-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No blocks available</Text>
          <Text style={styles.emptySubtext}>Connect to the network to see blocks</Text>
        </Card>
      )}
    </View>
  );

  const renderMiningReward = ({ item }: { item: MiningReward }) => (
    <Card style={styles.rewardCard}>
      <View style={styles.rewardHeader}>
        <Icon name="pickaxe" size={24} color={Colors.primary} />
        <View style={styles.rewardInfo}>
          <Text style={styles.rewardBlock}>Block #{item.blockNumber}</Text>
          <Text style={styles.rewardTime}>
            {new Date(item.timestamp).toLocaleString()}
          </Text>
        </View>
        <View style={styles.rewardAmount}>
          <Text style={styles.rewardValue}>+{item.reward}</Text>
          <Text style={styles.rewardLabel}>HNT</Text>
        </View>
      </View>
    </Card>
  );

  const renderMining = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>⛏️ Mining Operations</Text>
      
      {/* Mining Controls */}
      <Card style={styles.miningCard}>
        <Text style={styles.cardTitle}>Mining Status</Text>
        
        <View style={styles.miningControls}>
          <TouchableOpacity 
            style={[styles.miningButton, styles.startButton]}
            onPress={handleStartMining}
            disabled={!isConnected}
          >
            <Icon name="play" size={20} color={Colors.white} />
            <Text style={styles.miningButtonText}>Start Mining</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.miningButton, styles.stopButton]}
            onPress={handleStopMining}
          >
            <Icon name="stop" size={20} color={Colors.white} />
            <Text style={styles.miningButtonText}>Stop Mining</Text>
          </TouchableOpacity>
        </View>

        {!isConnected && (
          <Text style={styles.miningWarning}>
            ⚠️ Connect to network to start mining
          </Text>
        )}
      </Card>

      {/* Mining Rewards */}
      <Text style={styles.sectionTitle}>💰 Mining Rewards</Text>
      
      {miningRewards.length > 0 ? (
        <FlatList
          data={miningRewards}
          renderItem={renderMiningReward}
          keyExtractor={(item) => `${item.blockNumber}_${item.timestamp}`}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="currency-btc" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No mining rewards yet</Text>
          <Text style={styles.emptySubtext}>Start mining to earn HNT tokens</Text>
        </Card>
      )}
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner />
        <Text style={styles.loadingText}>Loading blockchain data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview', 'view-dashboard')}
        {renderTabButton('blocks', 'Blocks', 'cube')}
        {renderTabButton('mining', 'Mining', 'pickaxe')}
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'blocks' && renderBlocks()}
        {activeTab === 'mining' && renderMining()}
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
  tabContent: {
    flex: 1,
  },
  statusCard: {
    marginBottom: 16,
    padding: 16,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusText: {
    marginLeft: 12,
    fontSize: 16,
    fontWeight: '500',
    color: Colors.text,
  },
  nodeIdText: {
    fontSize: 12,
    color: Colors.textSecondary,
    fontFamily: 'monospace',
  },
  statsCard: {
    marginBottom: 16,
    padding: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.primary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  actionsCard: {
    marginBottom: 16,
    padding: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: Colors.surface,
    borderRadius: 8,
    marginBottom: 8,
  },
  actionButtonText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
    color: Colors.text,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  blockCard: {
    marginBottom: 12,
    padding: 16,
  },
  blockHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  blockNumber: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  blockNumberText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: Colors.white,
  },
  blockInfo: {
    flex: 1,
  },
  blockHash: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    fontFamily: 'monospace',
    marginBottom: 4,
  },
  blockTime: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  blockDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  blockDetail: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  blockDetailText: {
    marginLeft: 4,
    fontSize: 12,
    color: Colors.textSecondary,
  },
  miningCard: {
    marginBottom: 16,
    padding: 16,
  },
  miningControls: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  miningButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  startButton: {
    backgroundColor: Colors.success,
  },
  stopButton: {
    backgroundColor: Colors.error,
  },
  miningButtonText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: Colors.white,
  },
  miningWarning: {
    fontSize: 14,
    color: Colors.warning,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  rewardCard: {
    marginBottom: 8,
    padding: 16,
  },
  rewardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  rewardInfo: {
    flex: 1,
    marginLeft: 12,
  },
  rewardBlock: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
  },
  rewardTime: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  rewardAmount: {
    alignItems: 'flex-end',
  },
  rewardValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.success,
  },
  rewardLabel: {
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
