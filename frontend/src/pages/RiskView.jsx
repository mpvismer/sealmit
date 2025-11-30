import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './RiskView.css';

function RiskView() {
    const { projectName } = useParams();
    const [artifacts, setArtifacts] = useState({});
    const [loading, setLoading] = useState(true);
    const [showHazardForm, setShowHazardForm] = useState(false);
    const [showCauseForm, setShowCauseForm] = useState(false);

    // Form States
    const [newHazard, setNewHazard] = useState({ title: '', description: '', severity: 'Medium' });
    const [newCause, setNewCause] = useState({ title: '', description: '', probability: 'Medium' });

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

    const createArtifact = async (type, data) => {
        const payload = { type, ...data };
        try {
            const res = await fetch(`/api/artifacts/${projectName}/artifacts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                fetchArtifacts();
                return true;
            }
        } catch (err) {
            console.error('Error creating artifact:', err);
        }
        return false;
    };

    const handleCreateHazard = async (e) => {
        e.preventDefault();
        if (await createArtifact('risk_hazard', newHazard)) {
            setShowHazardForm(false);
            setNewHazard({ title: '', description: '', severity: 'Medium' });
        }
    };

    const handleCreateCause = async (e) => {
        e.preventDefault();
        if (await createArtifact('risk_cause', newCause)) {
            setShowCauseForm(false);
            setNewCause({ title: '', description: '', probability: 'Medium' });
        }
    };

    const hazards = Object.values(artifacts).filter(a => a.type === 'risk_hazard');
    const causes = Object.values(artifacts).filter(a => a.type === 'risk_cause');

    if (loading) return <div>Loading risks...</div>;

    return (
        <div className="risk-view">
            <div className="risk-section">
                <div className="section-header">
                    <h2>Hazards</h2>
                    <button className="add-btn" onClick={() => setShowHazardForm(!showHazardForm)}>
                        {showHazardForm ? 'Cancel' : 'Add Hazard'}
                    </button>
                </div>

                {showHazardForm && (
                    <form onSubmit={handleCreateHazard} className="add-form">
                        <input
                            placeholder="Hazard Title"
                            value={newHazard.title}
                            onChange={e => setNewHazard({ ...newHazard, title: e.target.value })}
                            required
                        />
                        <select
                            value={newHazard.severity}
                            onChange={e => setNewHazard({ ...newHazard, severity: e.target.value })}
                        >
                            <option value="High">High</option>
                            <option value="Medium">Medium</option>
                            <option value="Low">Low</option>
                        </select>
                        <textarea
                            placeholder="Description"
                            value={newHazard.description}
                            onChange={e => setNewHazard({ ...newHazard, description: e.target.value })}
                        />
                        <button type="submit" className="submit-btn">Save Hazard</button>
                    </form>
                )}

                <div className="cards-grid">
                    {hazards.map(h => (
                        <div key={h.id} className="risk-card hazard">
                            <div className="card-header">
                                <span className="id-badge">{h.id.substring(0, 6)}</span>
                                <span className={`severity-badge ${h.severity.toLowerCase()}`}>{h.severity}</span>
                            </div>
                            <h3>{h.title}</h3>
                            <p>{h.description}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="risk-section">
                <div className="section-header">
                    <h2>Causes</h2>
                    <button className="add-btn" onClick={() => setShowCauseForm(!showCauseForm)}>
                        {showCauseForm ? 'Cancel' : 'Add Cause'}
                    </button>
                </div>

                {showCauseForm && (
                    <form onSubmit={handleCreateCause} className="add-form">
                        <input
                            placeholder="Cause Title"
                            value={newCause.title}
                            onChange={e => setNewCause({ ...newCause, title: e.target.value })}
                            required
                        />
                        <select
                            value={newCause.probability}
                            onChange={e => setNewCause({ ...newCause, probability: e.target.value })}
                        >
                            <option value="High">High</option>
                            <option value="Medium">Medium</option>
                            <option value="Low">Low</option>
                        </select>
                        <textarea
                            placeholder="Description"
                            value={newCause.description}
                            onChange={e => setNewCause({ ...newCause, description: e.target.value })}
                        />
                        <button type="submit" className="submit-btn">Save Cause</button>
                    </form>
                )}

                <div className="cards-grid">
                    {causes.map(c => (
                        <div key={c.id} className="risk-card cause">
                            <div className="card-header">
                                <span className="id-badge">{c.id.substring(0, 6)}</span>
                                <span className={`probability-badge ${c.probability.toLowerCase()}`}>{c.probability}</span>
                            </div>
                            <h3>{c.title}</h3>
                            <p>{c.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default RiskView;
