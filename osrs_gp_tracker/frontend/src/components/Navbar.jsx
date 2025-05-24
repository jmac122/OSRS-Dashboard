import React from 'react';

const Navbar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'farming', label: 'Herb Farming', icon: '🌿' },
    { id: 'birdhouse', label: 'Birdhouse Runs', icon: '🏠' },
    { id: 'gotr', label: 'GOTR', icon: '🔮' },
    { id: 'slayer', label: 'Slayer', icon: '⚔️' },
    { id: 'config', label: 'Configuration', icon: '⚙️' },
  ];

  return (
    <nav className="bg-gradient-to-r from-amber-600 to-amber-800 shadow-lg mb-6">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white mr-8">
              💰 OSRS GP/Hour Tracker
            </h1>
          </div>
          
          <div className="flex space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'bg-white text-amber-800 shadow-md'
                    : 'text-white hover:bg-amber-700'
                }`}
              >
                <span>{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 