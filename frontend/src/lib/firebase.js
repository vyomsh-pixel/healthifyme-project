// Firebase Client Initialization & Google Sign-In Provider
const DEFAULT_FIREBASE_CONFIG = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyD8xs71Khb3Hax9Ia4fNZ97DvtR6Mszk-E",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "healthio-13cb9.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "healthio-13cb9",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "healthio-13cb9.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "180803807220",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:180803807220:web:0b445f7d4c6b53480cbba1",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-1QPENHT1NJ"
};


export function getFirebaseApp() {
  if (typeof window === "undefined" || typeof window.firebase === "undefined") {
    return null;
  }
  try {
    if (!window.firebase.apps || !window.firebase.apps.length) {
      window.firebase.initializeApp(DEFAULT_FIREBASE_CONFIG);
    }
    return window.firebase;
  } catch (err) {
    console.warn("Firebase initialization notice:", err);
    return window.firebase || null;
  }
}

export async function signInWithGooglePopup() {
  const fb = getFirebaseApp();
  if (!fb || !fb.auth) {
    throw new Error("Firebase Authentication SDK is loading or unavailable in this environment.");
  }

  const provider = new fb.auth.GoogleAuthProvider();
  try {
    const result = await fb.auth().signInWithPopup(provider);
    const user = result.user;
    const idToken = await user.getIdToken();

    return {
      idToken,
      google_id: user.uid,
      email: user.email,
      display_name: user.displayName || user.email.split("@")[0]
    };
  } catch (err) {
    if (err.code === "auth/unauthorized-domain") {
      throw new Error(`Domain (${window.location.hostname}) is not authorized in Firebase Console. Add '${window.location.hostname}' to Firebase Authorized Domains.`);
    }
    if (err.code === "auth/popup-closed-by-user") {
      throw new Error("Sign-in popup was closed before completing.");
    }
    if (err.code === "auth/cancelled-popup-request") {
      throw new Error("Only one popup request is allowed at a time.");
    }
    throw err;
  }
}
