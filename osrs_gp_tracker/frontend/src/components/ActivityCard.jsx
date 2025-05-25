import React, { useState, useEffect } from 'react';
import { calculateGpHr, getSlayerMasters, getSlayerBreakdown } from '../services/api';
import { useUserConfig } from '../context/UserConfigContext';
import GPChart from './GPChart';
import * as api from '../services/api';

const ActivityCard = ({ title, activityType, userId }) => {
  const { userConfig, updateUserConfig, loading: configLoading, error: configError, usingFallback } = useUserConfig();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [localParams, setLocalParams] = useState({});
  const [hasChanges, setHasChanges] = useState(false);
  const [hasInitiallyCalculated, setHasInitiallyCalculated] = useState(false);
  const [slayerMasters, setSlayerMasters] = useState({});
  const [slayerBreakdown, setSlayerBreakdown] = useState(null);
  const [loadingBreakdown, setLoadingBreakdown] = useState(false);
  const [slayerMonsters, setSlayerMonsters] = useState({});

  // Get current activity config
  const activityConfig = userConfig[activityType] || {};

  // Update local params when user config changes
  useEffect(() => {
    setLocalParams(activityConfig);
    setHasChanges(false);
  }, [activityConfig]);

  // Only auto-calculate GP/hour on initial load, not on parameter changes
  useEffect(() => {
    if (Object.keys(localParams).length > 0 && !hasInitiallyCalculated) {
      calculateGpHour();
      setHasInitiallyCalculated(true);
    }
  }, [localParams, userId, hasInitiallyCalculated]);

  // Load Slayer Masters when activity type is slayer
  useEffect(() => {
    if (activityType === 'slayer') {
      const loadSlayerMasters = async () => {
        try {
          const mastersData = await getSlayerMasters();
          if (mastersData.success && mastersData.items) {
            setSlayerMasters(mastersData.items || {});
          }
        } catch (error) {
          console.error('Failed to load Slayer Masters:', error);
        }
      };
      
      const loadSlayerMonsters = async () => {
        try {
          const response = await api.get('/items/slayer?category=monsters');
          if (response.data.success && response.data.items) {
            setSlayerMonsters(response.data.items || {});
          }
        } catch (error) {
          console.error('Failed to load Slayer Monsters:', error);
        }
      };
      
      loadSlayerMasters();
      loadSlayerMonsters();
    }
  }, [activityType]);

  const calculateGpHour = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Convert localParams to numeric values for API call
      const numericParams = {};
      for (const [key, value] of Object.entries(localParams)) {
        if (key === 'monster_name') {
          numericParams[key] = value || 'Unknown Monster';
        } else {
          // Convert to number, use 0 as fallback for empty values during calculation
          numericParams[key] = parseFloat(value) || 0;
        }
      }
      
      const response = await calculateGpHr(activityType, numericParams, userId);
      
      if (response.success) {
        setResult(response.result);
        setHasChanges(false);
        loadSlayerBreakdown();
      } else {
        setError(response.error || 'Calculation failed');
      }
    } catch (err) {
      setError(err.message || 'Failed to calculate GP/hour');
    } finally {
      setLoading(false);
    }
  };

  const loadSlayerBreakdown = async () => {
    if (activityType !== 'slayer' || !localParams.slayer_master_id) return;
    
    try {
      setLoadingBreakdown(true);
      const userLevels = {
        slayer_level: parseInt(localParams.user_slayer_level) || 85,
        combat_level: parseInt(localParams.user_combat_level) || 100,
        attack_level: parseInt(localParams.user_attack_level) || 80,
        strength_level: parseInt(localParams.user_strength_level) || 80,
        defence_level: parseInt(localParams.user_defence_level) || 75,
        ranged_level: parseInt(localParams.user_ranged_level) || 85,
        magic_level: parseInt(localParams.user_magic_level) || 80,
      };
      
      const breakdown = await getSlayerBreakdown(
        localParams.slayer_master_id,
        userLevels,
        userId
      );
      
      if (breakdown.success) {
        setSlayerBreakdown(breakdown.result);
      }
    } catch (error) {
      console.error('Failed to load Slayer breakdown:', error);
    } finally {
      setLoadingBreakdown(false);
    }
  };

  const handleParamChange = async (paramName, value) => {
    // Allow empty values for better UX, don't force to 0 immediately
    const processedValue = paramName === 'monster_name' ? value : value;
    const updatedParams = { ...localParams, [paramName]: processedValue };
    
    setLocalParams(updatedParams);
    setHasChanges(true);
    // Save to user config but don't trigger calculation
    await updateUserConfig(activityType, { [paramName]: processedValue });
    
    // For Slayer, load breakdown when master or key levels change
    if (activityType === 'slayer' && 
        (paramName === 'slayer_master_id' || 
         paramName === 'user_slayer_level' || 
         paramName === 'user_combat_level')) {
      // Use updated params for breakdown
      const tempParams = { ...localParams, [paramName]: processedValue };
      if (tempParams.slayer_master_id) {
        // Small delay to ensure state is updated
        setTimeout(() => loadSlayerBreakdown(), 100);
      }
    }
  };

  // Validation function to check if all required fields have values
  const validateParams = () => {
    const requiredFields = getRequiredFields();
    const emptyFields = [];
    
    // Helper function to get actual value (including defaults) for validation
    const getValidationValue = (paramName) => {
      const value = localParams[paramName];
      if (value !== undefined && value !== null) {
        return value;
      }
      
      // Return appropriate default values for each field
      const defaults = {
        'slayer_master_id': 'spria',
        'user_slayer_level': 85,
        'user_combat_level': 100,
        'user_attack_level': 80,
        'user_strength_level': 80,
        'user_defence_level': 75,
        'user_ranged_level': 85,
        'user_magic_level': 80
      };
      
      return defaults[paramName] || '';
    };
    
    for (const field of requiredFields) {
      const value = getValidationValue(field);
      
      if (field === 'monster_name' || field === 'slayer_master_id') {
        // For text/string fields, just check if it's empty or whitespace
        if (!value || value.toString().trim() === '') {
          emptyFields.push(field);
        }
      } else {
        // For numeric fields, check if it's empty or not a valid number
        if (value === '' || value === null || value === undefined || isNaN(parseFloat(value))) {
          emptyFields.push(field);
        }
      }
    }
    
    return emptyFields;
  };

  // Get required fields based on activity type
  const getRequiredFields = () => {
    switch (activityType) {
      case 'farming':
        return ['num_patches', 'avg_yield_per_patch', 'growth_time_minutes'];
      case 'birdhouse':
        return ['avg_nests_per_run', 'avg_value_per_nest', 'run_time_minutes', 'cycle_time_minutes'];
      case 'gotr':
        return ['games_per_hour', 'essence_per_game', 'avg_rune_value_per_game', 'avg_pearl_value_per_game'];
      case 'slayer':
        return ['slayer_master_id', 'user_slayer_level', 'user_combat_level'];
      default:
        return [];
    }
  };

  const handleManualCalculate = () => {
    // Validate all required fields before calculation
    const emptyFields = validateParams();
    
    if (emptyFields.length > 0) {
      const fieldNames = emptyFields.map(field => 
        field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
      ).join(', ');
      setError(`Please enter values for all required fields: ${fieldNames}`);
      setResult(null);
      return;
    }

    // Clear any previous errors and proceed with calculation
    setError(null);
    calculateGpHour();
  };

  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
  };

  // Helper function to get input value - shows empty string if user cleared it, otherwise shows value or default
  const getInputValue = (paramName, defaultValue) => {
    const value = localParams[paramName];
    // If value exists and isn't empty, show it; if it's empty string (user cleared), show empty; otherwise show default
    if (value !== undefined && value !== null) {
      return value.toString();
    }
    return defaultValue.toString();
  };

  const getChartData = () => {
    if (!result || result.error) return null;
    
    return {
      labels: [title],
      values: [result.gp_hr || 0]
    };
  };

  const renderActivitySpecificInputs = () => {
    switch (activityType) {
      case 'farming':
        return (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Patches
              </label>
              <input
                type="number"
                value={getInputValue('num_patches', 9)}
                onChange={(e) => handleParamChange('num_patches', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="15"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Avg Yield/Patch
              </label>
              <input
                type="number"
                value={getInputValue('avg_yield_per_patch', 8)}
                onChange={(e) => handleParamChange('avg_yield_per_patch', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="20"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Growth Time (min)
              </label>
              <input
                type="number"
                value={getInputValue('growth_time_minutes', 80)}
                onChange={(e) => handleParamChange('growth_time_minutes', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="300"
              />
            </div>
          </div>
        );
      
      case 'birdhouse':
        return (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Nests/Run
              </label>
              <input
                type="number"
                value={getInputValue('avg_nests_per_run', 10)}
                onChange={(e) => handleParamChange('avg_nests_per_run', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="50"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Value/Nest
              </label>
              <input
                type="number"
                value={getInputValue('avg_value_per_nest', 5000)}
                onChange={(e) => handleParamChange('avg_value_per_nest', e.target.value)}
                className="osrs-input w-full"
                min="100"
                max="50000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Run Time (min)
              </label>
              <input
                type="number"
                value={getInputValue('run_time_minutes', 5)}
                onChange={(e) => handleParamChange('run_time_minutes', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="30"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Cycle Time (min)
              </label>
              <input
                type="number"
                value={getInputValue('cycle_time_minutes', 50)}
                onChange={(e) => handleParamChange('cycle_time_minutes', e.target.value)}
                className="osrs-input w-full"
                min="30"
                max="120"
              />
            </div>
          </div>
        );
      
      case 'gotr':
        return (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Games/Hour
              </label>
              <input
                type="number"
                value={getInputValue('games_per_hour', 4)}
                onChange={(e) => handleParamChange('games_per_hour', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="10"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Essence/Game
              </label>
              <input
                type="number"
                value={getInputValue('essence_per_game', 150)}
                onChange={(e) => handleParamChange('essence_per_game', e.target.value)}
                className="osrs-input w-full"
                min="50"
                max="500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Rune Value/Game
              </label>
              <input
                type="number"
                value={getInputValue('avg_rune_value_per_game', 15000)}
                onChange={(e) => handleParamChange('avg_rune_value_per_game', e.target.value)}
                className="osrs-input w-full"
                min="1000"
                max="100000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Pearl Value/Game
              </label>
              <input
                type="number"
                value={getInputValue('avg_pearl_value_per_game', 8000)}
                onChange={(e) => handleParamChange('avg_pearl_value_per_game', e.target.value)}
                className="osrs-input w-full"
                min="1000"
                max="50000"
              />
            </div>
          </div>
        );
      
      case 'slayer':
        return (
          <div className="space-y-8">
            {/* Calculation Mode Selector */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-6 rounded-xl border-2 border-amber-200 shadow-lg">
              <h4 className="text-xl font-bold text-amber-800 mb-4 flex items-center">
                🎯 Calculation Mode
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => handleParamChange('calculation_mode', 'expected')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    getInputValue('calculation_mode', 'expected') === 'expected'
                      ? 'border-amber-500 bg-amber-100 shadow-md'
                      : 'border-gray-300 bg-white hover:border-amber-300'
                  }`}
                >
                  <div className="text-2xl mb-2">📊</div>
                  <div className="font-bold text-amber-800">Expected GP/Hr</div>
                  <div className="text-sm text-gray-600 mt-1">Average across all assignments</div>
                </button>
                <button
                  onClick={() => handleParamChange('calculation_mode', 'specific')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    getInputValue('calculation_mode', 'expected') === 'specific'
                      ? 'border-amber-500 bg-amber-100 shadow-md'
                      : 'border-gray-300 bg-white hover:border-amber-300'
                  }`}
                >
                  <div className="text-2xl mb-2">🎯</div>
                  <div className="font-bold text-amber-800">Specific Monster</div>
                  <div className="text-sm text-gray-600 mt-1">Calculate exact monster</div>
                </button>
                <button
                  onClick={() => handleParamChange('calculation_mode', 'breakdown')}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    getInputValue('calculation_mode', 'expected') === 'breakdown'
                      ? 'border-amber-500 bg-amber-100 shadow-md'
                      : 'border-gray-300 bg-white hover:border-amber-300'
                  }`}
                >
                  <div className="text-2xl mb-2">📋</div>
                  <div className="font-bold text-amber-800">Task Breakdown</div>
                  <div className="text-sm text-gray-600 mt-1">All assignments detailed</div>
                </button>
              </div>
            </div>

            {/* Slayer Master Selection */}
            <div className="bg-white p-6 rounded-xl border-2 border-amber-200 shadow-lg">
              <h4 className="text-xl font-bold text-amber-800 mb-4 flex items-center">
                👑 Slayer Master
              </h4>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-bold text-amber-800 mb-3">
                    Select Your Master
                  </label>
                  <select
                    value={getInputValue('slayer_master_id', 'spria')}
                    onChange={(e) => handleParamChange('slayer_master_id', e.target.value)}
                    className="w-full p-4 text-lg text-gray-800 bg-white border-2 border-amber-300 rounded-lg focus:border-amber-500 focus:ring focus:ring-amber-200"
                  >
                    <option value="spria">Spria (Draynor Village)</option>
                    <option value="turael">Turael (Burthorpe)</option>
                    <option value="mazchna">Mazchna (Canifis)</option>
                    <option value="vannaka">Vannaka (Edgeville Dungeon)</option>
                    <option value="chaeldar">Chaeldar (Zanaris)</option>
                    <option value="nieve">Nieve (Tree Gnome Stronghold)</option>
                    <option value="duradel">Duradel (Shilo Village)</option>
                  </select>
                </div>
                
                {/* Master Info Card */}
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 p-4 rounded-lg border border-amber-200">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-amber-600 font-medium">Combat Req</div>
                      <div className="text-lg font-bold text-amber-800">
                        {slayerMasters[getInputValue('slayer_master_id', 'spria')]?.combat_req || '0'}+
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-amber-600 font-medium">Slayer Req</div>
                      <div className="text-lg font-bold text-amber-800">
                        {slayerMasters[getInputValue('slayer_master_id', 'spria')]?.slayer_req || '0'}+
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-amber-600 font-medium">Location</div>
                      <div className="text-sm font-bold text-amber-800">
                        {slayerMasters[getInputValue('slayer_master_id', 'spria')]?.location || 'Draynor Village'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-amber-600 font-medium">Assignments</div>
                      <div className="text-lg font-bold text-green-600">
                        {Object.keys(slayerMasters[getInputValue('slayer_master_id', 'spria')]?.task_assignments || {}).length || '20+'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Monster Selection (only show for specific mode) */}
            {getInputValue('calculation_mode', 'expected') === 'specific' && (
              <div className="bg-white p-6 rounded-xl border-2 border-green-200 shadow-lg">
                <h4 className="text-xl font-bold text-green-800 mb-4 flex items-center">
                  🐉 Specific Monster
                </h4>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-green-800 mb-3">
                      Choose Monster to Calculate
                    </label>
                    <select
                      value={getInputValue('specific_monster_id', '')}
                      onChange={(e) => handleParamChange('specific_monster_id', e.target.value)}
                      className="w-full p-4 text-lg text-gray-800 bg-white border-2 border-green-300 rounded-lg focus:border-green-500 focus:ring focus:ring-green-200"
                    >
                      <option value="">Select a monster...</option>
                      {Object.keys(slayerMonsters).length > 0 ? (
                        Object.entries(slayerMonsters)
                          .sort(([,a], [,b]) => (a.slayer_level_req || 0) - (b.slayer_level_req || 0))
                          .map(([monsterId, monsterData]) => (
                            <option key={monsterId} value={monsterId}>
                              {monsterData.name} ({monsterData.slayer_level_req || 1}+ Slayer)
                            </option>
                          ))
                      ) : (
                        <>
                          <option value="gargoyles">Gargoyles (75+ Slayer)</option>
                          <option value="abyssal_demons">Abyssal Demons (85+ Slayer)</option>
                          <option value="alchemical_hydra">Alchemical Hydra (95+ Slayer)</option>
                          <option value="dust_devils">Dust Devils (65+ Slayer)</option>
                          <option value="nechryael">Nechryael (80+ Slayer)</option>
                        </>
                      )}
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Your Skill Levels */}
            <div className="bg-white p-6 rounded-xl border-2 border-blue-200 shadow-lg">
              <h4 className="text-xl font-bold text-blue-800 mb-4 flex items-center">
                ⚔️ Your Combat Stats
              </h4>
              
              {/* Primary Stats (Larger) */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border-2 border-purple-200">
                  <label className="block text-sm font-bold text-purple-800 mb-2">
                    🔮 Slayer Level
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_slayer_level', 85)}
                    onChange={(e) => handleParamChange('user_slayer_level', e.target.value)}
                    className="w-full p-3 text-xl font-bold text-center border-2 border-purple-300 rounded-lg focus:border-purple-500 focus:ring focus:ring-purple-200"
                    min="1"
                    max="99"
                  />
                </div>
                <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border-2 border-red-200">
                  <label className="block text-sm font-bold text-red-800 mb-2">
                    ⚔️ Combat Level
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_combat_level', 100)}
                    onChange={(e) => handleParamChange('user_combat_level', e.target.value)}
                    className="w-full p-3 text-xl font-bold text-center border-2 border-red-300 rounded-lg focus:border-red-500 focus:ring focus:ring-red-200"
                    min="3"
                    max="126"
                  />
                </div>
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border-2 border-orange-200">
                  <label className="block text-sm font-bold text-orange-800 mb-2">
                    ⚡ Attack Level
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_attack_level', 80)}
                    onChange={(e) => handleParamChange('user_attack_level', e.target.value)}
                    className="w-full p-3 text-xl font-bold text-center border-2 border-orange-300 rounded-lg focus:border-orange-500 focus:ring focus:ring-orange-200"
                    min="1"
                    max="99"
                  />
                </div>
              </div>

              {/* Secondary Stats (Smaller Grid) */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    💪 Strength
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_strength_level', 80)}
                    onChange={(e) => handleParamChange('user_strength_level', e.target.value)}
                    className="w-full p-2 text-center border border-gray-300 rounded focus:border-blue-500 focus:ring focus:ring-blue-200"
                    min="1"
                    max="99"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    🛡️ Defence
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_defence_level', 75)}
                    onChange={(e) => handleParamChange('user_defence_level', e.target.value)}
                    className="w-full p-2 text-center border border-gray-300 rounded focus:border-blue-500 focus:ring focus:ring-blue-200"
                    min="1"
                    max="99"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    🏹 Ranged
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_ranged_level', 85)}
                    onChange={(e) => handleParamChange('user_ranged_level', e.target.value)}
                    className="w-full p-2 text-center border border-gray-300 rounded focus:border-blue-500 focus:ring focus:ring-blue-200"
                    min="1"
                    max="99"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">
                    🪄 Magic
                  </label>
                  <input
                    type="number"
                    value={getInputValue('user_magic_level', 80)}
                    onChange={(e) => handleParamChange('user_magic_level', e.target.value)}
                    className="w-full p-2 text-center border border-gray-300 rounded focus:border-blue-500 focus:ring focus:ring-blue-200"
                    min="1"
                    max="99"
                  />
                </div>
              </div>
            </div>

            {/* Quick Level Presets - Enhanced */}
            <div className="bg-gradient-to-r from-yellow-50 to-amber-50 p-6 rounded-xl border border-yellow-200 shadow-lg">
              <h5 className="text-lg font-bold text-yellow-800 mb-4 flex items-center">
                ⚡ Quick Stat Presets
              </h5>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => {
                    handleParamChange('user_slayer_level', 70);
                    handleParamChange('user_combat_level', 85);
                    handleParamChange('user_attack_level', 70);
                    handleParamChange('user_strength_level', 70);
                    handleParamChange('user_defence_level', 60);
                    handleParamChange('user_ranged_level', 75);
                    handleParamChange('user_magic_level', 70);
                  }}
                  className="p-4 bg-gradient-to-r from-green-400 to-green-500 hover:from-green-500 hover:to-green-600 text-white rounded-lg shadow-md transition-all transform hover:scale-105"
                >
                  <div className="text-lg font-bold">🌱 Mid-Level</div>
                  <div className="text-sm opacity-90">70s Combat, 70 Slayer</div>
                </button>
                <button
                  onClick={() => {
                    handleParamChange('user_slayer_level', 90);
                    handleParamChange('user_combat_level', 115);
                    handleParamChange('user_attack_level', 90);
                    handleParamChange('user_strength_level', 90);
                    handleParamChange('user_defence_level', 85);
                    handleParamChange('user_ranged_level', 95);
                    handleParamChange('user_magic_level', 85);
                  }}
                  className="p-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg shadow-md transition-all transform hover:scale-105"
                >
                  <div className="text-lg font-bold">🚀 High-Level</div>
                  <div className="text-sm opacity-90">90s Combat, 90 Slayer</div>
                </button>
                <button
                  onClick={() => {
                    handleParamChange('user_slayer_level', 99);
                    handleParamChange('user_combat_level', 126);
                    handleParamChange('user_attack_level', 99);
                    handleParamChange('user_strength_level', 99);
                    handleParamChange('user_defence_level', 99);
                    handleParamChange('user_ranged_level', 99);
                    handleParamChange('user_magic_level', 99);
                  }}
                  className="p-4 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-lg shadow-md transition-all transform hover:scale-105"
                >
                  <div className="text-lg font-bold">👑 Maxed</div>
                  <div className="text-sm opacity-90">All 99s, 126 Combat</div>
                </button>
              </div>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="osrs-card p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-amber-800 mb-4 text-center">
        {title}
      </h2>
      
      {/* Main GP/Hour Display */}
      <div className="text-center mb-6">
        {loading ? (
          <div className="text-lg text-amber-700">Calculating...</div>
        ) : error ? (
          <div className="text-lg text-red-600">Error: {error}</div>
        ) : result && !result.error ? (
          <div>
            <div className="text-4xl font-bold text-osrs-gold mb-2">
              {formatNumber(result.gp_hr)} GP/hr
            </div>
            {result.profit_per_cycle && (
              <div className="text-lg text-amber-700">
                {formatNumber(result.profit_per_cycle)} GP per cycle
              </div>
            )}
          </div>
        ) : (
          <div className="text-lg text-amber-700">Click "Calculate GP/Hour" to get results</div>
        )}
      </div>

      {/* Chart */}
      {result && !result.error && (
        <div className="mb-6">
          <div className="mb-2 text-sm text-gray-600">
            Chart Debug: GP/HR = {result.gp_hr}, Chart Data = {JSON.stringify(getChartData())}
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <GPChart data={getChartData()} title={`${title} GP/Hour`} />
          </div>
        </div>
      )}

      {/* Activity-specific inputs */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-amber-800 mb-3">Parameters</h3>
        {renderActivitySpecificInputs()}
      </div>

      {/* Slayer Breakdown - only show for slayer activity */}
      {activityType === 'slayer' && slayerBreakdown && (
        <div className="mb-8 bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border-2 border-blue-200 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-blue-800 flex items-center">
              📋 Task Assignment Analysis
            </h3>
            {loadingBreakdown && (
              <div className="flex items-center text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                <span className="text-sm font-medium">Loading assignments...</span>
              </div>
            )}
          </div>
          
          {/* Overall Summary - Enhanced */}
          {slayerBreakdown.overall && (
            <div className="mb-6 bg-white p-6 rounded-xl border border-blue-200 shadow-md">
              <h4 className="text-xl font-bold text-blue-800 mb-4 flex items-center">
                📊 Master Summary
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                  <div className="text-green-600 font-bold text-sm mb-1">Expected GP/Hr</div>
                  <div className="text-2xl font-bold text-green-700">{formatNumber(slayerBreakdown.overall.expected_gp_per_hour || 0)}</div>
                  <div className="text-xs text-green-600 mt-1">Weighted Average</div>
                </div>
                <div className="text-center bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                  <div className="text-blue-600 font-bold text-sm mb-1">Avg GP/Task</div>
                  <div className="text-2xl font-bold text-blue-700">{formatNumber(slayerBreakdown.overall.avg_gp_per_task || 0)}</div>
                  <div className="text-xs text-blue-600 mt-1">Per Assignment</div>
                </div>
                <div className="text-center bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                  <div className="text-purple-600 font-bold text-sm mb-1">Tasks/Hour</div>
                  <div className="text-2xl font-bold text-purple-700">{(slayerBreakdown.overall.tasks_per_hour || 0).toFixed(2)}</div>
                  <div className="text-xs text-purple-600 mt-1">Completion Rate</div>
                </div>
                <div className="text-center bg-gradient-to-br from-amber-50 to-amber-100 p-4 rounded-lg border border-amber-200">
                  <div className="text-amber-600 font-bold text-sm mb-1">Available Tasks</div>
                  <div className="text-2xl font-bold text-amber-700">{slayerBreakdown.overall.available_tasks || 0}</div>
                  <div className="text-xs text-amber-600 mt-1">You Can Do</div>
                </div>
              </div>
            </div>
          )}
          
          {/* Task Assignment Grid - Enhanced */}
          {slayerBreakdown.assignments && slayerBreakdown.assignments.length > 0 ? (
            <div>
              <h4 className="text-xl font-bold text-blue-800 mb-4 flex items-center">
                🎯 Monster Assignments
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {slayerBreakdown.assignments
                  .sort((a, b) => (b.gp_per_hour || 0) - (a.gp_per_hour || 0))
                  .map((assignment, index) => (
                  <div key={index} className="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-102">
                    {/* Monster Header */}
                    <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-t-xl border-b">
                      <div className="flex justify-between items-start">
                        <h5 className="font-bold text-gray-800 text-lg">{assignment.monster_name}</h5>
                        <div className="text-right">
                          <div className="text-xs text-gray-500">Assignment Chance</div>
                          <div className="text-lg font-bold text-blue-600">{(assignment.probability * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                      
                      {/* Progress Bar for Assignment Probability */}
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${(assignment.probability * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Monster Stats */}
                    <div className="p-4 space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center bg-green-50 p-3 rounded-lg border border-green-100">
                          <div className="text-xs text-green-600 font-bold mb-1">GP/Hour</div>
                          <div className="text-lg font-bold text-green-700">{formatNumber(assignment.gp_per_hour || 0)}</div>
                        </div>
                        <div className="text-center bg-blue-50 p-3 rounded-lg border border-blue-100">
                          <div className="text-xs text-blue-600 font-bold mb-1">GP/Task</div>
                          <div className="text-lg font-bold text-blue-700">{formatNumber(assignment.gp_per_task || 0)}</div>
                        </div>
                      </div>
                      
                      {/* Requirements & Notes */}
                      {assignment.requirements && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                          <div className="text-xs font-bold text-yellow-700 mb-1">Requirements</div>
                          <div className="text-sm text-yellow-800">{assignment.requirements}</div>
                        </div>
                      )}
                      
                      {/* Profitability Indicator */}
                      <div className="flex items-center justify-center">
                        {(assignment.gp_per_hour || 0) > 500000 ? (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                            🔥 High Profit
                          </span>
                        ) : (assignment.gp_per_hour || 0) > 200000 ? (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                            💎 Good Profit
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-600">
                            📈 Decent Profit
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Top Assignments Summary */}
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-md">
                <h5 className="text-lg font-bold text-gray-800 mb-4">🏆 Top 3 Most Profitable Assignments</h5>
                <div className="space-y-2">
                  {slayerBreakdown.assignments
                    .sort((a, b) => (b.gp_per_hour || 0) - (a.gp_per_hour || 0))
                    .slice(0, 3)
                    .map((assignment, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
                      <div className="flex items-center">
                        <div className="text-2xl mr-3">
                          {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                        </div>
                        <div>
                          <div className="font-bold text-gray-800">{assignment.monster_name}</div>
                          <div className="text-sm text-gray-600">{(assignment.probability * 100).toFixed(1)}% chance</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-700">{formatNumber(assignment.gp_per_hour || 0)}</div>
                        <div className="text-xs text-green-600">GP/hr</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center bg-white p-8 rounded-xl border border-gray-200">
              <div className="text-4xl mb-4">🎯</div>
              <div className="text-xl font-bold text-gray-700 mb-2">
                {loadingBreakdown ? 'Analyzing Task Assignments...' : 'No Assignments Available'}
              </div>
              <div className="text-gray-600">
                {loadingBreakdown 
                  ? 'Please wait while we calculate your optimal task assignments.' 
                  : 'No assignments available for selected master and levels. Try selecting a different master or adjusting your levels.'}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Calculate Button */}
      <div className="text-center mb-6">
        <button
          onClick={handleManualCalculate}
          disabled={loading}
          className={`osrs-button px-8 py-3 text-lg font-bold disabled:opacity-50 ${
            hasChanges ? 'bg-orange-600 hover:bg-orange-700 animate-pulse' : ''
          }`}
        >
          {loading ? 'Calculating...' : hasChanges ? 'Recalculate GP/Hour' : 'Calculate GP/Hour'}
        </button>
        {hasChanges && (
          <div className="text-sm text-amber-600 mt-2">
            Parameters changed - click to recalculate
          </div>
        )}
      </div>

      {/* Detailed breakdown */}
      {result && !result.error && (
        <div className="bg-amber-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-amber-800 mb-3">Breakdown</h3>
          
          {/* Debug info */}
          <div className="mb-4 p-2 bg-blue-50 rounded text-xs text-blue-700">
            <strong>Debug:</strong> result keys: {Object.keys(result).join(', ')} | 
            costs: {result.costs ? 'Yes' : 'No'} | 
            revenue: {result.revenue ? 'Yes' : 'No'} | 
            prices_used: {result.prices_used ? 'Yes' : 'No'}
            <br/>
            <strong>Full result:</strong> {JSON.stringify(result, null, 2)}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {/* Costs Section - Fixed text colors */}
            {result.costs && typeof result.costs === 'object' && Object.keys(result.costs).length > 0 && (
              <div className="bg-white p-3 rounded border">
                <h4 className="font-medium text-amber-700 mb-2">💰 Costs</h4>
                {Object.entries(result.costs).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-1">
                    <span className="capitalize text-gray-700 font-medium">{key.replace(/_/g, ' ')}:</span>
                    <span className="font-medium text-gray-900">{formatNumber(value)} GP</span>
                  </div>
                ))}
              </div>
            )}
            
            <div className="bg-white p-3 rounded border">
              <h4 className="font-medium text-amber-700 mb-2">📈 Revenue & Profit</h4>
              {result.revenue && (
                <div className="flex justify-between py-1">
                  <span className="text-gray-700">Total Revenue:</span>
                  <span className="font-medium text-green-700">{formatNumber(result.revenue)} GP</span>
                </div>
              )}
              {result.profit_per_cycle && (
                <div className="flex justify-between py-1">
                  <span className="text-gray-700">Profit per Cycle:</span>
                  <span className="font-medium text-green-700">{formatNumber(result.profit_per_cycle)} GP</span>
                </div>
              )}
              {result.profit_per_run && (
                <div className="flex justify-between py-1">
                  <span className="text-gray-700">Profit per Run:</span>
                  <span className="font-medium text-green-700">{formatNumber(result.profit_per_run)} GP</span>
                </div>
              )}
              {result.cycle_time_hours && (
                <div className="flex justify-between py-1">
                  <span className="text-gray-700">Cycle Time:</span>
                  <span className="font-medium text-gray-900">{(result.cycle_time_hours * 60).toFixed(1)} min</span>
                </div>
              )}
              {result.gp_hr && (
                <div className="flex justify-between py-1 border-t pt-1">
                  <span className="font-semibold text-gray-800">GP per Hour:</span>
                  <span className="font-bold text-amber-600">{formatNumber(result.gp_hr)} GP</span>
                </div>
              )}
            </div>
          </div>

          {result.prices_used && typeof result.prices_used === 'object' && Object.keys(result.prices_used).length > 0 && (
            <div className="mt-4 bg-white p-3 rounded border">
              <h4 className="font-medium text-amber-700 mb-2">🏪 Current Market Prices</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(result.prices_used).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-xs p-2 bg-gray-50 rounded">
                    <span className="capitalize font-medium text-gray-700">{key.replace(/_/g, ' ')}:</span>
                    <span className="text-amber-600 font-medium">{formatNumber(value)} GP</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Show message if no breakdown data */}
          {(!result.costs || Object.keys(result.costs || {}).length === 0) && 
           !result.revenue && 
           (!result.prices_used || Object.keys(result.prices_used || {}).length === 0) && (
            <div className="text-center text-amber-600 py-4">
              No detailed breakdown available for this calculation.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ActivityCard; 