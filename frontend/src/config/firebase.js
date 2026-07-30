import { initializeApp } from "firebase/app";
import {
  getAuth,
  signInWithEmailAndPassword as firebaseSignIn,
  createUserWithEmailAndPassword as firebaseCreateUser,
  GoogleAuthProvider as FirebaseGoogleProvider,
  signInWithPopup as firebaseSignInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Check if the three required Firebase keys are present.
const hasFirebaseConfig = () =>
  !!(
    process.env.REACT_APP_FIREBASE_API_KEY &&
    process.env.REACT_APP_FIREBASE_AUTH_DOMAIN &&
    process.env.REACT_APP_FIREBASE_PROJECT_ID
  );

// Mock auth is only allowed during local development when the developer has
// explicitly opted in via REACT_APP_ALLOW_MOCK_AUTH=true.
// NEVER set this in a deployed / production environment.
const isMockAuthAllowed = () =>
  process.env.NODE_ENV === "development" &&
  process.env.REACT_APP_ALLOW_MOCK_AUTH === "true";

let app = null;
let firebaseAuth = null;
let analytics = null;

if (hasFirebaseConfig()) {
  const firebaseConfig = {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
    storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.REACT_APP_FIREBASE_APP_ID,
    measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
  };

  try {
    app = initializeApp(firebaseConfig);
    analytics = getAnalytics(app);
    firebaseAuth = getAuth(app);
    console.log("✅ Firebase initialized successfully");
  } catch (error) {
    console.error("❌ Firebase initialization failed:", error);
  }
} else if (isMockAuthAllowed()) {
  // DEV-only mock path — only reachable when NODE_ENV=development AND
  // REACT_APP_ALLOW_MOCK_AUTH=true.  Safe to leave a visible console warning.
  console.warn(
    "⚠️  [DEV] Firebase not configured — using mock auth " +
      "(REACT_APP_ALLOW_MOCK_AUTH=true). " +
      "Do NOT use this in a deployed environment."
  );
} else {
  // Production (or any env without explicit opt-in): no silent fake user.
  // Log a clear error so developers deploying to staging/production can see
  // immediately what is missing and fix it before going live.
  console.error(
    "Firebase not configured — authentication is disabled. " +
      "Set REACT_APP_FIREBASE_* env vars. " +
      "See frontend/.env.example for the full list of required keys."
  );
}

// ── Mock implementations (DEV only) ──────────────────────────────────────────

const createMockUser = (email = "mock@example.com") => ({
  email,
  uid: "mock-uid-123",
  displayName: "Mock User",
});

const mockSignInWithEmailAndPassword = async (email, _password) => ({
  user: createMockUser(email),
});

const mockCreateUserWithEmailAndPassword = async (email, _password) => ({
  user: createMockUser(email),
});

const mockSignInWithPopup = async (_provider) => ({
  user: createMockUser("google-mock@example.com"),
});

// onAuthStateChanged immediately signals "not signed in" (null) so that
// UI state is at least consistent in mock mode.
const mockAuth = {
  currentUser: null,
  onAuthStateChanged: (callback) => {
    setTimeout(() => callback(null), 0);
    return () => {};
  },
};

const mockGoogleAuthProvider = class GoogleAuthProvider {
  constructor() {
    this.providerId = "google.com";
  }
};

const mockSignOut = async () => Promise.resolve();

// ── Null / no-op implementations (production with missing config) ─────────────
// These are exported when Firebase is not configured AND mock auth is not
// allowed.  They prevent runtime crashes in components that call auth functions
// but surface a clear "not authenticated" state rather than a fake user.

const nullAuth = {
  currentUser: null,
  onAuthStateChanged: (callback) => {
    setTimeout(() => callback(null), 0);
    return () => {};
  },
};

const nullOp = async () => {
  throw new Error(
    "Authentication is not configured. Set REACT_APP_FIREBASE_* env vars."
  );
};

const NullGoogleAuthProvider = class GoogleAuthProvider {
  constructor() {
    this.providerId = "google.com";
  }
};

// ── Exports ───────────────────────────────────────────────────────────────────

const useMock = !firebaseAuth && isMockAuthAllowed();

export const auth = firebaseAuth ?? (useMock ? mockAuth : nullAuth);

export const signInWithEmailAndPassword = firebaseAuth
  ? firebaseSignIn
  : useMock
  ? mockSignInWithEmailAndPassword
  : nullOp;

export const createUserWithEmailAndPassword = firebaseAuth
  ? firebaseCreateUser
  : useMock
  ? mockCreateUserWithEmailAndPassword
  : nullOp;

export const GoogleAuthProvider = firebaseAuth
  ? FirebaseGoogleProvider
  : useMock
  ? mockGoogleAuthProvider
  : NullGoogleAuthProvider;

export const signInWithPopup = firebaseAuth
  ? firebaseSignInWithPopup
  : useMock
  ? mockSignInWithPopup
  : nullOp;

export const signOut = firebaseAuth ? firebaseSignOut : useMock ? mockSignOut : nullOp;

// True when sign-in can actually succeed.  The UI needs this to avoid offering
// a form whose every button throws: without Firebase keys the exported auth
// functions are nullOp, so a deployment with no auth configured must route
// people to guest access instead of presenting a dead signup screen.
export const isAuthConfigured = Boolean(firebaseAuth) || useMock;

export default app;
