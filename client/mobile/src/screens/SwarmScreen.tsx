/**
 * Swarm Intelligence Screen for HoneyNet Mobile
 * מסך בינה נחילית לאפליקציית HoneyNet לנייד
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
  Dimensions,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { 
  SwarmService, 
  SwarmAgent, 
  SwarmTask, 
  PheromoneTrail, 
  CollectiveDecision,
  SwarmStats 
} from '../services/SwarmService';
import { Colors } from '../constants/Colors';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';

const { width } = Dimensions.get('window');

export const SwarmScreen: React.FC = () => {
  const [swarmStats, setSwarmStats] = useState<SwarmStats | null>(null);
  const [agents, setAgents] = useState<SwarmAgent[]>([]);
  const [activeTasks, setActiveTasks] = useState<SwarmTask[]>([]);
  const [pheromoneTrails, setPheromoneTrails] = useState<PheromoneTrail[]>([]);
  const [recentDecisions, setRecentDecisions] = useState<CollectiveDecision[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'tasks' | 'intelligence'>('overview');

  useFocusEffect(
    useCallback(() => {
      loadSwarmData();
    }, [])
  );

  const loadSwarmData = async () => {
    try {
      setLoading(true);
      
      const [stats, agentsList, tasks, trails, decisions] = await Promise.all([
        SwarmService.getSwarmStats(),
        SwarmService.getAgents(),
        SwarmService.getActiveTasks(),
        SwarmService.getPheromoneTrails(),
        SwarmService.getRecentDecisions(10)
      ]);

      setSwarmStats(stats);
      setAgents(agentsList);
      setActiveTasks(tasks);
      setPheromoneTrails(trails);
      setRecentDecisions(decisions);
    } catch (error) {
      console.error('Error loading swarm data:', error);
      Alert.alert('Error', 'Failed to load swarm intelligence data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSwarmData();
    setRefreshing(false);
  };

  const handleJoinSwarm = async () => {
    try {
      const success = await SwarmService.joinSwarm();
      if (success) {
        Alert.alert('Success', 'Successfully joined the swarm network');
        await loadSwarmData();
      } else {
        Alert.alert('Error', 'Failed to join swarm network');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to join swarm network');
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
    if (!swarmStats) return null;

    return (
      <View>
        {/* Swarm Status */}
        <Card style={styles.statusCard}>
          <View style={styles.statusHeader}>
            <Icon name="hexagon-multiple" size={32} color={Colors.primary} />
            <View style={styles.statusInfo}>
              <Text style={styles.statusTitle}>Swarm Network Status</Text>
              <Text style={styles.statusSubtitle}>
                {swarmStats.isConnected ? 'Connected & Active' : 'Offline'}
              </Text>
            </View>
            <View style={[styles.statusIndicator, { 
              backgroundColor: swarmStats.isConnected ? Colors.success : Colors.error 
            }]} />
          </View>
        </Card>

        {/* Network Stats */}
        <Card style={styles.statsCard}>
          <Text style={styles.cardTitle}>🌐 Network Statistics</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{swarmStats.totalAgents}</Text>
              <Text style={styles.statLabel}>Total Agents</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{swarmStats.activeAgents}</Text>
              <Text style={styles.statLabel}>Active Agents</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{swarmStats.completedTasks}</Text>
              <Text style={styles.statLabel}>Completed Tasks</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{swarmStats.activeTasks}</Text>
              <Text style={styles.statLabel}>Active Tasks</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{(swarmStats.networkEfficiency * 100).toFixed(1)}%</Text>
              <Text style={styles.statLabel}>Network Efficiency</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{swarmStats.knowledgeShared}</Text>
              <Text style={styles.statLabel}>Knowledge Shared</Text>
            </View>
          </View>
        </Card>

        {/* Collective Intelligence */}
        <Card style={styles.intelligenceCard}>
          <Text style={styles.cardTitle}>🧠 Collective Intelligence</Text>
          
          <View style={styles.intelligenceMetric}>
            <Text style={styles.intelligenceLabel}>Swarm IQ Score</Text>
            <View style={styles.intelligenceScore}>
              <Text style={styles.intelligenceNumber}>{swarmStats.collectiveIQ}</Text>
              <Text style={styles.intelligenceUnit}>/1000</Text>
            </View>
            <ProgressBar 
              progress={swarmStats.collectiveIQ / 1000} 
              color={Colors.primary}
              style={styles.intelligenceProgress}
            />
          </View>

          <View style={styles.emergentBehaviors}>
            <Text style={styles.emergentTitle}>Emergent Behaviors Detected:</Text>
            {swarmStats.emergentBehaviors.map((behavior, index) => (
              <View key={index} style={styles.behaviorItem}>
                <Icon name="lightbulb-on" size={16} color={Colors.accent} />
                <Text style={styles.behaviorText}>{behavior}</Text>
              </View>
            ))}
          </View>
        </Card>

        {/* Quick Actions */}
        <Card style={styles.actionsCard}>
          <Text style={styles.cardTitle}>⚡ Swarm Actions</Text>
          
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={handleJoinSwarm}
            disabled={swarmStats.isConnected}
          >
            <Icon name="hexagon-multiple" size={24} color={Colors.primary} />
            <Text style={styles.actionButtonText}>
              {swarmStats.isConnected ? 'Already Connected' : 'Join Swarm Network'}
            </Text>
            <Icon name="chevron-right" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => Alert.alert('Share Knowledge', 'Knowledge sharing initiated')}
          >
            <Icon name="share-variant" size={24} color={Colors.success} />
            <Text style={styles.actionButtonText}>Share Local Knowledge</Text>
            <Icon name="chevron-right" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>
        </Card>
      </View>
    );
  };

  const renderAgentItem = ({ item }: { item: SwarmAgent }) => (
    <Card style={styles.agentCard}>
      <View style={styles.agentHeader}>
        <View style={[styles.agentIcon, { backgroundColor: getAgentRoleColor(item.role) }]}>
          <Icon name={getAgentRoleIcon(item.role)} size={20} color={Colors.white} />
        </View>
        <View style={styles.agentInfo}>
          <Text style={styles.agentId}>Agent {item.agentId.substring(0, 8)}</Text>
          <Text style={styles.agentRole}>{item.role}</Text>
        </View>
        <View style={[styles.agentStatus, { 
          backgroundColor: item.isActive ? Colors.success : Colors.error 
        }]}>
          <Text style={styles.agentStatusText}>
            {item.isActive ? 'Active' : 'Inactive'}
          </Text>
        </View>
      </View>
      
      <View style={styles.agentMetrics}>
        <View style={styles.agentMetric}>
          <Text style={styles.metricLabel}>Tasks Completed</Text>
          <Text style={styles.metricValue}>{item.tasksCompleted}</Text>
        </View>
        <View style={styles.agentMetric}>
          <Text style={styles.metricLabel}>Efficiency</Text>
          <Text style={styles.metricValue}>{(item.efficiency * 100).toFixed(0)}%</Text>
        </View>
        <View style={styles.agentMetric}>
          <Text style={styles.metricLabel}>Trust Score</Text>
          <Text style={styles.metricValue}>{item.trustScore.toFixed(1)}</Text>
        </View>
      </View>
    </Card>
  );

  const renderAgents = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>🤖 Swarm Agents</Text>
      
      {agents.length > 0 ? (
        <FlatList
          data={agents}
          renderItem={renderAgentItem}
          keyExtractor={(item) => item.agentId}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="robot-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No agents available</Text>
          <Text style={styles.emptySubtext}>Join the swarm network to see agents</Text>
        </Card>
      )}
    </View>
  );

  const renderTaskItem = ({ item }: { item: SwarmTask }) => (
    <Card style={styles.taskCard}>
      <View style={styles.taskHeader}>
        <View style={[styles.taskPriority, { backgroundColor: getTaskPriorityColor(item.priority) }]}>
          <Text style={styles.taskPriorityText}>{item.priority}</Text>
        </View>
        <View style={styles.taskInfo}>
          <Text style={styles.taskType}>{item.taskType}</Text>
          <Text style={styles.taskDescription}>{item.description}</Text>
        </View>
      </View>
      
      <View style={styles.taskProgress}>
        <Text style={styles.taskProgressLabel}>Progress: {(item.progress * 100).toFixed(0)}%</Text>
        <ProgressBar 
          progress={item.progress} 
          color={getTaskPriorityColor(item.priority)}
          style={styles.taskProgressBar}
        />
      </View>

      <View style={styles.taskDetails}>
        <Text style={styles.taskDetail}>
          Assigned Agents: {item.assignedAgents.length}
        </Text>
        <Text style={styles.taskDetail}>
          Created: {new Date(item.createdAt).toLocaleDateString()}
        </Text>
      </View>
    </Card>
  );

  const renderTasks = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>📋 Active Tasks</Text>
      
      {activeTasks.length > 0 ? (
        <FlatList
          data={activeTasks}
          renderItem={renderTaskItem}
          keyExtractor={(item) => item.taskId}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="clipboard-list-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No active tasks</Text>
          <Text style={styles.emptySubtext}>Tasks will appear when assigned by the swarm</Text>
        </Card>
      )}
    </View>
  );

  const renderIntelligence = () => (
    <View style={styles.tabContent}>
      {/* Pheromone Trails */}
      <Text style={styles.sectionTitle}>🧭 Pheromone Trails</Text>
      
      {pheromoneTrails.map((trail, index) => (
        <Card key={index} style={styles.trailCard}>
          <View style={styles.trailHeader}>
            <Icon name="map-marker-path" size={20} color={Colors.primary} />
            <Text style={styles.trailType}>{trail.trailType}</Text>
            <Text style={styles.trailStrength}>
              Strength: {(trail.strength * 100).toFixed(0)}%
            </Text>
          </View>
          <Text style={styles.trailDescription}>{trail.description}</Text>
          <Text style={styles.trailAge}>
            Age: {Math.floor((Date.now() - trail.timestamp) / 1000 / 60)} minutes
          </Text>
        </Card>
      ))}

      {/* Recent Decisions */}
      <Text style={styles.sectionTitle}>🎯 Recent Collective Decisions</Text>
      
      {recentDecisions.map((decision, index) => (
        <Card key={index} style={styles.decisionCard}>
          <View style={styles.decisionHeader}>
            <Icon name="vote" size={20} color={Colors.accent} />
            <Text style={styles.decisionType}>{decision.decisionType}</Text>
            <Text style={styles.decisionConsensus}>
              {(decision.consensusLevel * 100).toFixed(0)}% consensus
            </Text>
          </View>
          <Text style={styles.decisionDescription}>{decision.description}</Text>
          <Text style={styles.decisionParticipants}>
            {decision.participatingAgents} agents participated
          </Text>
        </Card>
      ))}

      {recentDecisions.length === 0 && (
        <Card style={styles.emptyCard}>
          <Icon name="brain" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No collective decisions yet</Text>
          <Text style={styles.emptySubtext}>Decisions will appear as the swarm learns</Text>
        </Card>
      )}
    </View>
  );

  const getAgentRoleColor = (role: string) => {
    switch (role) {
      case 'scout': return Colors.primary;
      case 'worker': return Colors.success;
      case 'guard': return Colors.error;
      case 'coordinator': return Colors.accent;
      default: return Colors.textSecondary;
    }
  };

  const getAgentRoleIcon = (role: string) => {
    switch (role) {
      case 'scout': return 'radar';
      case 'worker': return 'hammer-wrench';
      case 'guard': return 'shield';
      case 'coordinator': return 'account-supervisor';
      default: return 'robot';
    }
  };

  const getTaskPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return Colors.error;
      case 'medium': return Colors.warning;
      case 'low': return Colors.success;
      default: return Colors.textSecondary;
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner />
        <Text style={styles.loadingText}>Loading swarm intelligence data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview', 'hexagon-multiple')}
        {renderTabButton('agents', 'Agents', 'robot')}
        {renderTabButton('tasks', 'Tasks', 'clipboard-list')}
        {renderTabButton('intelligence', 'Intelligence', 'brain')}
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'agents' && renderAgents()}
        {activeTab === 'tasks' && renderTasks()}
        {activeTab === 'intelligence' && renderIntelligence()}
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
    paddingHorizontal: 8,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 8,
    borderRadius: 6,
    marginHorizontal: 2,
  },
  activeTabButton: {
    backgroundColor: Colors.primary + '20',
  },
  tabButtonText: {
    marginLeft: 6,
    fontSize: 12,
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
  },
  statusInfo: {
    flex: 1,
    marginLeft: 16,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 4,
  },
  statusSubtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
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
  intelligenceCard: {
    marginBottom: 16,
    padding: 16,
  },
  intelligenceMetric: {
    marginBottom: 16,
  },
  intelligenceLabel: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 8,
  },
  intelligenceScore: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  intelligenceNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  intelligenceUnit: {
    fontSize: 16,
    color: Colors.textSecondary,
    marginLeft: 4,
  },
  intelligenceProgress: {
    marginBottom: 16,
  },
  emergentBehaviors: {
    marginTop: 16,
  },
  emergentTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 8,
  },
  behaviorItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  behaviorText: {
    marginLeft: 8,
    fontSize: 14,
    color: Colors.textSecondary,
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
  agentCard: {
    marginBottom: 12,
    padding: 16,
  },
  agentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  agentIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  agentInfo: {
    flex: 1,
  },
  agentId: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
  },
  agentRole: {
    fontSize: 12,
    color: Colors.textSecondary,
    textTransform: 'capitalize',
  },
  agentStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  agentStatusText: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.white,
  },
  agentMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  agentMetric: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 2,
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
  },
  taskCard: {
    marginBottom: 12,
    padding: 16,
  },
  taskHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  taskPriority: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 12,
  },
  taskPriorityText: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.white,
    textTransform: 'uppercase',
  },
  taskInfo: {
    flex: 1,
  },
  taskType: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
  },
  taskDescription: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  taskProgress: {
    marginBottom: 12,
  },
  taskProgressLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  taskProgressBar: {
    marginBottom: 8,
  },
  taskDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  taskDetail: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  trailCard: {
    marginBottom: 8,
    padding: 12,
  },
  trailHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  trailType: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
  },
  trailStrength: {
    fontSize: 12,
    color: Colors.primary,
  },
  trailDescription: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  trailAge: {
    fontSize: 10,
    color: Colors.textSecondary,
  },
  decisionCard: {
    marginBottom: 8,
    padding: 12,
  },
  decisionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  decisionType: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
  },
  decisionConsensus: {
    fontSize: 12,
    color: Colors.accent,
  },
  decisionDescription: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  decisionParticipants: {
    fontSize: 10,
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
