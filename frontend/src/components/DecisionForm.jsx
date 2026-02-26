import { useState } from "react";

export default function DecisionForm({ onCreated }) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title.trim()) return;
        setLoading(true);
        setError(null);
        try {
            await onCreated(title.trim(), description.trim());
            setTitle("");
            setDescription("");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="decision-form">
            <h2>Propose a New Task</h2>
            {error && <div className="error-banner small">{error}</div>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="task-title">Task Title</label>
                    <input
                        id="task-title"
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter task title"
                        required
                        maxLength={200}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="task-desc">Description (optional)</label>
                    <textarea
                        id="task-desc"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Task details..."
                        rows={3}
                        maxLength={1000}
                    />
                </div>
                <button
                    type="submit"
                    className="btn btn-create"
                    disabled={loading || !title.trim()}
                >
                    {loading ? "Creating..." : "Submit Task"}
                </button>
            </form>
        </div>
    );
}
