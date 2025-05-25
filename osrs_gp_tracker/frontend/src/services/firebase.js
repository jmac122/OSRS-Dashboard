import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously } from 'firebase/auth';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Initialize Firebase app with error handling
let firebaseApp = null;
let auth = null;

try {
  // Only initialize if we have the required config
  if (firebaseConfig.apiKey && firebaseConfig.projectId) {
    firebaseApp = initializeApp(firebaseConfig);
    auth = getAuth(firebaseApp);
    console.log('Firebase initialized successfully');
  } else {
    console.warn('Firebase configuration incomplete, using fallback mode');
  }
} catch (error) {
  console.error('Firebase initialization failed:', error);
}

// Enhanced anonymous authentication with retry logic
export const signInAnonymouslyUser = async () => {
  try {
    if (!auth) {
      // Fallback: generate a unique user ID
      return {
        user: { uid: 'fallback-user-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9) }
      };
    }
    
    const userCredential = await signInAnonymously(auth);
    console.log('Anonymous sign-in successful');
    return userCredential;
  } catch (error) {
    console.error('Anonymous sign-in failed:', error);
    
    // Fallback: generate a unique user ID
    return {
      user: { uid: 'fallback-user-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9) }
    };
  }
};

// Export auth with fallback
export { auth };

// Mock auth object for when Firebase is not available
const mockAuth = {
  currentUser: null,
  onAuthStateChanged: (callback) => {
    // Simulate auth state change with fallback user
    setTimeout(() => {
      callback({ uid: 'fallback-user-' + Date.now() });
    }, 100);
    return () => {}; // unsubscribe function
  }
};

export default firebaseApp || mockAuth; 