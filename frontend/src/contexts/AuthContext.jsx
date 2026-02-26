import { createContext, useContext, useState, useEffect } from "react";
import { signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged } from "firebase/auth";
import { auth } from "../firebase";
import { registerGoogleUser, getProfile, adminLogin } from "../services/api";

const AuthContext = createContext(null);

export function useAuth() {
    return useContext(AuthContext);
}

const googleProvider = new GoogleAuthProvider();

export function AuthProvider({ children }) {
    const [firebaseUser, setFirebaseUser] = useState(null);
    const [userProfile, setUserProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    // Admin uses a local session token, not Firebase
    const [adminToken, setAdminToken] = useState(() => localStorage.getItem("adminToken"));

    // On mount, check for admin session or Firebase auth
    useEffect(() => {
        // If admin token exists, fetch admin profile
        if (adminToken) {
            getProfile(adminToken)
                .then((profile) => {
                    setUserProfile(profile);
                    setLoading(false);
                })
                .catch(() => {
                    // Invalid admin token — clear it
                    localStorage.removeItem("adminToken");
                    setAdminToken(null);
                    setLoading(false);
                });
            return;
        }

        // Otherwise listen for Firebase auth
        const unsubscribe = onAuthStateChanged(auth, async (user) => {
            setFirebaseUser(user);
            if (user) {
                try {
                    const token = await user.getIdToken();
                    const profile = await getProfile(token);
                    setUserProfile(profile);
                } catch {
                    setUserProfile(null);
                }
            } else {
                setUserProfile(null);
            }
            setLoading(false);
        });
        return unsubscribe;
    }, [adminToken]);

    // Employee: Google Sign-In
    const signInWithGoogle = async () => {
        setError(null);
        try {
            const result = await signInWithPopup(auth, googleProvider);
            const token = await result.user.getIdToken();
            // Register in backend (creates employee user if new)
            const profile = await registerGoogleUser(token);
            setUserProfile(profile);
            return profile;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    // Admin: hardcoded login
    const loginAsAdmin = async (email, password) => {
        setError(null);
        try {
            const result = await adminLogin(email, password);
            const token = result.token;
            localStorage.setItem("adminToken", token);
            setAdminToken(token);
            setUserProfile(result.user);
            return result.user;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    };

    const logout = async () => {
        if (adminToken) {
            localStorage.removeItem("adminToken");
            setAdminToken(null);
        } else {
            await signOut(auth);
        }
        setUserProfile(null);
        setFirebaseUser(null);
    };

    const getToken = async () => {
        if (adminToken) return adminToken;
        if (firebaseUser) return firebaseUser.getIdToken();
        return null;
    };

    const value = {
        firebaseUser,
        userProfile,
        loading,
        error,
        signInWithGoogle,
        loginAsAdmin,
        logout,
        getToken,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
