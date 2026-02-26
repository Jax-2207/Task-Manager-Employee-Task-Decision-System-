import { useState } from "react";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import LoginPage from "./pages/LoginPage";
import AdminDashboard from "./pages/AdminDashboard";
import EmployeeDashboard from "./pages/EmployeeDashboard";
import "./index.css";

function AppContent() {
  const { userProfile, loading } = useAuth();

  if (loading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="spinner" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Not logged in
  if (!userProfile) {
    return <LoginPage />;
  }

  // Route by role
  if (userProfile.role === "ADMIN") {
    return <AdminDashboard />;
  }

  return <EmployeeDashboard />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
