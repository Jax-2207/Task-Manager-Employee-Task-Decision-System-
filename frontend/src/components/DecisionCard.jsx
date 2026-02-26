import { useState } from "react";

export default function DecisionCard({ decision, onStatusUpdate, onDelete }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const isProposed = decision.status === "PROPOSED";
    const statusClass = `status-badge status-${decision.status.toLowerCase()}`;

    const handleAction = async (action) => {
        setError(null);
        setLoading(true);
        try {
            if (action === "DELETE") {
                await onDelete(decision.id);
            } else {
                await onStatusUpdate(decision.id, action);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="decision-card">
            <div className="card-header">
                <h3 className="card-title">{decision.title}</h3>
                <span className={statusClass}>{decision.status}</span>
            </div>

            {decision.description && (
                <p className="card-description">{decision.description}</p>
            )}

            <div className="card-meta">
                <span>Created: {new Date(decision.created_at).toLocaleDateString()}</span>
                <span>Updated: {new Date(decision.updated_at).toLocaleDateString()}</span>
            </div>

            {error && <div className="error-banner small">{error}</div>}

            <div className="card-actions">
                {isProposed && (
                    <>
                        <button
                            className="btn btn-accept"
                            onClick={() => handleAction("ACCEPTED")}
                            disabled={loading}
                        >
                            ✓ Accept
                        </button>
                        <button
                            className="btn btn-reject"
                            onClick={() => handleAction("REJECTED")}
                            disabled={loading}
                        >
                            ✗ Reject
                        </button>
                    </>
                )}
                <button
                    className="btn btn-delete"
                    onClick={() => handleAction("DELETE")}
                    disabled={loading}
                >
                    🗑 Delete
                </button>
            </div>
        </div>
    );
}
