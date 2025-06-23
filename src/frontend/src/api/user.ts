import apiClient from './axiosConfig';
import { UserProfile } from '../types/user';

export async function getCurrentUser(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/users/me');
  return response.data;
}

export async function updateCurrentUser(profile: Partial<UserProfile>): Promise<UserProfile> {
  const response = await apiClient.patch<UserProfile>('/users/me', profile);
  return response.data;
} 