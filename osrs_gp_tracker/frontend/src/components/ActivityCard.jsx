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
  const [hasChanges, setHasChanges] = useState(false);

  // Get current activity config
  const activityConfig = userConfig[activityType] || {};

  // Update local params when user config changes
  useEffect(() => {
    setLocalParams(activityConfig);
    setHasChanges(false);
  }, [activityConfig]);

  // Auto-calculate GP/hour when component loads (but not on every change)
  useEffect(() => {
    if (Object.keys(localParams).length > 0 && !hasChanges) {
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
        setHasChanges(false);
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
    const numValue = paramName === 'monster_name' ? value : (parseFloat(value) || 0);
    const updatedParams = { ...localParams, [paramName]: numValue };
    
    setLocalParams(updatedParams);
    setHasChanges(true);
    await updateUserConfig(activityType, { [paramName]: numValue });
  };

  const handleManualCalculate = () => {
    calculateGpHour();
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