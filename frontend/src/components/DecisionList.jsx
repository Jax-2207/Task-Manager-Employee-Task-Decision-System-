import DecisionCard from "./DecisionCard";

export default function DecisionList({ decisions, onStatusUpdate, onDelete }) {
    if (decisions.length === 0) {
        return (
            <div className="empty-state">
                <div className="empty-icon">📋</div>
                <h3>No decisions yet</h3>
                <p>Create your first decision to get started.</p>
            </div>
        );
    }

    return (
        <div className="decision-list">
            {decisions.map((d) => (
                <DecisionCard
                    key={d.id}
                    decision={d}
                    onStatusUpdate={onStatusUpdate}
                    onDelete={onDelete}
                />
            ))}
        </div>
    );
}
