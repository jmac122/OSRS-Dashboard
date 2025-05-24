import React, { useState, useEffect } from 'react';
import { calculateGpHr } from '../services/api';
import { useUserConfig } from '../context/UserConfigContext';

const ActivityComparison = ({ activityType, userId }) => {
  const { userConfig } = useUserConfig();
  const [availableOptions, setAvailableOptions] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [comparisonResults, setComparisonResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [loadingOptions, setLoadingOptions] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('gp_hr');
  const [sortOrder, setSortOrder] = useState('desc');

  // Activity type mapping for API calls
  const getActivityApiConfig = () => {
    switch (activityType) {
      case 'farming':
        return {
          title: 'Herb Farming Comparison',
          apiActivity: 'farming',
          apiCategory: 'herbs',
          defaultParams: {
            num_patches: 9,
            growth_time_minutes: 80,
            compost_id: 21483
          }
        };
      case 'birdhouse':
        return {
          title: 'Birdhouse Type Comparison',
          apiActivity: 'hunter',
          apiCategory: 'birdhouses',
          defaultParams: {
            seed_id: 5318,
            run_time_minutes: 5,
            cycle_time_minutes: 50,
            avg_value_per_nest: 5000
          }
        };
      case 'gotr':
        return {
          title: 'GOTR Rune Comparison',
          apiActivity: 'runecraft',
          apiCategory: 'gotr_strategies',
          defaultParams: {
            essence_id: 7936,
            games_per_hour: 4,
            essence_per_game: 150,
            avg_pearl_value_per_game: 8000
          }
        };
      case 'slayer':
        return {
          title: 'Slayer Monster Comparison',
          apiActivity: 'slayer',
          apiCategory: 'monsters',
          defaultParams: {}
        };
      default:
        return { title: 'Unknown Activity', apiActivity: null, apiCategory: null, defaultParams: {} };
    }
  };

  const activityConfig = getActivityApiConfig();

  // Load available options from database
  useEffect(() => {
    const loadOptions = async () => {
      if (!activityConfig.apiActivity || !activityConfig.apiCategory) {
        setError('Invalid activity type');
        setLoadingOptions(false);
        return;
      }

      setLoadingOptions(true);
      setError(null);

      try {
        const response = await fetch(
          `http://localhost:5000/api/items/${activityConfig.apiActivity}?category=${activityConfig.apiCategory}`
        );

        if (!response.ok) {
          throw new Error(`Failed to load options: ${response.status}`);
        }

        const data = await response.json();
        const items = data.items || {};

        // Transform database items into option format
        const options = Object.entries(items).map(([itemId, itemData]) => ({
          id: itemId,
          name: itemData.name,
          data: itemData,
          // Include relevant fields for each activity type
          ...(activityType === 'farming' && {
            seed_id: itemData.seed_id,
            herb_id: itemData.herb_id,
            growth_time: itemData.growth_time_minutes,
            default_yield: itemData.default_yield,
            level_req: itemData.farming_level_req
          }),
          ...(activityType === 'birdhouse' && {
            log_id: itemData.log_id,
            hunter_req: itemData.hunter_req,
            avg_nests: itemData.avg_nests_per_run,
            exp_per_birdhouse: itemData.exp_per_birdhouse
          }),
          ...(activityType === 'gotr' && {
            rune_id: itemData.rune_id,
            avg_runes_per_game: itemData.avg_runes_per_game,
            points_req: itemData.points_req,
            level_req: itemData.runecraft_level_req
          }),
          ...(activityType === 'slayer' && {
            avg_loot: itemData.avg_loot_value_per_kill,
            kills_per_hour: itemData.kills_per_hour,
            supply_cost: itemData.avg_supply_cost_per_hour,
            slayer_req: itemData.slayer_level_req,
            combat_level: itemData.combat_level
          })
        }));

        // Sort options by level requirement or name
        const sortedOptions = options.sort((a, b) => {
          const levelA = a.level_req || a.hunter_req || a.slayer_req || 0;
          const levelB = b.level_req || b.hunter_req || b.slayer_req || 0;
          return levelA - levelB || a.name.localeCompare(b.name);
        });

        setAvailableOptions(sortedOptions);

        // Auto-select first 2-3 options
        const autoSelected = sortedOptions.slice(0, Math.min(3, sortedOptions.length)).map(opt => opt.id);
        setSelectedOptions(autoSelected);

      } catch (err) {
        console.error('Error loading options:', err);
        setError(`Failed to load ${activityType} options: ${err.message}`);
      } finally {
        setLoadingOptions(false);
      }
    };

    loadOptions();
  }, [activityType, activityConfig.apiActivity, activityConfig.apiCategory]);

  // Calculate comparisons when selections change
  useEffect(() => {
    if (selectedOptions.length > 0 && availableOptions.length > 0) {
      calculateComparisons();
    }
  }, [selectedOptions, availableOptions]);

  const calculateComparisons = async () => {
    setLoading(true);
    setError(null);
    const results = {};

    try {
      for (const optionId of selectedOptions) {
        const option = availableOptions.find(opt => opt.id === optionId);
        if (!option) continue;

        const params = buildParamsForOption(option);
        const result = await calculateGpHr(activityType, params, userId);
        
        if (result.success) {
          results[optionId] = {
            ...result.result,
            option_name: option.name,
            option_data: option.data,
            option_meta: {
              level_req: option.level_req || option.hunter_req || option.slayer_req,
              wiki_url: option.data.wiki_url
            }
          };
        } else {
          results[optionId] = {
            error: result.error,
            option_name: option.name,
            gp_hr: 0
          };
        }
      }

      setComparisonResults(results);
    } catch (err) {
      setError(err.message || 'Failed to calculate comparisons');
    } finally {
      setLoading(false);
    }
  };

  const buildParamsForOption = (option) => {
    const baseParams = { ...activityConfig.defaultParams };

    switch (activityType) {
      case 'farming':
        return {
          ...baseParams,
          seed_id: option.seed_id,
          herb_id: option.herb_id,
          avg_yield_per_patch: option.default_yield,
          growth_time_minutes: option.growth_time
        };

      case 'birdhouse':
        return {
          ...baseParams,
          log_id: option.log_id,
          avg_nests_per_run: option.avg_nests
        };

      case 'gotr':
        return {
          ...baseParams,
          primary_rune_id: option.rune_id,
          avg_rune_value_per_game: 0, // Will be calculated based on current prices
          estimated_runes_per_game: option.avg_runes_per_game
        };

      case 'slayer':
        return {
          monster_name: option.name,
          kills_per_hour: option.kills_per_hour,
          avg_loot_value_per_kill: option.avg_loot,
          avg_supply_cost_per_hour: option.supply_cost
        };

      default:
        return baseParams;
    }
  };

  const handleOptionToggle = (optionId) => {
    setSelectedOptions(prev => {
      if (prev.includes(optionId)) {
        return prev.filter(id => id !== optionId);
      } else {
        return [...prev, optionId];
      }
    });
  };

  const getSortedResults = () => {
    const entries = Object.entries(comparisonResults);
    return entries.sort((a, b) => {
      const [, resultA] = a;
      const [, resultB] = b;
      
      let valueA = resultA[sortBy] || 0;
      let valueB = resultB[sortBy] || 0;
      
      if (sortOrder === 'desc') {
        return valueB - valueA;
      } else {
        return valueA - valueB;
      }
    });
  };

  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
  };

  const getBestOption = () => {
    const sorted = getSortedResults();
    return sorted.length > 0 ? sorted[0] : null;
  };

  // Loading state for options
  if (loadingOptions) {
    return (
      <div className="osrs-card p-6 max-w-6xl mx-auto">
        <h2 className="text-2xl font-bold text-amber-800 mb-4 text-center">
          {activityConfig.title}
        </h2>
        <div className="text-center py-8">
          <div className="text-lg text-amber-700">Loading available options...</div>
          <div className="text-sm text-gray-600 mt-2">Fetching data from database</div>
        </div>
      </div>
    );
  }

  return (
    <div className="osrs-card p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-amber-800 mb-4 text-center">
        {activityConfig.title}
      </h2>

      {/* Database Status Badge */}
      <div className="mb-4 text-center">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          📊 Database-Powered • {availableOptions.length} Options Available
        </span>
      </div>

      {/* Option Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-amber-800 mb-3">
          Select Options to Compare ({selectedOptions.length}/{availableOptions.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {availableOptions.map((option) => {
            const levelReq = option.level_req || option.hunter_req || option.slayer_req;
            return (
              <label key={option.id} className="flex items-start space-x-3 cursor-pointer p-3 border rounded-lg hover:bg-amber-50">
                <input
                  type="checkbox"
                  checked={selectedOptions.includes(option.id)}
                  onChange={() => handleOptionToggle(option.id)}
                  className="mt-1 rounded border-amber-300 text-amber-600 focus:ring-amber-500"
                />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900">{option.name}</div>
                  {levelReq && (
                    <div className="text-sm text-gray-600">
                      Level {levelReq} required
                    </div>
                  )}
                  {option.data.description && (
                    <div className="text-xs text-gray-500 mt-1">
                      {option.data.description}
                    </div>
                  )}
                </div>
              </label>
            );
          })}
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-amber-800">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="osrs-input text-sm"
          >
            <option value="gp_hr">GP/Hour</option>
            <option value="profit_per_cycle">Profit per Cycle</option>
          </select>
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            className="osrs-input text-sm"
          >
            <option value="desc">Highest First</option>
            <option value="asc">Lowest First</option>
          </select>
        </div>
        
        <button
          onClick={calculateComparisons}
          disabled={loading || selectedOptions.length === 0}
          className="osrs-button px-6 py-2 disabled:opacity-50"
        >
          {loading ? 'Calculating...' : 'Refresh Comparison'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          Error: {error}
        </div>
      )}

      {/* Best Option Highlight */}
      {!loading && !error && getBestOption() && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 rounded-lg">
          <h3 className="text-lg font-semibold text-green-800 mb-2">🏆 Best Option</h3>
          <div className="text-green-700">
            <strong>{getBestOption()[1].option_name}</strong> - {formatNumber(getBestOption()[1].gp_hr)} GP/hour
            {getBestOption()[1].option_meta?.level_req && (
              <span className="text-sm ml-2">(Level {getBestOption()[1].option_meta.level_req})</span>
            )}
          </div>
        </div>
      )}

      {/* Results Table */}
      {!loading && Object.keys(comparisonResults).length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full bg-white rounded-lg border">
            <thead className="bg-amber-50">
              <tr>
                <th className="px-4 py-3 text-left text-amber-800 font-semibold">Option</th>
                <th className="px-4 py-3 text-right text-amber-800 font-semibold">GP/Hour</th>
                <th className="px-4 py-3 text-right text-amber-800 font-semibold">Profit/Cycle</th>
                <th className="px-4 py-3 text-center text-amber-800 font-semibold">Level</th>
                <th className="px-4 py-3 text-right text-amber-800 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {getSortedResults().map(([optionId, result], index) => (
                <tr key={optionId} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{result.option_name}</div>
                    {result.option_meta?.wiki_url && (
                      <a 
                        href={result.option_meta.wiki_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline"
                      >
                        View on Wiki →
                      </a>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right font-bold text-amber-600">
                    {result.error ? 'Error' : `${formatNumber(result.gp_hr)} GP`}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-700">
                    {result.profit_per_cycle ? `${formatNumber(result.profit_per_cycle)} GP` : '-'}
                  </td>
                  <td className="px-4 py-3 text-center text-gray-600">
                    {result.option_meta?.level_req || '-'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {result.error ? (
                      <span className="text-red-600 text-sm">❌ Error</span>
                    ) : index === 0 ? (
                      <span className="text-green-600 text-sm">👑 Best</span>
                    ) : (
                      <span className="text-gray-500 text-sm">✓ OK</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-8">
          <div className="text-lg text-amber-700">Calculating comparisons...</div>
          <div className="text-sm text-gray-600 mt-2">Fetching current market prices for each option</div>
        </div>
      )}

      {/* Empty State */}
      {!loading && selectedOptions.length === 0 && (
        <div className="text-center py-8 text-gray-600">
          Select at least one option to compare profitability
        </div>
      )}

      {/* No Options Available */}
      {!loadingOptions && availableOptions.length === 0 && (
        <div className="text-center py-8 text-gray-600">
          <div className="text-lg mb-2">No options available</div>
          <div className="text-sm">Database may not be populated for this activity type</div>
        </div>
      )}
    </div>
  );
};

export default ActivityComparison; 