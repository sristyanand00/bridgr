import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword as firebaseSignIn, createUserWithEmailAndPassword as firebaseCreateUser, GoogleAuthProvider as FirebaseGoogleProvider, signInWithPopup as firebaseSignInWithPopup } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Check if Firebase credentials are available
const hasFirebaseConfig = () => {
  return !!(process.env.REACT_APP_FIREBASE_API_KEY && 
           process.env.REACT_APP_FIREBASE_AUTH_DOMAIN &&
           process.env.REACT_APP_FIREBASE_PROJECT_ID);
};

let app = null;
let firebaseAuth = null;
let analytics = null;

if (hasFirebaseConfig()) {
  // Real Firebase configuration
  const firebaseConfig = {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
    storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.REACT_APP_FIREBASE_APP_ID,
    measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID
  };

  try {
    app = initializeApp(firebaseConfig);
    analytics = getAnalytics(app);
    firebaseAuth = getAuth(app);
    console.log("✅ Firebase initialized successfully");
  } catch (error) {
    console.error("❌ Firebase initialization failed:", error);
  }
} else {
  console.log("⚠️ Firebase credentials not found, using mock implementation");
}

// Mock implementations for when Firebase is not configured
const createMockUser = (email = "mock@example.com") => ({
  email,
  uid: "mock-uid-123",
  displayName: "Mock User"
});

const mockSignInWithEmailAndPassword = async (email, password) => {
  return { user: createMockUser(email) };
};

const mockCreateUserWithEmailAndPassword = async (email, password) => {
  return { user: createMockUser(email) };
};

const mockSignInWithPopup = async (provider) => {
  return { user: createMockUser("google-mock@example.com") };
};

const mockAuth = {
  currentUser: null,
  onAuthStateChanged: (callback) => {
    // Immediately call callback with null user (not signed in)
    setTimeout(() => callback(null), 0);
    return () => {}; // Unsubscribe function
  }
};

const mockGoogleAuthProvider = class GoogleAuthProvider {
  constructor() {
    this.providerId = "google.com";
  }
};

// Export real Firebase if available, otherwise mock
export const auth = firebaseAuth || mockAuth;
export const signInWithEmailAndPassword = firebaseAuth ? firebaseSignIn : mockSignInWithEmailAndPassword;
export const createUserWithEmailAndPassword = firebaseAuth ? firebaseCreateUser : mockCreateUserWithEmailAndPassword;
export const GoogleAuthProvider = firebaseAuth ? FirebaseGoogleProvider : mockGoogleAuthProvider;
export const signInWithPopup = firebaseAuth ? firebaseSignInWithPopup : mockSignInWithPopup;

export default app;
