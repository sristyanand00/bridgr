import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDMGtRK_Il1WBjC12rQvpUVhX0fdYREHbU",
  authDomain: "bridgr-72de1.firebaseapp.com",
  projectId: "bridgr-72de1",
  storageBucket: "bridgr-72de1.firebasestorage.app",
  messagingSenderId: "66063758858",
  appId: "1:66063758858:web:df6dcf86ac9df09a51d1f3",
  measurementId: "G-HBHZ97SH51"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

// Export auth functions
export {
  auth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup
};

export default app;
