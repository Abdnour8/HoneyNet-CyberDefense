/**
 * HoneyNet Mobile App - Main Component
 * אפליקציית HoneyNet לנייד - רכיב ראשי
 */

import React, { useEffect } from 'react';
import {
  StatusBar,
  StyleSheet,
  View,
  Alert,
  AppState,
  AppStateStatus,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { store } from './store/store';
import MainNavigator from './navigation/MainNavigator';
import { HoneyNetService } from './services/HoneyNetService';
import { NotificationService } from './services/NotificationService';
import { BiometricService } from './services/BiometricService';
import { GamificationService } from './services/GamificationService';
import { BlockchainService } from './services/BlockchainService';
import { SwarmService } from './services/SwarmService';
import { QuantumService } from './services/QuantumService';
import { Colors } from './constants/Colors';

const App: React.FC = () => {
  useEffect(() => {
    initializeApp();
    
    const handleAppStateChange = (nextAppState: AppStateStatus) => {
      if (nextAppState === 'active') {
        // App became active - resume protection
        HoneyNetService.resumeProtection();
      } else if (nextAppState === 'background') {
        // App went to background - continue background protection
        HoneyNetService.enableBackgroundProtection();
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    
    return () => {
      subscription?.remove();
      HoneyNetService.cleanup();
      
      // Cleanup advanced services
      GamificationService.cleanup();
      BlockchainService.cleanup();
      SwarmService.cleanup();
      QuantumService.cleanup();
    };
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize advanced services
      await GamificationService.initialize();
      await BlockchainService.initialize();
      await SwarmService.initialize();
      await QuantumService.initialize();
      // Initialize core services
      await NotificationService.initialize();
      await BiometricService.initialize();
      await HoneyNetService.initialize();
      
      console.log('🚀 HoneyNet Mobile initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize HoneyNet Mobile:', error);
      Alert.alert(
        'שגיאת אתחול',
        'לא ניתן לאתחל את HoneyNet. אנא נסה שוב.',
        [{ text: 'אישור', style: 'default' }]
      );
    }
  };

  return (
    <GestureHandlerRootView style={styles.container}>
      <Provider store={store}>
        <SafeAreaProvider>
          <NavigationContainer>
            <StatusBar
              barStyle="light-content"
              backgroundColor={Colors.primary}
              translucent={false}
            />
            <View style={styles.container}>
              <MainNavigator />
            </View>
          </NavigationContainer>
        </SafeAreaProvider>
      </Provider>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
});

export default App;
