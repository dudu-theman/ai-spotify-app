// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// import { getAnalytics } from "firebase/analytics";


const API_KEY =  import.meta.env.VITE_API_KEY;
const AUTH_DOMAIN = import.meta.env.VITE_AUTH_DOMAIN;
const PROJECT_ID = import.meta.env.VITE_PROJECT_ID;
const STORAGE_BUCKET = import.meta.env.VITE_STORAGE_BUCKET;
const SENDER_ID = import.meta.env.VITE_SENDER_ID;
const APP_ID = import.meta.env.VITE_APP_ID;
const MEASUREMENT_ID = import.meta.env.VITE_MEASUREMENT_ID;
console.log(import.meta.env.VITE_TEST);

console.log(import.meta.env);
console.log(import.meta.env.VITE_BASE_URL)

// Paste your config object here
const firebaseConfig = {
  apiKey: API_KEY,
  authDomain: AUTH_DOMAIN,
  projectId: PROJECT_ID,
  storageBucket: STORAGE_BUCKET,
  messagingSenderId: SENDER_ID,
  appId: APP_ID,
  measurementId: MEASUREMENT_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);


export const auth = getAuth(app);
export default app;
