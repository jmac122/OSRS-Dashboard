import React, { useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth, signInAnonymouslyUser } from './services/firebase';
import { UserConfigProvider } from './context/UserConfigContext';
import Navbar from './components/Navbar';
import ActivityCard from './components/ActivityCard';
import ConfigEditor from './components/ConfigEditor';
import { healthCheck } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('farming');
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState(null);

  // Initialize Firebase Auth
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUser(user);
      } else {
        // Sign in anonymously if no user
        signInAnonymouslyUser()
          .then((user) => {
            setUser(user);
          })
          .catch((error) => {
            console.error('Error signing in anonymously:', error);
          });
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Check backend health
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const status = await healthCheck();
        setBackendStatus(status);
      } catch (error) {
        console.error('Backend health check failed:', error);
        setBackendStatus({ status: 'unhealthy', error: error.message });
      }
    };

    checkBackend();
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'farming':
        return (
          <ActivityCard
            title="🌿 Herb Farming"
            activityType="farming"
            userId={user?.uid}
          />
        );
      case 'birdhouse':
        return (
          <ActivityCard
            title="🏠 Birdhouse Runs"
            activityType="birdhouse"
            userId={user?.uid}
          />
        );
      case 'gotr':
        return (
          <ActivityCard
            title="🔮 Guardians of the Rift"
            activityType="gotr"
            userId={user?.uid}
          />
        );
      case 'slayer':
        return (
          <ActivityCard
            title="⚔️ Slayer"
            activityType="slayer"
            userId={user?.uid}
          />
        );
      case 'config':
        return <ConfigEditor />;
      default:
        return (
          <div className="osrs-card p-6 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-amber-800 text-center">
              Welcome to OSRS GP/Hour Tracker
            </h2>
            <p className="text-amber-700 text-center mt-4">
              Select an activity from the navigation to get started!
            </p>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 flex items-center justify-center">
        <div className="osrs-card p-8">
          <div className="text-center">
            <div className="text-2xl font-bold text-amber-800 mb-4">
              🏰 Loading OSRS GP Tracker...
            </div>
            <div className="text-amber-700">Initializing user session...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100">
      <UserConfigProvider userId={user?.uid}>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        {/* Backend Status Indicator */}
        {backendStatus && (
          <div className="max-w-7xl mx-auto px-4 mb-4">
            <div className={`p-2 rounded-lg text-sm text-center ${
              backendStatus.status === 'healthy' 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              Backend: {backendStatus.status} 
              {backendStatus.firebase_connected !== undefined && 
                ` | Firebase: ${backendStatus.firebase_connected ? 'Connected' : 'Disconnected'}`
              }
              {backendStatus.error && ` | Error: ${backendStatus.error}`}
            </div>
          </div>
        )}

        <main className="max-w-7xl mx-auto px-4 py-6">
          {renderContent()}
        </main>

        {/* Footer */}
        <footer className="bg-amber-800 text-white py-4 mt-12">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="text-sm">
              OSRS GP/Hour Tracker - Built for Old School RuneScape players
            </p>
            <p className="text-xs mt-1 opacity-75">
              User ID: {user?.uid?.substring(0, 8)}... | 
              Prices from OSRS Wiki API | 
              Data saved to Firebase
            </p>
          </div>
        </footer>
      </UserConfigProvider>
    </div>
  );
}

export default App;
