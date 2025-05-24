import React from 'react';

const Navbar = ({ activeTab, setActiveTab }) => {
  // Single activity tabs (existing functionality)
  const singleTabs = [
    { id: 'farming', label: 'Herb Farming', icon: '🌿' },
    { id: 'birdhouse', label: 'Birdhouse Runs', icon: '🏠' },
    { id: 'gotr', label: 'GOTR', icon: '🔮' },
    { id: 'slayer', label: 'Slayer', icon: '⚔️' },
  ];

  // Comparison tabs (new functionality)
  const comparisonTabs = [
    { id: 'compare-farming', label: 'Compare Herbs', icon: '🌿📊' },
    { id: 'compare-birdhouse', label: 'Compare Houses', icon: '🏠📊' },
    { id: 'compare-gotr', label: 'Compare Runes', icon: '🔮📊' },
    { id: 'compare-slayer', label: 'Compare Monsters', icon: '⚔️📊' },
  ];

  const configTab = { id: 'config', label: 'Configuration', icon: '⚙️' };

  return (
    <nav className="bg-gradient-to-r from-amber-600 to-amber-800 shadow-lg mb-6">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-3">
          <div className="flex items-center">
            <h1 className="text-xl lg:text-2xl font-bold text-white mr-4 lg:mr-8">
              💰 OSRS GP/Hour Tracker
            </h1>
          </div>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:block pb-3">
          <div className="space-y-2">
            {/* Single Activities Section */}
            <div className="flex items-center space-x-1">
              <span className="text-amber-200 text-sm font-medium mr-3">Single:</span>
              {singleTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-white text-amber-800 shadow-md'
                      : 'text-amber-100 hover:text-white hover:bg-amber-700'
                  }`}
                >
                  <span className="mr-1">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Comparison Section */}
            <div className="flex items-center space-x-1">
              <span className="text-amber-200 text-sm font-medium mr-3">Compare:</span>
              {comparisonTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-white text-amber-800 shadow-md'
                      : 'text-amber-100 hover:text-white hover:bg-amber-700'
                  }`}
                >
                  <span className="mr-1">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Configuration Section */}
            <div className="flex items-center space-x-1">
              <span className="text-amber-200 text-sm font-medium mr-3">Settings:</span>
              <button
                onClick={() => setActiveTab(configTab.id)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  activeTab === configTab.id
                    ? 'bg-white text-amber-800 shadow-md'
                    : 'text-amber-100 hover:text-white hover:bg-amber-700'
                }`}
              >
                <span className="mr-1">{configTab.icon}</span>
                {configTab.label}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-3">
          <div className="grid grid-cols-2 gap-2">
            {[...singleTabs, ...comparisonTabs, configTab].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white text-amber-800 shadow-md'
                    : 'text-amber-100 hover:text-white hover:bg-amber-700'
                }`}
              >
                <span className="mr-1">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 