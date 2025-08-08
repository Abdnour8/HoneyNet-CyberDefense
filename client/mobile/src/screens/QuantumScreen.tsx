/**
 * Quantum Security Screen for HoneyNet Mobile
 * מסך אבטחה קוונטית לאפליקציית HoneyNet לנייד
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

import { 
  QuantumService, 
  QuantumHoneypot, 
  QuantumKey, 
  QuantumAttackSignature,
  QuantumStats 
} from '../services/QuantumService';
import { Colors } from '../constants/Colors';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';

export const QuantumScreen: React.FC = () => {
  const [quantumStats, setQuantumStats] = useState<QuantumStats | null>(null);
  const [honeypots, setHoneypots] = useState<QuantumHoneypot[]>([]);
  const [quantumKeys, setQuantumKeys] = useState<QuantumKey[]>([]);
  const [attackSignatures, setAttackSignatures] = useState<QuantumAttackSignature[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'honeypots' | 'keys' | 'attacks'>('overview');

  useFocusEffect(
    useCallback(() => {
      loadQuantumData();
    }, [])
  );

  const loadQuantumData = async () => {
    try {
      setLoading(true);
      
      const [stats, honeypotsData, keys, signatures] = await Promise.all([
        QuantumService.getQuantumStats(),
        QuantumService.getQuantumHoneypots(),
        QuantumService.getQuantumKeys(),
        QuantumService.getAttackSignatures()
      ]);

      setQuantumStats(stats);
      setHoneypots(honeypotsData);
      setQuantumKeys(keys);
      setAttackSignatures(signatures);
    } catch (error) {
      console.error('Error loading quantum data:', error);
      Alert.alert('Error', 'Failed to load quantum security data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadQuantumData();
    setRefreshing(false);
  };

  const handleRotateKeys = async () => {
    Alert.alert(
      'Rotate Quantum Keys',
      'This will generate new quantum keys and invalidate old ones. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Rotate', 
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await QuantumService.rotateQuantumKeys();
              if (success) {
                Alert.alert('Success', 'Quantum keys rotated successfully');
                await loadQuantumData();
              } else {
                Alert.alert('Error', 'Failed to rotate quantum keys');
              }
            } catch (error) {
              Alert.alert('Error', 'Failed to rotate quantum keys');
            }
          }
        }
      ]
    );
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
    if (!quantumStats) return null;

    return (
      <View>
        {/* Quantum Status */}
        <Card style={styles.statusCard}>
          <View style={styles.statusHeader}>
            <Icon name="atom" size={32} color={Colors.primary} />
            <View style={styles.statusInfo}>
              <Text style={styles.statusTitle}>Quantum Security Status</Text>
              <Text style={styles.statusSubtitle}>
                {quantumStats.isQuantumReady ? 'Quantum-Ready' : 'Classical Mode'}
              </Text>
            </View>
            <View style={[styles.quantumIndicator, { 
              backgroundColor: quantumStats.isQuantumReady ? Colors.success : Colors.warning 
            }]} />
          </View>
        </Card>

        {/* Security Stats */}
        <Card style={styles.statsCard}>
          <Text style={styles.cardTitle}>🔐 Security Statistics</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{quantumStats.activeHoneypots}</Text>
              <Text style={styles.statLabel}>Quantum Honeypots</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{quantumStats.quantumKeys}</Text>
              <Text style={styles.statLabel}>Quantum Keys</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{quantumStats.attacksDetected}</Text>
              <Text style={styles.statLabel}>Attacks Detected</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{quantumStats.quantumAttacks}</Text>
              <Text style={styles.statLabel}>Quantum Attacks</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{(quantumStats.entanglementStrength * 100).toFixed(1)}%</Text>
              <Text style={styles.statLabel}>Entanglement</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{(quantumStats.coherenceTime / 1000).toFixed(1)}s</Text>
              <Text style={styles.statLabel}>Coherence Time</Text>
            </View>
          </View>
        </Card>

        {/* Quantum States */}
        <Card style={styles.quantumCard}>
          <Text style={styles.cardTitle}>⚛️ Quantum States</Text>
          
          <View style={styles.quantumStates}>
            <View style={styles.quantumState}>
              <Icon name="circle-outline" size={24} color={Colors.primary} />
              <Text style={styles.quantumStateLabel}>Superposition</Text>
              <Text style={styles.quantumStateValue}>
                {quantumStats.superpositionStates} qubits
              </Text>
            </View>
            
            <View style={styles.quantumState}>
              <Icon name="link" size={24} color={Colors.accent} />
              <Text style={styles.quantumStateLabel}>Entanglement</Text>
              <Text style={styles.quantumStateValue}>
                {quantumStats.entangledPairs} pairs
              </Text>
            </View>
          </View>

          <View style={styles.quantumMetric}>
            <Text style={styles.quantumMetricLabel}>Quantum Advantage Score</Text>
            <View style={styles.quantumScore}>
              <Text style={styles.quantumScoreNumber}>{quantumStats.quantumAdvantage}</Text>
              <Text style={styles.quantumScoreUnit}>/100</Text>
            </View>
            <ProgressBar 
              progress={quantumStats.quantumAdvantage / 100} 
              color={Colors.primary}
              style={styles.quantumProgress}
            />
          </View>
        </Card>

        {/* Quick Actions */}
        <Card style={styles.actionsCard}>
          <Text style={styles.cardTitle}>⚡ Quantum Actions</Text>
          
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={handleRotateKeys}
          >
            <Icon name="key-change" size={24} color={Colors.primary} />
            <Text style={styles.actionButtonText}>Rotate Quantum Keys</Text>
            <Icon name="chevron-right" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.actionButton}
            onPress={() => Alert.alert('Quantum Scan', 'Quantum vulnerability scan initiated')}
          >
            <Icon name="radar" size={24} color={Colors.success} />
            <Text style={styles.actionButtonText}>Quantum Vulnerability Scan</Text>
            <Icon name="chevron-right" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>
        </Card>
      </View>
    );
  };

  const renderHoneypotItem = ({ item }: { item: QuantumHoneypot }) => (
    <Card style={styles.honeypotCard}>
      <View style={styles.honeypotHeader}>
        <View style={[styles.honeypotIcon, { backgroundColor: getQuantumStateColor(item.quantumState) }]}>
          <Icon name="hexagon" size={20} color={Colors.white} />
        </View>
        <View style={styles.honeypotInfo}>
          <Text style={styles.honeypotId}>Honeypot {item.honeypotId.substring(0, 8)}</Text>
          <Text style={styles.honeypotState}>{item.quantumState}</Text>
        </View>
        <View style={[styles.honeypotStatus, { 
          backgroundColor: item.isActive ? Colors.success : Colors.error 
        }]}>
          <Text style={styles.honeypotStatusText}>
            {item.isActive ? 'Active' : 'Inactive'}
          </Text>
        </View>
      </View>
      
      <View style={styles.honeypotMetrics}>
        <View style={styles.honeypotMetric}>
          <Text style={styles.metricLabel}>Entanglement</Text>
          <Text style={styles.metricValue}>{(item.entanglementLevel * 100).toFixed(0)}%</Text>
        </View>
        <View style={styles.honeypotMetric}>
          <Text style={styles.metricLabel}>Interactions</Text>
          <Text style={styles.metricValue}>{item.interactions}</Text>
        </View>
        <View style={styles.honeypotMetric}>
          <Text style={styles.metricLabel}>Fidelity</Text>
          <Text style={styles.metricValue}>{item.fidelity.toFixed(2)}</Text>
        </View>
      </View>
    </Card>
  );

  const renderHoneypots = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>🍯 Quantum Honeypots</Text>
      
      {honeypots.length > 0 ? (
        <FlatList
          data={honeypots}
          renderItem={renderHoneypotItem}
          keyExtractor={(item) => item.honeypotId}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="hexagon-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No quantum honeypots</Text>
          <Text style={styles.emptySubtext}>Deploy quantum honeypots to enhance security</Text>
        </Card>
      )}
    </View>
  );

  const renderKeyItem = ({ item }: { item: QuantumKey }) => (
    <Card style={styles.keyCard}>
      <View style={styles.keyHeader}>
        <View style={[styles.keyIcon, { backgroundColor: getKeyTypeColor(item.keyType) }]}>
          <Icon name="key" size={20} color={Colors.white} />
        </View>
        <View style={styles.keyInfo}>
          <Text style={styles.keyId}>Key {item.keyId.substring(0, 12)}</Text>
          <Text style={styles.keyType}>{item.keyType}</Text>
        </View>
        <View style={styles.keyStrength}>
          <Text style={styles.keyStrengthText}>{item.keyStrength}-bit</Text>
        </View>
      </View>
      
      <View style={styles.keyDetails}>
        <Text style={styles.keyDetail}>
          Created: {new Date(item.createdAt).toLocaleDateString()}
        </Text>
        <Text style={styles.keyDetail}>
          Expires: {new Date(item.expiresAt).toLocaleDateString()}
        </Text>
        <Text style={[styles.keyDetail, { color: item.isActive ? Colors.success : Colors.error }]}>
          Status: {item.isActive ? 'Active' : 'Inactive'}
        </Text>
      </View>
    </Card>
  );

  const renderKeys = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>🔑 Quantum Keys</Text>
      
      {quantumKeys.length > 0 ? (
        <FlatList
          data={quantumKeys}
          renderItem={renderKeyItem}
          keyExtractor={(item) => item.keyId}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="key-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No quantum keys</Text>
          <Text style={styles.emptySubtext}>Generate quantum keys for secure communication</Text>
        </Card>
      )}
    </View>
  );

  const renderAttackItem = ({ item }: { item: QuantumAttackSignature }) => (
    <Card style={styles.attackCard}>
      <View style={styles.attackHeader}>
        <View style={[styles.attackSeverity, { backgroundColor: getSeverityColor(item.severity) }]}>
          <Text style={styles.attackSeverityText}>{item.severity}</Text>
        </View>
        <View style={styles.attackInfo}>
          <Text style={styles.attackType}>{item.attackType}</Text>
          <Text style={styles.attackDescription}>{item.description}</Text>
        </View>
      </View>
      
      <View style={styles.attackDetails}>
        <Text style={styles.attackDetail}>
          Detected: {new Date(item.detectedAt).toLocaleString()}
        </Text>
        <Text style={styles.attackDetail}>
          Confidence: {(item.confidence * 100).toFixed(0)}%
        </Text>
        <Text style={styles.attackDetail}>
          Quantum Signature: {item.quantumSignature.substring(0, 16)}...
        </Text>
      </View>
    </Card>
  );

  const renderAttacks = () => (
    <View style={styles.tabContent}>
      <Text style={styles.sectionTitle}>⚠️ Quantum Attack Signatures</Text>
      
      {attackSignatures.length > 0 ? (
        <FlatList
          data={attackSignatures}
          renderItem={renderAttackItem}
          keyExtractor={(item) => item.signatureId}
          showsVerticalScrollIndicator={false}
          scrollEnabled={false}
        />
      ) : (
        <Card style={styles.emptyCard}>
          <Icon name="shield-alert-outline" size={48} color={Colors.textSecondary} />
          <Text style={styles.emptyText}>No quantum attacks detected</Text>
          <Text style={styles.emptySubtext}>Your quantum defenses are working</Text>
        </Card>
      )}
    </View>
  );

  const getQuantumStateColor = (state: string) => {
    switch (state) {
      case 'superposition': return Colors.primary;
      case 'entangled': return Colors.accent;
      case 'collapsed': return Colors.warning;
      default: return Colors.textSecondary;
    }
  };

  const getKeyTypeColor = (keyType: string) => {
    switch (keyType) {
      case 'quantum': return Colors.primary;
      case 'post-quantum': return Colors.success;
      case 'hybrid': return Colors.accent;
      default: return Colors.textSecondary;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return Colors.error;
      case 'high': return Colors.warning;
      case 'medium': return Colors.primary;
      case 'low': return Colors.success;
      default: return Colors.textSecondary;
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner />
        <Text style={styles.loadingText}>Loading quantum security data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview', 'atom')}
        {renderTabButton('honeypots', 'Honeypots', 'hexagon')}
        {renderTabButton('keys', 'Keys', 'key')}
        {renderTabButton('attacks', 'Attacks', 'shield-alert')}
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'honeypots' && renderHoneypots()}
        {activeTab === 'keys' && renderKeys()}
        {activeTab === 'attacks' && renderAttacks()}
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
  quantumIndicator: {
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
  quantumCard: {
    marginBottom: 16,
    padding: 16,
  },
  quantumStates: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  quantumState: {
    alignItems: 'center',
  },
  quantumStateLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 8,
    marginBottom: 4,
  },
  quantumStateValue: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
  },
  quantumMetric: {
    marginTop: 16,
  },
  quantumMetricLabel: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 8,
  },
  quantumScore: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  quantumScoreNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: Colors.primary,
  },
  quantumScoreUnit: {
    fontSize: 16,
    color: Colors.textSecondary,
    marginLeft: 4,
  },
  quantumProgress: {
    marginBottom: 16,
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
  honeypotCard: {
    marginBottom: 12,
    padding: 16,
  },
  honeypotHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  honeypotIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  honeypotInfo: {
    flex: 1,
  },
  honeypotId: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
  },
  honeypotState: {
    fontSize: 12,
    color: Colors.textSecondary,
    textTransform: 'capitalize',
  },
  honeypotStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  honeypotStatusText: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.white,
  },
  honeypotMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  honeypotMetric: {
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
  keyCard: {
    marginBottom: 12,
    padding: 16,
  },
  keyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  keyIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  keyInfo: {
    flex: 1,
  },
  keyId: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
    fontFamily: 'monospace',
  },
  keyType: {
    fontSize: 12,
    color: Colors.textSecondary,
    textTransform: 'capitalize',
  },
  keyStrength: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: Colors.primary + '20',
    borderRadius: 4,
  },
  keyStrengthText: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.primary,
  },
  keyDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
  },
  keyDetail: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  attackCard: {
    marginBottom: 12,
    padding: 16,
  },
  attackHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  attackSeverity: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 12,
  },
  attackSeverityText: {
    fontSize: 12,
    fontWeight: '500',
    color: Colors.white,
    textTransform: 'uppercase',
  },
  attackInfo: {
    flex: 1,
  },
  attackType: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.text,
    marginBottom: 2,
  },
  attackDescription: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  attackDetails: {
    marginTop: 8,
  },
  attackDetail: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginBottom: 2,
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
