import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AdminPanel from './components/AdminPanel';
import ActivityCard from './components/ActivityCard';
import { UserConfigProvider } from './context/UserConfigContext';
import { signInAnonymouslyUser } from './services/firebase';
import { healthCheck } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Check backend health
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await healthCheck();
        setBackendStatus(response ? 'connected' : 'disconnected');
      } catch (error) {
        console.error('Backend health check failed:', error);
        setBackendStatus('disconnected');
      }
    };

    checkBackend();
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  // Handle Firebase authentication
  useEffect(() => {
    const authenticateUser = async () => {
      try {
        setAuthLoading(true);
        console.log('Attempting anonymous sign-in...');
        
        const userCredential = await signInAnonymouslyUser();
        if (userCredential && userCredential.user) {
          setCurrentUser(userCredential.user);
          console.log('User authenticated:', userCredential.user.uid);
        } else {
          console.warn('Authentication failed, using fallback');
        }
      } catch (error) {
        console.error('Authentication error:', error);
        // Don't throw - continue with null user
      } finally {
        setAuthLoading(false);
      }
    };

    authenticateUser();
  }, []);

  const getStatusIndicator = () => {
    switch (backendStatus) {
      case 'connected':
        return <span className="text-green-600 font-medium">🟢 Connected</span>;
      case 'disconnected':
        return <span className="text-red-600 font-medium">🔴 Disconnected</span>;
      default:
        return <span className="text-yellow-600 font-medium">🟡 Checking...</span>;
    }
  };

  const renderContent = () => {
    // Show loading screen while auth is in progress
    if (authLoading) {
      return (
        <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-amber-800 text-center mb-4">
            🔧 Initializing Application
          </h2>
          <p className="text-amber-700 text-center mb-4">
            Setting up Firebase authentication and user configuration...
          </p>
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
          </div>
        </div>
      );
    }

    switch (activeTab) {
      case 'admin':
        return <AdminPanel />;
      
      case 'slayer':
        return <ActivityCard activityType="slayer" title="Slayer Calculator" userId={currentUser?.uid} />;
      
      case 'farming':
        return <ActivityCard activityType="farming" title="Herb Farming Calculator" userId={currentUser?.uid} />;
      
      case 'birdhouse':
        return <ActivityCard activityType="birdhouse" title="Birdhouse Run Calculator" userId={currentUser?.uid} />;
        
      case 'gotr':
        return <ActivityCard activityType="gotr" title="Guardians of the Rift Calculator" userId={currentUser?.uid} />;
      
      default:
        return (
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-amber-800 text-center mb-4">
              🎉 Firebase & Drop Tables Restored!
            </h2>
            <p className="text-amber-700 text-center mb-4">
              Firebase is now active and slayer calculations should have proper drop table data.
            </p>
            <div className="mt-6 text-center">
              {currentUser ? (
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <h3 className="font-bold text-green-800 mb-2">✅ Authentication Active</h3>
                  <p className="text-green-700 text-sm mb-2">
                    User ID: {currentUser.uid}
                  </p>
                  <p className="text-green-600 text-sm">
                    Your configurations will be saved to Firebase
                  </p>
                </div>
              ) : (
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <h3 className="font-bold text-yellow-800 mb-2">⚠️ Fallback Mode</h3>
                  <p className="text-yellow-700 text-sm">
                    Using local configuration (changes won't be saved)
                  </p>
                </div>
              )}
              
              <div className="mt-4">
                <p className="text-amber-600 font-medium">✨ Ready to test slayer calculations!</p>
                <p className="text-sm text-gray-600 mt-2">
                  Click the "Slayer" tab to test the restored drop table functionality
                </p>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <UserConfigProvider userId={currentUser?.uid}>
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-100">
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <div className="container mx-auto px-4 py-6">
          {/* Status Bar */}
          <div className="mb-4 text-center text-sm">
            Backend: {getStatusIndicator()}
            <span className="ml-4 text-blue-600">🌐 Port: 3002</span>
            {currentUser && (
              <span className="ml-4 text-green-600">👤 User: {currentUser.uid.slice(-8)}</span>
            )}
          </div>

          {/* Main Content */}
          {renderContent()}
        </div>
      </div>
    </UserConfigProvider>
  );
}

export default App;
