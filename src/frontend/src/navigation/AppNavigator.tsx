import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { ActivityIndicator, View } from 'react-native';

import LoginScreen from '../screens/LoginScreen';
import SignUpScreen from '../screens/SignUpScreen';
import ProfileSetupScreen from '../screens/ProfileSetupScreen';
import BottomTabNavigator from './BottomTabNavigator';
import { useAuth } from '../contexts/AuthContext';
import { getCurrentUser } from '../api/user';
import { UserProfile } from '../types/user';

const Stack = createStackNavigator();

const isProfileComplete = (profile: UserProfile | null) => {
  return !!(
    profile &&
    profile.height &&
    profile.weight &&
    profile.age &&
    profile.sex &&
    profile.activity_level &&
    profile.fitness_goal
  );
};

const AppNavigator = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      setProfileLoading(true);
      getCurrentUser()
        .then(setProfile)
        .finally(() => setProfileLoading(false));
    } else {
      setProfile(null);
      setProfileLoading(false);
    }
  }, [isAuthenticated]);

  if (isLoading || (isAuthenticated && profileLoading)) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="SignUp" component={SignUpScreen} />
            <Stack.Screen name="ProfileSetup" component={ProfileSetupScreen} />
          </>
        ) : !isProfileComplete(profile) ? (
          <Stack.Screen name="ProfileSetup" component={ProfileSetupScreen} />
        ) : (
          <Stack.Screen name="Main" component={BottomTabNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator; 