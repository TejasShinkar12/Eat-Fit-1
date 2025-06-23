import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TextInput, Button, ActivityIndicator, Alert } from 'react-native';
import { getCurrentUser, updateCurrentUser } from '../api/user';
import { UserProfile, Sex, ActivityLevel, FitnessGoal } from '../types/user';

const sexOptions: Sex[] = ['male', 'female', 'other'];
const activityOptions: ActivityLevel[] = ['sedentary', 'light', 'moderate', 'active', 'very_active'];
const goalOptions: FitnessGoal[] = ['lose', 'maintain', 'gain'];

const ProfileScreen = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<Partial<UserProfile>>({});

  useEffect(() => {
    getCurrentUser().then(user => {
      setProfile(user);
      setForm(user);
      setLoading(false);
    });
  }, []);

  const handleChange = (field: keyof UserProfile, value: any) => {
    setForm({ ...form, [field]: value });
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const updated = await updateCurrentUser(form);
      setProfile(updated);
      setEditMode(false);
      setLoading(false);
      Alert.alert('Profile updated!');
    } catch (e) {
      setLoading(false);
      Alert.alert('Error', 'Failed to update profile.');
    }
  };

  if (loading || !profile) return <ActivityIndicator style={{ flex: 1 }} />;

  return (
    <View style={styles.container}>
      {editMode ? (
        <>
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
          <Text style={styles.label}>Sex</Text>
          <TextInput
            style={styles.input}
            value={form.sex || ''}
            onChangeText={v => handleChange('sex', v as Sex)}
            placeholder="male/female/other"
          />
          <Text style={styles.label}>Activity Level</Text>
          <TextInput
            style={styles.input}
            value={form.activity_level || ''}
            onChangeText={v => handleChange('activity_level', v as ActivityLevel)}
            placeholder="sedentary/light/moderate/active/very_active"
          />
          <Text style={styles.label}>Fitness Goal</Text>
          <TextInput
            style={styles.input}
            value={form.fitness_goal || ''}
            onChangeText={v => handleChange('fitness_goal', v as FitnessGoal)}
            placeholder="lose/maintain/gain"
          />
          <Button title="Save" onPress={handleSave} />
          <Button title="Cancel" onPress={() => setEditMode(false)} />
        </>
      ) : (
        <>
          <Text style={styles.label}>Email: {profile.email}</Text>
          <Text style={styles.label}>Height: {profile.height} cm</Text>
          <Text style={styles.label}>Weight: {profile.weight} kg</Text>
          <Text style={styles.label}>Age: {profile.age}</Text>
          <Text style={styles.label}>Sex: {profile.sex}</Text>
          <Text style={styles.label}>Activity Level: {profile.activity_level}</Text>
          <Text style={styles.label}>Fitness Goal: {profile.fitness_goal}</Text>
          <Button title="Edit Profile" onPress={() => setEditMode(true)} />
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24 },
  label: { fontWeight: 'bold', marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 4, padding: 8, marginTop: 4 },
});

export default ProfileScreen; 