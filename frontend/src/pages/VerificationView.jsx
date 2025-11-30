import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './VerificationView.css';

function VerificationView() {
    const { projectName } = useParams();
    const [artifacts, setArtifacts] = useState({});
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);

    // Form State
    const [newActivity, setNewActivity] = useState({
        title: '',
        description: '',
        method: 'test',
        procedure: '',
        setup: '',
        passed: false
    });

    const fetchArtifacts = () => {
        setLoading(true);
        fetch(`/api/projects/${projectName}`)
            .then(res => res.json())
            .then(data => {
                setArtifacts(data.artifacts);
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching artifacts:', err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchArtifacts();
    }, [projectName]);

    const handleCreate = async (e) => {
        e.preventDefault();
        const payload = {
            type: 'verification_activity',
            title: newActivity.title,
            description: newActivity.description,
            method: newActivity.method,
            procedure: newActivity.procedure,
            setup: newActivity.setup,
            passed: newActivity.passed
        };

        try {
            const res = await fetch(`/api/artifacts/${projectName}/artifacts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setShowForm(false);
                setNewActivity({
                    title: '',
                    description: '',
                    method: 'test',
                    procedure: '',
                    setup: '',
                    passed: false
                });
                fetchArtifacts();
            }
        } catch (err) {
            console.error('Error creating verification activity:', err);
        }
    };

    const activities = Object.values(artifacts).filter(a => a.type === 'verification_activity');

    if (loading) return <div>Loading verification activities...</div>;

    return (
        <div className="verification-view">
            <div className="view-header">
                <h2>Verification Activities</h2>
                <button className="add-btn" onClick={() => setShowForm(!showForm)}>
                    {showForm ? 'Cancel' : 'Add Activity'}
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleCreate} className="add-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label>Title</label>
                            <input
                                value={newActivity.title}
                                onChange={e => setNewActivity({ ...newActivity, title: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Method</label>
                            <select
                                value={newActivity.method}
                                onChange={e => setNewActivity({ ...newActivity, method: e.target.value })}
                            >
                                <option value="test">Test</option>
                                <option value="analysis">Analysis</option>
                                <option value="review">Review</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Procedure</label>
                        <textarea
                            value={newActivity.procedure}
                            onChange={e => setNewActivity({ ...newActivity, procedure: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label>Setup / Environment</label>
                        <textarea
                            value={newActivity.setup}
                            onChange={e => setNewActivity({ ...newActivity, setup: e.target.value })}
                        />
                    </div>

                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={newActivity.passed}
                                onChange={e => setNewActivity({ ...newActivity, passed: e.target.checked })}
                            />
                            Passed
                        </label>
                    </div>

                    <button type="submit" className="submit-btn">Save Activity</button>
                </form>
            )}

            <div className="activities-list">
                {activities.map(act => (
                    <div key={act.id} className={`activity-card ${act.passed ? 'passed' : 'failed'}`}>
                        <div className="card-header">
                            <span className="method-badge">{act.method}</span>
                            <span className={`status-badge ${act.passed ? 'pass' : 'fail'}`}>
                                {act.passed ? 'PASS' : 'FAIL'}
                            </span>
                        </div>
                        <h3>{act.title}</h3>
                        <div className="activity-details">
                            {act.procedure && <p><strong>Procedure:</strong> {act.procedure}</p>}
                            {act.setup && <p><strong>Setup:</strong> {act.setup}</p>}
                        </div>
                    </div>
                ))}
                {activities.length === 0 && <div className="empty-state">No verification activities defined.</div>}
            </div>
        </div>
    );
}

export default VerificationView;
