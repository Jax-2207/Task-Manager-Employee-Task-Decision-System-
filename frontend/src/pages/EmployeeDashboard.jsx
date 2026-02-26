import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import DecisionForm from "../components/DecisionForm";
import {
    fetchDecisions,
    fetchAssignedDecisions,
    createDecision,
    deleteDecision,
} from "../services/api";

export default function EmployeeDashboard() {
    const { userProfile, logout, getToken } = useAuth();
    const [myTasks, setMyTasks] = useState([]);
    const [assignedTasks, setAssignedTasks] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("my");

    const loadData = async () => {
        try {
            setError(null);
            const token = await getToken();
            const [my, assigned] = await Promise.all([
                fetchDecisions(token),
                fetchAssignedDecisions(token),
            ]);
            setMyTasks(my);
            setAssignedTasks(assigned);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleCreate = async (title, description) => {
        const token = await getToken();
        await createDecision(title, description, token);
        await loadData();
    };

    const handleDelete = async (id) => {
        try {
            setError(null);
            const token = await getToken();
            await deleteDecision(id, token);
            await loadData();
        } catch (err) {
            setError(err.message);
        }
    };

    const statusClass = (status) => `status-badge status-${status.toLowerCase()}`;
    const currentList = activeTab === "my" ? myTasks : assignedTasks;

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-content">
                    <h1>⚡ Task Manager</h1>
                    <p className="subtitle">Employee Dashboard</p>
                </div>
                <div className="header-user">
                    <span className="role-badge role-employee">EMPLOYEE</span>
                    <span className="user-email">{userProfile?.email}</span>
                    <span className="user-emp-id">{userProfile?.employee_id}</span>
                    <button className="btn btn-logout" onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            <main className="app-main">
                <div className="container">
                    <section className="form-section">
                        <DecisionForm onCreated={handleCreate} />
                    </section>

                    <section className="list-section">
                        <div className="tabs">
                            <button
                                className={`tab ${activeTab === "my" ? "tab-active" : ""}`}
                                onClick={() => setActiveTab("my")}
                            >
                                My Tasks
                                <span className="count-badge">{myTasks.length}</span>
                            </button>
                            <button
                                className={`tab ${activeTab === "assigned" ? "tab-active" : ""}`}
                                onClick={() => setActiveTab("assigned")}
                            >
                                Assigned to Me
                                <span className="count-badge">{assignedTasks.length}</span>
                            </button>
                        </div>

                        {error && <div className="error-banner">{error}</div>}
                        {loading ? (
                            <div className="loading">Loading tasks...</div>
                        ) : currentList.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-icon">📋</div>
                                <h3>
                                    {activeTab === "my"
                                        ? "No tasks yet"
                                        : "Nothing assigned to you"}
                                </h3>
                                <p>
                                    {activeTab === "my"
                                        ? "Create your first task above."
                                        : "Your admin hasn't assigned any tasks yet."}
                                </p>
                            </div>
                        ) : (
                            <div className="decision-list">
                                {currentList.map((t) => (
                                    <div key={t.id} className="decision-card">
                                        <div className="card-header">
                                            <h3 className="card-title">{t.title}</h3>
                                            <span className={statusClass(t.status)}>
                                                {t.status}
                                            </span>
                                        </div>
                                        {t.description && (
                                            <p className="card-description">{t.description}</p>
                                        )}
                                        <div className="card-meta">
                                            <span>
                                                Created: {new Date(t.created_at).toLocaleDateString()}
                                            </span>
                                            <span>
                                                Updated: {new Date(t.updated_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                        {activeTab === "my" && (
                                            <div className="card-actions">
                                                <button
                                                    className="btn btn-delete"
                                                    onClick={() => handleDelete(t.id)}
                                                >
                                                    🗑 Delete
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                </div>
            </main>
        </div>
    );
}
