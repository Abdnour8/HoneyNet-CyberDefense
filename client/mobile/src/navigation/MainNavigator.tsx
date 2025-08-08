/**
 * HoneyNet Mobile - Main Navigator
 * ניווט ראשי של אפליקציית HoneyNet
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';

import HomeScreen from '../screens/HomeScreen';
import HoneypotsScreen from '../screens/HoneypotsScreen';
import ThreatsScreen from '../screens/ThreatsScreen';
import NetworkScreen from '../screens/NetworkScreen';
import ProfileScreen from '../screens/ProfileScreen';
import SettingsScreen from '../screens/SettingsScreen';
import ThreatDetailScreen from '../screens/ThreatDetailScreen';
import HoneypotDetailScreen from '../screens/HoneypotDetailScreen';
import { GamificationScreen } from '../screens/GamificationScreen';
import { BlockchainScreen } from '../screens/BlockchainScreen';
import { SwarmScreen } from '../screens/SwarmScreen';
import { QuantumScreen } from '../screens/QuantumScreen';

import { Colors } from '../constants/Colors';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const TabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Home':
              iconName = 'home';
              break;
            case 'Honeypots':
              iconName = 'bug-report';
              break;
            case 'Threats':
              iconName = 'warning';
              break;
            case 'Network':
              iconName = 'public';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            case 'Gamification':
              iconName = 'emoji-events';
              break;
            case 'Blockchain':
              iconName = 'link';
              break;
            case 'Swarm':
              iconName = 'hub';
              break;
            case 'Quantum':
              iconName = 'science';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.textSecondary,
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopColor: Colors.border,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '600',
        },
        headerStyle: {
          backgroundColor: Colors.primary,
        },
        headerTintColor: Colors.white,
        headerTitleStyle: {
          fontWeight: 'bold',
          fontSize: 18,
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: '🛡️ HoneyNet',
          tabBarLabel: 'בית',
        }}
      />
      <Tab.Screen 
        name="Honeypots" 
        component={HoneypotsScreen}
        options={{
          title: '🍯 פיתיונות חכמים',
          tabBarLabel: 'פיתיונות',
        }}
      />
      <Tab.Screen 
        name="Threats" 
        component={ThreatsScreen}
        options={{
          title: '🚨 איומים',
          tabBarLabel: 'איומים',
        }}
      />
      <Tab.Screen 
        name="Network" 
        component={NetworkScreen}
        options={{
          title: '🌐 רשת גלובלית',
          tabBarLabel: 'רשת',
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: '👤 פרופיל',
          tabBarLabel: 'פרופיל',
        }}
      />
      <Tab.Screen 
        name="Gamification" 
        component={GamificationScreen}
        options={{
          title: '🎮 גיימיפיקציה',
          tabBarLabel: 'משחקים',
        }}
      />
      <Tab.Screen 
        name="Blockchain" 
        component={BlockchainScreen}
        options={{
          title: '⛓️ בלוקצ\'יין',
          tabBarLabel: 'בלוקצ\'יין',
        }}
      />
      <Tab.Screen 
        name="Swarm" 
        component={SwarmScreen}
        options={{
          title: '🐝 נחיל חכם',
          tabBarLabel: 'נחיל',
        }}
      />
      <Tab.Screen 
        name="Quantum" 
        component={QuantumScreen}
        options={{
          title: '⚛️ קוונטי',
          tabBarLabel: 'קוונטי',
        }}
      />
    </Tab.Navigator>
  );
};

const MainNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: Colors.primary,
        },
        headerTintColor: Colors.white,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="MainTabs" 
        component={TabNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="ThreatDetail" 
        component={ThreatDetailScreen}
        options={{
          title: 'פרטי איום',
          headerBackTitle: 'חזור',
        }}
      />
      <Stack.Screen 
        name="HoneypotDetail" 
        component={HoneypotDetailScreen}
        options={{
          title: 'פרטי פיתיון',
          headerBackTitle: 'חזור',
        }}
      />
      <Stack.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          title: 'הגדרות',
          headerBackTitle: 'חזור',
        }}
      />
    </Stack.Navigator>
  );
};

export default MainNavigator;
