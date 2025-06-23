import React, { useState } from 'react';
import { View, StyleSheet, Text, TextInput, Button, Alert } from 'react-native';
import { StackScreenProps } from '@react-navigation/stack';
import * as api from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { updateCurrentUser } from '../api/user';
import { UserProfile, Sex, ActivityLevel, FitnessGoal } from '../types/user';
import { RootStackParamList } from './SignUpScreen';

const sexOptions: Sex[] = ['male', 'female', 'other'];
const activityOptions: ActivityLevel[] = ['sedentary', 'light', 'moderate', 'active', 'very_active'];
const goalOptions: FitnessGoal[] = ['lose', 'maintain', 'gain'];

type Props = StackScreenProps<RootStackParamList, 'ProfileSetup'>;

const ProfileSetupScreen: React.FC<Props> = ({ route, navigation }) => {
  // Check if params exist (sign-up flow) or not (profile completion flow)
  const signupParams = route?.params;
  const [form, setForm] = useState<Partial<UserProfile>>({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleChange = (field: keyof UserProfile, value: any) => {
    setForm({ ...form, [field]: value });
  };

  const isValid = () => {
    return (
      !!form.height &&
      !!form.weight &&
      !!form.age &&
      !!form.sex &&
      !!form.activity_level &&
      !!form.fitness_goal
    );
  };

  const handleSave = async () => {
    if (!isValid()) {
      Alert.alert('Please fill in all fields.');
      return;
    }
    setLoading(true);
    try {
      if (signupParams) {
        // Sign-up flow
        await api.signup({
          email: signupParams.email,
          password: signupParams.password,
          full_name: signupParams.fullName,
          height: form.height,
          weight: form.weight,
          age: form.age,
          sex: form.sex,
          activity_level: form.activity_level,
          fitness_goal: form.fitness_goal,
        });
        const data = await api.login({ email: signupParams.email, password: signupParams.password });
        await login(data.access_token);
        // Navigation will be handled by AppNavigator
      } else {
        // Profile completion flow (user already exists)
        await updateCurrentUser(form);
        // Optionally, show a success message or navigate
        Alert.alert('Profile updated!');
      }
    } catch (e: any) {
      const message = e.response?.data?.detail || 'Failed to save profile.';
      Alert.alert('Error', message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Set Up Your Fitness Profile</Text>
      <Text style={styles.label}>Height (cm)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={form.height?.toString() || ''}
        onChangeText={v => handleChange('height', parseFloat(v))}
      />
      <Text style={styles.label}>Weight (kg)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={form.weight?.toString() || ''}
        onChangeText={v => handleChange('weight', parseFloat(v))}
      />
      <Text style={styles.label}>Age</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={form.age?.toString() || ''}
        onChangeText={v => handleChange('age', parseInt(v))}
      />
      <Text style={styles.label}>Sex (male/female/other)</Text>
      <TextInput
        style={styles.input}
        value={form.sex || ''}
        onChangeText={v => handleChange('sex', v as Sex)}
      />
      <Text style={styles.label}>Activity Level (sedentary/light/moderate/active/very_active)</Text>
      <TextInput
        style={styles.input}
        value={form.activity_level || ''}
        onChangeText={v => handleChange('activity_level', v as ActivityLevel)}
      />
      <Text style={styles.label}>Fitness Goal (lose/maintain/gain)</Text>
      <TextInput
        style={styles.input}
        value={form.fitness_goal || ''}
        onChangeText={v => handleChange('fitness_goal', v as FitnessGoal)}
      />
      <Button title={loading ? 'Saving...' : 'Save & Continue'} onPress={handleSave} disabled={loading || !isValid()} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center' },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 24, textAlign: 'center' },
  label: { fontWeight: 'bold', marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 4, padding: 8, marginTop: 4 },
});

export default ProfileSetupScreen; 