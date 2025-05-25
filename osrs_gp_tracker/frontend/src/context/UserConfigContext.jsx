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

// Fallback configuration to prevent crashes
const FALLBACK_CONFIG = {
  slayer: {
    calculation_mode: 'expected',
    slayer_master_id: 'duradel',
    user_slayer_level: 85,
    user_combat_level: 100,
    user_attack_level: 80,
    user_strength_level: 80,
    user_defence_level: 75,
    user_ranged_level: 85,
    user_magic_level: 80
  },
  farming: {
    num_patches: 9,
    avg_yield_per_patch: 8,
    growth_time_minutes: 80
  },
  birdhouse: {
    avg_nests_per_run: 10,
    avg_value_per_nest: 5000,
    run_time_minutes: 5,
    cycle_time_minutes: 50
  },
  gotr: {
    games_per_hour: 4,
    essence_per_game: 150,
    avg_rune_value_per_game: 15000,
    avg_pearl_value_per_game: 8000
  }
};

export const UserConfigProvider = ({ children, userId }) => {
  const [userConfig, setUserConfig] = useState(FALLBACK_CONFIG);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingFallback, setUsingFallback] = useState(false);

  // Load user configuration on mount or when userId changes
  useEffect(() => {
    const loadUserConfig = async () => {
      try {
        setLoading(true);
        setError(null);
        setUsingFallback(false);

        let config = null;

        // Add timeout to prevent hanging
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 10000)
        );

        // If we have a userId, try to get user config first
        if (userId) {
          try {
            console.log('Loading user config for userId:', userId);
            const response = await Promise.race([
              getUserConfig(userId),
              timeoutPromise
            ]);
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
            const defaultResponse = await Promise.race([
              getDefaultConfig(),
              timeoutPromise
            ]);
            config = defaultResponse.config;
            console.log('Default config loaded:', config);
          } catch (err) {
            console.warn('Failed to load default config:', err);
            // Don't throw here, use fallback instead
            config = FALLBACK_CONFIG;
            setUsingFallback(true);
            console.log('Using fallback configuration');
          }
        }

        // Ensure we have a valid config
        if (config && Object.keys(config).length > 0) {
          // Merge with fallback to ensure all required fields exist
          const mergedConfig = {
            ...FALLBACK_CONFIG,
            ...config,
            // Ensure each activity has all required fields
            slayer: { ...FALLBACK_CONFIG.slayer, ...(config.slayer || {}) },
            farming: { ...FALLBACK_CONFIG.farming, ...(config.farming || {}) },
            birdhouse: { ...FALLBACK_CONFIG.birdhouse, ...(config.birdhouse || {}) },
            gotr: { ...FALLBACK_CONFIG.gotr, ...(config.gotr || {}) }
          };
          
          setUserConfig(mergedConfig);
          console.log('Final config set:', mergedConfig);
        } else {
          throw new Error('No configuration data available');
        }
      } catch (err) {
        console.error('Error loading user config:', err);
        setError(err.message);
        // Always fall back to default config to prevent crashes
        setUserConfig(FALLBACK_CONFIG);
        setUsingFallback(true);
        console.log('Using fallback configuration due to error');
      } finally {
        setLoading(false);
      }
    };

    loadUserConfig();
  }, [userId]);

  // Update user configuration with error handling
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
      if (userId && !usingFallback) {
        try {
          await saveUserConfig(userId, updatedConfig);
          console.log('User config saved:', updatedConfig);
        } catch (err) {
          console.warn('Failed to save user config, continuing with local changes:', err);
          // Don't throw error, just log it - local changes still work
        }
      }
    } catch (err) {
      console.error('Error updating user config:', err);
      setError(err.message);
    }
  };

  // Update entire configuration with error handling
  const setFullUserConfig = async (newConfig) => {
    try {
      setUserConfig(newConfig);

      // Save to backend if userId is available
      if (userId && !usingFallback) {
        try {
          await saveUserConfig(userId, newConfig);
          console.log('Full user config saved:', newConfig);
        } catch (err) {
          console.warn('Failed to save full user config, continuing with local changes:', err);
          // Don't throw error, just log it - local changes still work
        }
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
    usingFallback,
    updateUserConfig,
    setFullUserConfig,
  };

  return (
    <UserConfigContext.Provider value={value}>
      {children}
    </UserConfigContext.Provider>
  );
}; 