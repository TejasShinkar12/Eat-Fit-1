export type Sex = 'male' | 'female' | 'other';
export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
export type FitnessGoal = 'lose' | 'maintain' | 'gain';

export interface UserProfile {
  id: string;
  email: string;
  height: number | null;
  weight: number | null;
  age: number | null;
  sex: Sex | null;
  activity_level: ActivityLevel | null;
  fitness_goal: FitnessGoal | null;
  created_at: string;
  updated_at: string;
} 