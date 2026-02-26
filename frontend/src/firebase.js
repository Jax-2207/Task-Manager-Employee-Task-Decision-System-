// Firebase client configuration.
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyA58FG9RLRa1z0lWtCf_bmLSDIsng17gAw",
    authDomain: "fsassignintern.firebaseapp.com",
    projectId: "fsassignintern",
    storageBucket: "fsassignintern.firebasestorage.app",
    messagingSenderId: "372848042260",
    appId: "1:372848042260:web:6b11048569e49a62bb6201",
    measurementId: "G-5LRJ39MCN3",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
