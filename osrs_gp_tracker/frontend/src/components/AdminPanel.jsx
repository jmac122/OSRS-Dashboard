import React, { useState } from 'react';

const AdminPanel = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [syncStatus, setSyncStatus] = useState('');
  const [isSyncing, setIsSyncing] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    
    try {
      const response = await fetch('http://localhost:5000/api/admin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        setIsAuthenticated(true);
        setUsername('');
        setPassword('');
      } else {
        setLoginError(result.error || 'Login failed');
      }
    } catch (error) {
      setLoginError('Network error during login');
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5000/api/admin/logout', {
        method: 'POST',
        credentials: 'include',
      });
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleWikiSync = async (syncType = 'slayer') => {
    setIsSyncing(true);
    setSyncStatus('Starting wiki sync...');
    
    try {
      const response = await fetch('http://localhost:5000/api/admin/sync_wiki', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ sync_type: syncType }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        setSyncStatus(`✅ Wiki sync completed successfully! 
          Masters synced: ${result.stats?.masters_synced || 0}
          Monsters synced: ${result.stats?.monsters_synced || 0}`);
      } else {
        setSyncStatus(`❌ Wiki sync failed: ${result.error}`);
      }
    } catch (error) {
      setSyncStatus(`❌ Network error during sync: ${error.message}`);
    } finally {
      setIsSyncing(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="osrs-card p-6 max-w-md mx-auto">
        <h2 className="text-2xl font-bold text-amber-800 mb-4">🔐 Admin Login</h2>
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-amber-700 font-semibold mb-2">
              Username:
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="osrs-input w-full"
              required
            />
          </div>
          
          <div>
            <label className="block text-amber-700 font-semibold mb-2">
              Password:
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="osrs-input w-full"
              required
            />
          </div>
          
          {loginError && (
            <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
              {loginError}
            </div>
          )}
          
          <button
            type="submit"
            className="osrs-button w-full bg-amber-600 hover:bg-amber-700"
          >
            Login
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="osrs-card p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-amber-800">⚙️ Admin Panel</h2>
        <button
          onClick={handleLogout}
          className="osrs-button bg-gray-600 hover:bg-gray-700 text-white"
        >
          Logout
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Wiki Sync Section */}
        <div className="bg-amber-50 p-4 rounded-lg">
          <h3 className="text-lg font-bold text-amber-800 mb-3">📖 Wiki Data Sync</h3>
          <p className="text-amber-700 text-sm mb-4">
            Manually sync monster and master data from the OSRS Wiki. This may take several minutes.
          </p>
          
          <button
            onClick={() => handleWikiSync('slayer')}
            disabled={isSyncing}
            className={`osrs-button w-full ${
              isSyncing 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            } text-white`}
          >
            {isSyncing ? '⏳ Syncing...' : '🔄 Sync Slayer Data'}
          </button>
          
          {syncStatus && (
            <div className={`mt-4 p-3 rounded border text-sm whitespace-pre-line ${
              syncStatus.includes('✅') 
                ? 'bg-green-50 border-green-200 text-green-800' 
                : syncStatus.includes('❌')
                ? 'bg-red-50 border-red-200 text-red-800'
                : 'bg-blue-50 border-blue-200 text-blue-800'
            }`}>
              {syncStatus}
            </div>
          )}
        </div>

        {/* System Status Section */}
        <div className="bg-green-50 p-4 rounded-lg">
          <h3 className="text-lg font-bold text-green-800 mb-3">📊 System Status</h3>
          <div className="space-y-2 text-sm">
            <div>
              <span className="font-semibold">Backend:</span>
              <span className="text-green-600 ml-2">🟢 Running</span>
            </div>
            <div>
              <span className="font-semibold">Database:</span>
              <span className="text-green-600 ml-2">🟢 Connected</span>
            </div>
            <div>
              <span className="font-semibold">GE API:</span>
              <span className="text-green-600 ml-2">🟢 Active</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
        <h3 className="text-lg font-bold text-yellow-800 mb-2">⚠️ Important Notes</h3>
        <ul className="text-yellow-700 text-sm space-y-1">
          <li>• Wiki sync should only be run when necessary (e.g., new monsters added)</li>
          <li>• Sync operations are resource-intensive and may slow down the application</li>
          <li>• Regular users should not need to sync data manually</li>
          <li>• Data is automatically cached to improve performance</li>
        </ul>
      </div>
    </div>
  );
};

export default AdminPanel; 