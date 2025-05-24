import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const getGePrice = async (itemId) => {
  try {
    const response = await api.get(`/ge_price/${itemId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching GE price:', error);
    throw error;
  }
};

export const calculateGpHr = async (activityType, params, userId = null) => {
  try {
    const response = await api.post('/calculate_gp_hr', {
      activity_type: activityType,
      params,
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    console.error('Error calculating GP/hr:', error);
    throw error;
  }
};

export const getUserConfig = async (userId) => {
  try {
    const response = await api.get(`/user_config/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user config:', error);
    throw error;
  }
};

export const saveUserConfig = async (userId, config) => {
  try {
    const response = await api.post(`/user_config/${userId}`, { config });
    return response.data;
  } catch (error) {
    console.error('Error saving user config:', error);
    throw error;
  }
};

export const getDefaultConfig = async () => {
  try {
    const response = await api.get('/default_config');
    return response.data;
  } catch (error) {
    console.error('Error fetching default config:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export const getSlayerMasters = async () => {
  try {
    const response = await api.get('/items/slayer');
    return response.data;
  } catch (error) {
    console.error('Error fetching Slayer Masters:', error);
    throw error;
  }
};

export const getSlayerBreakdown = async (slayerMasterId, userLevels, userId = null) => {
  try {
    const response = await api.post('/api/slayer/breakdown', {
      slayer_master_id: slayerMasterId,
      user_levels: userLevels,
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching Slayer breakdown:', error);
    throw error;
  }
}; 