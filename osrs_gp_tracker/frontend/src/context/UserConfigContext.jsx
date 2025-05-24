import React, { createContext, useContext, useState, useEffect } from 'react';
import { getUserConfig, saveUserConfig, getDefaultConfig } from '../services/api';

const UserConfigContext = createContext();

export const useUserConfig = () => {
  const context = useContext(UserConfigContext);
  if (!context) {
    throw new Error('useUserConfig must be used within a UserConfigProvider');
  }
  return context;
};

export const UserConfigProvider = ({ children, userId }) => {
  const [userConfig, setUserConfig] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user configuration on mount or when userId changes
  useEffect(() => {
    const loadUserConfig = async () => {
      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Try to get user config first
        let config = null;
        try {
          const response = await getUserConfig(userId);
          config = response.config;
        } catch (err) {
          console.log('No existing user config found, using defaults');
        }

        // If no user config exists, get default config
        if (!config || Object.keys(config).length === 0) {
          const defaultResponse = await getDefaultConfig();
          config = defaultResponse.config;
        }

        setUserConfig(config || {});
      } catch (err) {
        console.error('Error loading user config:', err);
        setError(err.message);
        // Set empty config as fallback
        setUserConfig({});
      } finally {
        setLoading(false);
      }
    };

    loadUserConfig();
  }, [userId]);

  // Update user configuration
  const updateUserConfig = async (activityType, newParams) => {
    try {
      const updatedConfig = {
        ...userConfig,
        [activityType]: {
          ...userConfig[activityType],
          ...newParams,
        },
      };

      setUserConfig(updatedConfig);

      // Save to backend if userId is available
      if (userId) {
        await saveUserConfig(userId, updatedConfig);
      }
    } catch (err) {
      console.error('Error updating user config:', err);
      setError(err.message);
    }
  };

  // Update entire configuration
  const setFullUserConfig = async (newConfig) => {
    try {
      setUserConfig(newConfig);

      // Save to backend if userId is available
      if (userId) {
        await saveUserConfig(userId, newConfig);
      }
    } catch (err) {
      console.error('Error setting full user config:', err);
      setError(err.message);
    }
  };

  const value = {
    userConfig,
    loading,
    error,
    updateUserConfig,
    setFullUserConfig,
  };

  return (
    <UserConfigContext.Provider value={value}>
      {children}
    </UserConfigContext.Provider>
  );
}; 