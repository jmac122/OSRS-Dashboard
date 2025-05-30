import React, { useState } from 'react';
import { useUserConfig } from '../context/UserConfigContext';

const ConfigEditor = () => {
  const { userConfig, setFullUserConfig, loading, error } = useUserConfig();
  const [localConfig, setLocalConfig] = useState(userConfig || {});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Update local config when userConfig changes
  React.useEffect(() => {
    if (userConfig && Object.keys(userConfig).length > 0) {
      setLocalConfig(userConfig);
    }
  }, [userConfig]);

  const handleConfigChange = (activityType, paramName, value) => {
    const updatedConfig = {
      ...localConfig,
      [activityType]: {
        ...localConfig[activityType],
        [paramName]: paramName === 'monster_name' ? value : (parseFloat(value) || 0),
      },
    };
    setLocalConfig(updatedConfig);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage('');
      
      await setFullUserConfig(localConfig);
      setMessage('Configuration saved successfully!');
      
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error saving configuration: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setLocalConfig(userConfig || {});
    setMessage('Configuration reset to last saved state');
    setTimeout(() => setMessage(''), 3000);
  };

  if (loading) {
    return (
      <div className="osrs-card p-6 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-amber-800 mb-6 text-center">
          ⚙️ Configuration Editor
        </h2>
        <div className="text-center text-amber-700">Loading configuration...</div>
        <div className="text-center text-sm text-amber-600 mt-2">
          This may take a few moments while we fetch your settings...
        </div>
      </div>
    );
  }

  const renderActivityConfig = (activityType, config, title) => {
    // Ensure config exists
    const activityConfig = config || {};
    
    if (Object.keys(activityConfig).length === 0) {
      return (
        <div key={activityType} className="bg-amber-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-amber-800 mb-3">{title}</h3>
          <div className="text-amber-600 text-center py-4">
            No configuration available for {title}
          </div>
        </div>
      );
    }

    return (
      <div key={activityType} className="bg-amber-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-amber-800 mb-3">{title}</h3>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(activityConfig).map(([key, value]) => (
            <div key={key}>
              <label className="block text-sm font-medium text-amber-800 mb-1">
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </label>
              {key === 'monster_name' ? (
                <input
                  type="text"
                  value={value || ''}
                  onChange={(e) => handleConfigChange(activityType, key, e.target.value)}
                  className="osrs-input w-full"
                />
              ) : (
                <input
                  type="number"
                  value={value || 0}
                  onChange={(e) => handleConfigChange(activityType, key, e.target.value)}
                  className="osrs-input w-full"
                  step={key.includes('yield') || key.includes('games') ? '0.1' : '1'}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="osrs-card p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold text-amber-800 mb-6 text-center">
        ⚙️ Configuration Editor
      </h2>

      {/* Error Display */}
      {error && (
        <div className="p-3 rounded-lg mb-4 text-center bg-red-100 text-red-700 border border-red-300">
          <strong>Configuration Error:</strong> {error}
        </div>
      )}

      {/* Message Display */}
      {message && (
        <div className={`p-3 rounded-lg mb-4 text-center ${
          message.includes('Error') 
            ? 'bg-red-100 text-red-700 border border-red-300' 
            : 'bg-green-100 text-green-700 border border-green-300'
        }`}>
          {message}
        </div>
      )}

      {/* Debug information at top for troubleshooting */}
      <div className="mb-6 p-3 bg-blue-50 rounded text-sm text-blue-700 border border-blue-200">
        <strong>Status:</strong> 
        Loading: {loading ? 'Yes' : 'No'} | 
        Error: {error ? 'Yes' : 'No'} | 
        UserConfig Keys: {Object.keys(userConfig || {}).join(', ') || 'None'} | 
        LocalConfig Keys: {Object.keys(localConfig || {}).join(', ') || 'None'}
      </div>

      {/* Show configuration even if partially loaded */}
      {(Object.keys(localConfig).length > 0 || Object.keys(userConfig).length > 0) ? (
        <>
          <div className="space-y-6">
            {renderActivityConfig('farming', localConfig.farming, '🌿 Herb Farming')}
            {renderActivityConfig('birdhouse', localConfig.birdhouse, '🏠 Birdhouse Runs')}
            {renderActivityConfig('gotr', localConfig.gotr, '🔮 Guardians of the Rift')}
            {renderActivityConfig('slayer', localConfig.slayer, '⚔️ Slayer')}
          </div>

          <div className="flex justify-center space-x-4 mt-6">
            <button
              onClick={handleSave}
              disabled={saving}
              className="osrs-button px-6 py-2 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
            <button
              onClick={handleReset}
              className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded border-2 border-gray-700 transition-all duration-200"
            >
              Reset
            </button>
          </div>
        </>
      ) : (
        <div className="text-center">
          <div className="text-amber-700 mb-4">
            Configuration not loaded yet. This might be because:
          </div>
          <ul className="text-left text-amber-600 mb-4 max-w-md mx-auto">
            <li>• Backend is still loading default configuration</li>
            <li>• Network connectivity issue</li>
            <li>• User authentication is in progress</li>
            <li>• API endpoint not responding</li>
          </ul>
          <button 
            onClick={() => window.location.reload()} 
            className="osrs-button px-4 py-2"
          >
            Refresh Page
          </button>
        </div>
      )}

      <div className="mt-6 p-4 bg-amber-100 rounded-lg">
        <h3 className="font-semibold text-amber-800 mb-2">Configuration Tips:</h3>
        <ul className="text-sm text-amber-700 space-y-1">
          <li>• Changes are automatically saved when you modify individual activity parameters</li>
          <li>• Use this editor to make bulk changes or fine-tune all settings at once</li>
          <li>• Item IDs are automatically handled - focus on quantities and rates</li>
          <li>• Your configuration is saved to your user profile and persists across sessions</li>
        </ul>
      </div>
    </div>
  );
};

export default ConfigEditor; 