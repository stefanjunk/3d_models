import { getApp, getApps, initializeApp, type FirebaseApp, type FirebaseOptions } from "firebase/app";

const firebaseOptions: FirebaseOptions = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

export function hasFirebaseClientConfig(): boolean {
  return Boolean(firebaseOptions.apiKey && firebaseOptions.authDomain && firebaseOptions.projectId && firebaseOptions.appId);
}

export function getFirebaseClientApp(): FirebaseApp | null {
  if (!hasFirebaseClientConfig()) return null;
  return getApps().length ? getApp() : initializeApp(firebaseOptions);
}
