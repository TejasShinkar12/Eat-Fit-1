import apiClient from './axiosConfig';
import { LoginCredentials, SignUpData } from '../types/auth';

export const login = async (credentials: LoginCredentials) => {
  const form = new URLSearchParams();
  form.append('username', credentials.email);
  form.append('password', credentials.password);

  const response = await apiClient.post('/auth/login', form, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const signup = async (userData: SignUpData) => {
  const response = await apiClient.post('/users/', userData);
  return response.data;
}; 