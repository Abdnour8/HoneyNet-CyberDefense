/**
 * HoneyNet Mobile - Home Screen
 * מסך הבית של אפליקציית HoneyNet
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Animated,
  RefreshControl,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

import { Colors } from '../constants/Colors';
import { HoneyNetService } from '../services/HoneyNetService';
import { updateProtectionStatus, updateStatistics } from '../store/slices/appSlice';
import { RootState } from '../store/store';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend?: 'up' | 'down' | 'stable';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend }) => {
  const scaleAnim = new Animated.Value(1);

  const handlePress = () => {
    Animated.sequence([
      Animated.timing(scaleAnim, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  };

  return (
    <Animated.View style={[styles.statCard, { transform: [{ scale: scaleAnim }] }]}>
      <TouchableOpacity onPress={handlePress} activeOpacity={0.8}>
        <View style={styles.statCardContent}>
          <View style={[styles.statIcon, { backgroundColor: color }]}>
            <Icon name={icon} size={24} color={Colors.white} />
          </View>
          <View style={styles.statInfo}>
            <Text style={styles.statValue}>{value}</Text>
            <Text style={styles.statTitle}>{title}</Text>
            {trend && (
              <View style={styles.trendContainer}>
                <Icon 
                  name={trend === 'up' ? 'trending-up' : trend === 'down' ? 'trending-down' : 'trending-flat'} 
                  size={16} 
                  color={trend === 'up' ? Colors.success : trend === 'down' ? Colors.error : Colors.textSecondary} 
                />
              </View>
            )}
          </View>
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
};

const HomeScreen: React.FC = () => {
  const dispatch = useDispatch();
  const { isProtectionActive, statistics, lastUpdate } = useSelector((state: RootState) => state.app);
  const [refreshing, setRefreshing] = useState(false);
  const [pulseAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    loadInitialData();
    startPulseAnimation();
    
    const interval = setInterval(() => {
      updateData();
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const loadInitialData = async () => {
    try {
      const status = await HoneyNetService.getProtectionStatus();
      const stats = await HoneyNetService.getStatistics();
      
      dispatch(updateProtectionStatus(status));
      dispatch(updateStatistics(stats));
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const updateData = async () => {
    try {
      const stats = await HoneyNetService.getStatistics();
      dispatch(updateStatistics(stats));
    } catch (error) {
      console.error('Error updating data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadInitialData();
    setRefreshing(false);
  };

  const toggleProtection = async () => {
    try {
      if (isProtectionActive) {
        await HoneyNetService.stopProtection();
        Alert.alert('הגנה הופסקה', 'HoneyNet הופסק בהצלחה');
      } else {
        await HoneyNetService.startProtection();
        Alert.alert('הגנה הופעלה', 'HoneyNet פעיל ומגן עליך!');
      }
      
      const newStatus = await HoneyNetService.getProtectionStatus();
      dispatch(updateProtectionStatus(newStatus));
    } catch (error) {
      Alert.alert('שגיאה', 'לא ניתן לשנות את מצב ההגנה');
    }
  };

  const simulateAttack = async () => {
    Alert.alert(
      'סימולציית התקפה',
      'האם אתה בטוח שברצונך לדמות התקפת סייבר?',
      [
        { text: 'ביטול', style: 'cancel' },
        { 
          text: 'כן, דמה התקפה', 
          style: 'destructive',
          onPress: async () => {
            try {
              await HoneyNetService.simulateAttack();
              Alert.alert('התקפה נחסמה!', 'HoneyNet זיהה וחסם את ההתקפה המדומה בהצלחה! 🛡️');
            } catch (error) {
              Alert.alert('שגיאה', 'לא ניתן לדמות התקפה');
            }
          }
        }
      ]
    );
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Protection Status Card */}
      <LinearGradient
        colors={isProtectionActive ? [Colors.success, Colors.successDark] : [Colors.error, Colors.errorDark]}
        style={styles.statusCard}
      >
        <View style={styles.statusContent}>
          <Animated.View style={[styles.statusIcon, { transform: [{ scale: pulseAnim }] }]}>
            <Icon 
              name={isProtectionActive ? 'shield' : 'warning'} 
              size={48} 
              color={Colors.white} 
            />
          </Animated.View>
          <Text style={styles.statusTitle}>
            {isProtectionActive ? '🟢 מוגן' : '🔴 לא מוגן'}
          </Text>
          <Text style={styles.statusSubtitle}>
            {isProtectionActive 
              ? 'HoneyNet פעיל ומגן עליך בזמן אמת'
              : 'הפעל את HoneyNet להגנה מלאה'
            }
          </Text>
          <TouchableOpacity 
            style={[styles.toggleButton, { backgroundColor: isProtectionActive ? Colors.white : Colors.primary }]}
            onPress={toggleProtection}
          >
            <Text style={[styles.toggleButtonText, { color: isProtectionActive ? Colors.success : Colors.white }]}>
              {isProtectionActive ? 'הפסק הגנה' : 'הפעל הגנה'}
            </Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>

      {/* Statistics Grid */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>📊 סטטיסטיקות בזמן אמת</Text>
        
        <View style={styles.statsGrid}>
          <StatCard
            title="איומים זוהו"
            value={statistics.threatsDetected}
            icon="warning"
            color={Colors.warning}
            trend="stable"
          />
          <StatCard
            title="התקפות נחסמו"
            value={statistics.attacksBlocked}
            icon="block"
            color={Colors.error}
            trend="down"
          />
          <StatCard
            title="פיתיונות פעילים"
            value={statistics.activeHoneypots}
            icon="bug-report"
            color={Colors.primary}
            trend="up"
          />
          <StatCard
            title="רשת גלובלית"
            value="1.2M+"
            icon="public"
            color={Colors.info}
            trend="up"
          />
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.sectionTitle}>⚡ פעולות מהירות</Text>
        
        <TouchableOpacity style={styles.actionButton} onPress={simulateAttack}>
          <Icon name="security" size={24} color={Colors.warning} />
          <Text style={styles.actionButtonText}>דמה התקפת סייבר</Text>
          <Icon name="chevron-right" size={24} color={Colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="assessment" size={24} color={Colors.info} />
          <Text style={styles.actionButtonText}>דוח בטיחות</Text>
          <Icon name="chevron-right" size={24} color={Colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="school" size={24} color={Colors.success} />
          <Text style={styles.actionButtonText}>מדריכי אבטחה</Text>
          <Icon name="chevron-right" size={24} color={Colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* Recent Activity */}
      <View style={styles.activityContainer}>
        <Text style={styles.sectionTitle}>🕒 פעילות אחרונה</Text>
        
        <View style={styles.activityItem}>
          <Icon name="check-circle" size={20} color={Colors.success} />
          <Text style={styles.activityText}>פיתיון חדש נוצר בהצלחה</Text>
          <Text style={styles.activityTime}>לפני 5 דקות</Text>
        </View>

        <View style={styles.activityItem}>
          <Icon name="public" size={20} color={Colors.info} />
          <Text style={styles.activityText}>התחברות לרשת הגלובלית</Text>
          <Text style={styles.activityTime}>לפני 12 דקות</Text>
        </View>

        <View style={styles.activityItem}>
          <Icon name="update" size={20} color={Colors.primary} />
          <Text style={styles.activityText}>עדכון מסד נתוני איומים</Text>
          <Text style={styles.activityTime}>לפני 23 דקות</Text>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          עדכון אחרון: {lastUpdate ? new Date(lastUpdate).toLocaleTimeString('he-IL') : 'לא זמין'}
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  statusCard: {
    margin: 16,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
  },
  statusContent: {
    alignItems: 'center',
  },
  statusIcon: {
    marginBottom: 16,
  },
  statusTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: Colors.white,
    marginBottom: 8,
  },
  statusSubtitle: {
    fontSize: 16,
    color: Colors.white,
    textAlign: 'center',
    marginBottom: 20,
    opacity: 0.9,
  },
  toggleButton: {
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 25,
  },
  toggleButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  statsContainer: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.text,
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: Colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  statInfo: {
    flex: 1,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: Colors.text,
  },
  statTitle: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  trendContainer: {
    marginTop: 4,
  },
  actionsContainer: {
    margin: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 16,
    color: Colors.text,
    marginLeft: 12,
  },
  activityContainer: {
    margin: 16,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  activityText: {
    flex: 1,
    fontSize: 14,
    color: Colors.text,
    marginLeft: 12,
  },
  activityTime: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  footer: {
    alignItems: 'center',
    padding: 16,
  },
  footerText: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
});

export default HomeScreen;
