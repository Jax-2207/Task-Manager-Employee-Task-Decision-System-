import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import {
    fetchDecisions,
    createDecision,
    updateDecisionStatus,
    deleteDecision,
    assignDecision,
    assignDecisionToAll,
} from "../services/api";

export default function AdminDashboard() {
    const { userProfile, logout, getToken } = useAuth();
    const [tasks, setTasks] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [assignInputs, setAssignInputs] = useState({});

    // Create form state
    const [newTitle, setNewTitle] = useState("");
    const [newDesc, setNewDesc] = useState("");
    const [assignTarget, setAssignTarget] = useState("");
    const [creating, setCreating] = useState(false);

    const loadTasks = async () => {
        try {
            setError(null);
            const token = await getToken();
            const data = await fetchDecisions(token);
            setTasks(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTasks();
    }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        if (!newTitle.trim()) return;
        setCreating(true);
        setError(null);
        try {
            const token = await getToken();
            const task = await createDecision(newTitle.trim(), newDesc.trim() || null, token);

            if (assignTarget.trim()) {
                if (assignTarget.trim().toLowerCase() === "all") {
                    await assignDecisionToAll(task.id, token);
                } else {
                    await assignDecision(task.id, assignTarget.trim(), token);
                }
            }

            setNewTitle("");
            setNewDesc("");
            setAssignTarget("");
            await loadTasks();
        } catch (err) {
            setError(err.message);
        } finally {
            setCreating(false);
        }
    };

    const handleStatusUpdate = async (id, status) => {
        try {
            setError(null);
            const token = await getToken();
            await updateDecisionStatus(id, status, token);
            await loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleDelete = async (id) => {
        try {
            setError(null);
            const token = await getToken();
            await deleteDecision(id, token);
            await loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleAssign = async (taskId) => {
        const employeeId = assignInputs[taskId];
        if (!employeeId) return;
        try {
            setError(null);
            const token = await getToken();
            await assignDecision(taskId, employeeId, token);
            setAssignInputs({ ...assignInputs, [taskId]: "" });
            await loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleAssignAll = async (taskId) => {
        try {
            setError(null);
            const token = await getToken();
            await assignDecisionToAll(taskId, token);
            await loadTasks();
        } catch (err) {
            setError(err.message);
        }
    };

    const statusClass = (status) => `status-badge status-${status.toLowerCase()}`;

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-content">
                    <h1>⚡ Task Manager</h1>
                    <p className="subtitle">Admin Dashboard</p>
                </div>
                <div className="header-user">
                    <span className="role-badge role-admin">ADMIN</span>
                    <span className="user-email">{userProfile?.email}</span>
                    <span className="user-emp-id">{userProfile?.employee_id}</span>
                    <button className="btn btn-logout" onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            <main className="app-main">
                <div className="container">
                    {/* Create + Assign Task Form */}
                    <section className="form-section">
                        <div className="decision-form">
                            <h2>Create & Assign Task</h2>
                            <form onSubmit={handleCreate}>
                                <div className="form-group">
                                    <label htmlFor="admin-title">Task Title</label>
                                    <input
                                        id="admin-title"
                                        type="text"
                                        value={newTitle}
                                        onChange={(e) => setNewTitle(e.target.value)}
                                        placeholder="Enter task title"
                                        required
                                        maxLength={200}
                                    />
                                </div>
                                <div className="form-group">
                                    <label htmlFor="admin-desc">Description (optional)</label>
                                    <textarea
                                        id="admin-desc"
                                        value={newDesc}
                                        onChange={(e) => setNewDesc(e.target.value)}
                                        placeholder="Task details..."
                                        rows={3}
                                        maxLength={1000}
                                    />
                                </div>
                                <div className="form-group">
                                    <label htmlFor="admin-assign">
                                        Assign to (optional) — type <code>EMP-001</code> or <code>all</code>
                                    </label>
                                    <input
                                        id="admin-assign"
                                        type="text"
                                        value={assignTarget}
                                        onChange={(e) => setAssignTarget(e.target.value)}
                                        placeholder='EMP-001 or "all"'
                                    />
                                </div>
                                <button
                                    type="submit"
                                    className="btn btn-create"
                                    disabled={creating || !newTitle.trim()}
                                >
                                    {creating ? "Creating..." : "Create Task"}
                                </button>
                            </form>
                        </div>
                    </section>

                    {/* Task List */}
                    <section className="list-section">
                        <div className="section-header">
                            <h2>All Tasks</h2>
                            <span className="count-badge">{tasks.length}</span>
                        </div>

                        {error && <div className="error-banner">{error}</div>}
                        {loading ? (
                            <div className="loading">Loading tasks...</div>
                        ) : tasks.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-icon">📋</div>
                                <h3>No tasks yet</h3>
                                <p>Create a task above or wait for employees to propose.</p>
                            </div>
                        ) : (
                            <div className="decision-list">
                                {tasks.map((t) => (
                                    <div key={t.id} className="decision-card">
                                        <div className="card-header">
                                            <h3 className="card-title">{t.title}</h3>
                                            <span className={statusClass(t.status)}>{t.status}</span>
                                        </div>

                                        {t.description && (
                                            <p className="card-description">{t.description}</p>
                                        )}

                                        <div className="card-meta">
                                            <span>
                                                <strong>Created by:</strong>{" "}
                                                {t.created_by_employee_id || "—"} ({t.created_by_email || "N/A"})
                                            </span>
                                            {t.assigned_to_employee_id && (
                                                <span>
                                                    <strong>Assigned to:</strong>{" "}
                                                    {t.assigned_to_employee_id} ({t.assigned_to_email})
                                                </span>
                                            )}
                                            <span>Created: {new Date(t.created_at).toLocaleDateString()}</span>
                                        </div>

                                        <div className="card-actions">
                                            {t.status === "PROPOSED" && (
                                                <>
                                                    <button
                                                        className="btn btn-accept"
                                                        onClick={() => handleStatusUpdate(t.id, "ACCEPTED")}
                                                    >
                                                        ✓ Accept
                                                    </button>
                                                    <button
                                                        className="btn btn-reject"
                                                        onClick={() => handleStatusUpdate(t.id, "REJECTED")}
                                                    >
                                                        ✗ Reject
                                                    </button>
                                                </>
                                            )}
                                            <button
                                                className="btn btn-delete"
                                                onClick={() => handleDelete(t.id)}
                                            >
                                                🗑 Delete
                                            </button>
                                        </div>

                                        {/* Assignment controls */}
                                        <div className="assign-section">
                                            <div className="assign-row">
                                                <input
                                                    type="text"
                                                    placeholder="EMP-001"
                                                    value={assignInputs[t.id] || ""}
                                                    onChange={(e) =>
                                                        setAssignInputs({
                                                            ...assignInputs,
                                                            [t.id]: e.target.value,
                                                        })
                                                    }
                                                    className="assign-input"
                                                />
                                                <button
                                                    className="btn btn-assign"
                                                    onClick={() => handleAssign(t.id)}
                                                >
                                                    Assign
                                                </button>
                                                <button
                                                    className="btn btn-assign-all"
                                                    onClick={() => handleAssignAll(t.id)}
                                                >
                                                    Assign to All
                                                </button>
                                            </div>
                                        </div>
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
