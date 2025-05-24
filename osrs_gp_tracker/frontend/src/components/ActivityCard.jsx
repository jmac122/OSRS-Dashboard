import React, { useState, useEffect } from 'react';
import { calculateGpHr } from '../services/api';
import { useUserConfig } from '../context/UserConfigContext';
import GPChart from './GPChart';

const ActivityCard = ({ title, activityType, userId }) => {
  const { userConfig, updateUserConfig } = useUserConfig();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [localParams, setLocalParams] = useState({});

  // Get current activity config
  const activityConfig = userConfig[activityType] || {};

  // Update local params when user config changes
  useEffect(() => {
    setLocalParams(activityConfig);
  }, [activityConfig]);

  // Calculate GP/hour when config changes
  useEffect(() => {
    if (Object.keys(localParams).length > 0) {
      calculateGpHour();
    }
  }, [localParams, userId]);

  const calculateGpHour = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await calculateGpHr(activityType, localParams, userId);
      
      if (response.success) {
        setResult(response.result);
      } else {
        setError(response.error || 'Calculation failed');
      }
    } catch (err) {
      setError(err.message || 'Failed to calculate GP/hour');
    } finally {
      setLoading(false);
    }
  };

  const handleParamChange = async (paramName, value) => {
    const numValue = parseFloat(value) || 0;
    const updatedParams = { ...localParams, [paramName]: numValue };
    
    setLocalParams(updatedParams);
    await updateUserConfig(activityType, { [paramName]: numValue });
  };

  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
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
                value={localParams.num_patches || 9}
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
                value={localParams.avg_yield_per_patch || 8}
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
                value={localParams.growth_time_minutes || 80}
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
                value={localParams.avg_nests_per_run || 10}
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
                value={localParams.avg_value_per_nest || 5000}
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
                value={localParams.run_time_minutes || 5}
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
                value={localParams.cycle_time_minutes || 50}
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
                value={localParams.games_per_hour || 4}
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
                value={localParams.essence_per_game || 150}
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
                value={localParams.avg_rune_value_per_game || 15000}
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
                value={localParams.avg_pearl_value_per_game || 8000}
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
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Monster Name
              </label>
              <input
                type="text"
                value={localParams.monster_name || 'Rune Dragons'}
                onChange={(e) => handleParamChange('monster_name', e.target.value)}
                className="osrs-input w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Kills/Hour
              </label>
              <input
                type="number"
                value={localParams.kills_per_hour || 40}
                onChange={(e) => handleParamChange('kills_per_hour', e.target.value)}
                className="osrs-input w-full"
                min="1"
                max="1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Loot/Kill
              </label>
              <input
                type="number"
                value={localParams.avg_loot_value_per_kill || 37000}
                onChange={(e) => handleParamChange('avg_loot_value_per_kill', e.target.value)}
                className="osrs-input w-full"
                min="100"
                max="1000000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                Supply Cost/Hour
              </label>
              <input
                type="number"
                value={localParams.avg_supply_cost_per_hour || 100000}
                onChange={(e) => handleParamChange('avg_supply_cost_per_hour', e.target.value)}
                className="osrs-input w-full"
                min="0"
                max="1000000"
              />
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
          <div className="text-lg text-amber-700">No data available</div>
        )}
      </div>

      {/* Chart */}
      {result && !result.error && (
        <div className="mb-6">
          <GPChart data={getChartData()} title={`${title} GP/Hour`} />
        </div>
      )}

      {/* Activity-specific inputs */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-amber-800 mb-3">Parameters</h3>
        {renderActivitySpecificInputs()}
      </div>

      {/* Detailed breakdown */}
      {result && !result.error && (
        <div className="bg-amber-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-amber-800 mb-3">Breakdown</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {result.costs && (
              <div>
                <h4 className="font-medium text-amber-700 mb-1">Costs</h4>
                {Object.entries(result.costs).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="capitalize">{key.replace('_', ' ')}:</span>
                    <span>{formatNumber(value)} GP</span>
                  </div>
                ))}
              </div>
            )}
            {result.revenue && (
              <div>
                <h4 className="font-medium text-amber-700 mb-1">Revenue</h4>
                <div className="flex justify-between">
                  <span>Total:</span>
                  <span>{formatNumber(result.revenue)} GP</span>
                </div>
              </div>
            )}
            {result.prices_used && (
              <div className="col-span-2">
                <h4 className="font-medium text-amber-700 mb-1">Current Prices</h4>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(result.prices_used).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-xs">
                      <span className="capitalize">{key}:</span>
                      <span>{formatNumber(value)} GP</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityCard; 