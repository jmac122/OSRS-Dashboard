import React, { useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth, signInAnonymouslyUser } from './services/firebase';
import { UserConfigProvider } from './context/UserConfigContext';
import Navbar from './components/Navbar';
import ActivityCard from './components/ActivityCard';
import ActivityComparison from './components/ActivityComparison';
import ConfigEditor from './components/ConfigEditor';
import { healthCheck } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('farming');
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const result = await healthCheck();
        setBackendStatus(result.firebase_connected ? 'connected' : 'firebase-error');
      } catch (error) {
        setBackendStatus('disconnected');
      }
    };
    checkBackend();
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        signInAnonymouslyUser()
          .then((userCredential) => {
            setUser(userCredential.user);
          })
          .catch((error) => {
            console.error('Authentication failed:', error);
          });
      }
    });

    return () => unsubscribe();
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      // Single Activity Cases (existing functionality)
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

      // Comparison Cases (new functionality)
      case 'compare-farming':
        return (
          <ActivityComparison
            activityType="farming"
            userId={user?.uid}
          />
        );
      case 'compare-birdhouse':
        return (
          <ActivityComparison
            activityType="birdhouse"
            userId={user?.uid}
          />
        );
      case 'compare-gotr':
        return (
          <ActivityComparison
            activityType="gotr"
            userId={user?.uid}
          />
        );
      case 'compare-slayer':
        return (
          <ActivityComparison
            activityType="slayer"
            userId={user?.uid}
          />
        );

      // Configuration Case (existing functionality)
      case 'config':
        return <ConfigEditor userId={user?.uid} />;
      
      default:
        return (
          <div className="osrs-card p-6 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-amber-800 text-center">
              Welcome to OSRS GP/Hour Tracker! 🎉
            </h2>
            <p className="text-amber-700 text-center mt-4">
              Track your Old School RuneScape activities and compare profitability.
            </p>
            <div className="mt-6 text-center">
              <p className="text-gray-600 mb-4">Choose an activity from the navigation above to get started.</p>
              <div className="bg-amber-50 p-4 rounded-lg">
                <h3 className="font-bold text-amber-800 mb-2">New in Phase 1: Comparison Mode!</h3>
                <p className="text-amber-700 text-sm">
                  Use the "Compare" tabs to analyze multiple options side-by-side and find the most profitable activities.
                </p>
              </div>
            </div>
          </div>
        );
    }
  };

  const getStatusIndicator = () => {
    switch (backendStatus) {
      case 'connected':
        return <span className="text-green-600">🟢 Connected</span>;
      case 'firebase-error':
        return <span className="text-yellow-600">🟡 Backend OK, Firebase Issue</span>;
      case 'disconnected':
        return <span className="text-red-600">🔴 Backend Disconnected</span>;
      default:
        return <span className="text-gray-600">⏳ Checking...</span>;
    }
  };

  return (
    <UserConfigProvider>
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-100">
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <div className="container mx-auto px-4 py-6">
          {/* Status Bar */}
          <div className="mb-4 text-center text-sm">
            Backend: {getStatusIndicator()}
            {user && <span className="ml-4 text-gray-600">User: {user.uid.slice(-6)}</span>}
          </div>

          {/* Main Content */}
          {renderContent()}
        </div>
      </div>
    </UserConfigProvider>
  );
}

export default App;
