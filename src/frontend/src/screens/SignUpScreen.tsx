import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { TextInput, Button, Title } from 'react-native-paper';
import { StackScreenProps } from '@react-navigation/stack';

// Add ProfileSetupScreen to navigation types
export type RootStackParamList = {
  Login: undefined;
  SignUp: undefined;
  ProfileSetup: {
    email: string;
    password: string;
    fullName: string;
  };
};

type Props = StackScreenProps<RootStackParamList, 'SignUp'>;

const SignUpScreen = ({ navigation }: Props) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');

  const handleContinue = () => {
    if (password !== confirmPassword) {
      Alert.alert("Passwords don't match");
      return;
    }
    if (!email || !password || !fullName) {
      Alert.alert('Please fill in all fields.');
      return;
    }
    navigation.navigate('ProfileSetup', { email, password, fullName });
  };

  return (
    <View style={styles.container}>
      <Title style={styles.title}>Sign Up</Title>
      <TextInput
        label="Full Name"
        value={fullName}
        onChangeText={setFullName}
        style={styles.input}
        autoCapitalize="words"
      />
      <TextInput
        label="Email"
        value={email}
        onChangeText={setEmail}
        style={styles.input}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        label="Password"
        value={password}
        onChangeText={setPassword}
        style={styles.input}
        secureTextEntry
      />
      <TextInput
        label="Confirm Password"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        style={styles.input}
        secureTextEntry
      />
      <Button mode="contained" onPress={handleContinue} style={styles.button}>
        Continue
      </Button>
      <Button onPress={() => navigation.navigate('Login')} style={styles.button}>
        Go to Login
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
  },
  title: {
    fontSize: 24,
    marginBottom: 16,
    textAlign: 'center',
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
});

export default SignUpScreen; 