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
      try {
        setLoading(true);
        setError(null);

        let config = null;

        // If we have a userId, try to get user config first
        if (userId) {
          try {
            console.log('Loading user config for userId:', userId);
            const response = await getUserConfig(userId);
            config = response.config;
            console.log('User config loaded:', config);
          } catch (err) {
            console.log('No existing user config found, will use defaults:', err.message);
          }
        }

        // If no user config exists or is empty, get default config
        if (!config || Object.keys(config).length === 0) {
          console.log('Loading default configuration...');
          try {
            const defaultResponse = await getDefaultConfig();
            config = defaultResponse.config;
            console.log('Default config loaded:', config);
          } catch (err) {
            console.error('Failed to load default config:', err);
            throw err;
          }
        }

        // Ensure we have a valid config
        if (config && Object.keys(config).length > 0) {
          setUserConfig(config);
          console.log('Final config set:', config);
        } else {
          throw new Error('No configuration data available');
        }
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
        console.log('User config saved:', updatedConfig);
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
        console.log('Full user config saved:', newConfig);
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