import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './RequirementsView.css';

function RequirementsView() {
    const { projectName } = useParams();
    const [artifacts, setArtifacts] = useState({});
    const [settings, setSettings] = useState({
        enforce_single_parent: false,
        prevent_orphans_at_lower_levels: false
    });
    const [levels, setLevels] = useState(['User', 'System']);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [error, setError] = useState(null);

    // Form State
    const [newReq, setNewReq] = useState({
        title: '',
        description: '',
        justification: '',
        level: '',
        parent_ids: []
    });

    const fetchData = async () => {
        try {
            setLoading(true);
            const [projectRes, settingsRes] = await Promise.all([
                fetch(`/api/projects/${projectName}`),
                fetch(`/api/projects/${projectName}/settings`)
            ]);

            if (!projectRes.ok) throw new Error('Failed to fetch project data');

            const projectData = await projectRes.json();
            setArtifacts(projectData.artifacts);

            // Extract levels
            const configLevels = projectData.config.levels.map(l =>
                typeof l === 'string' ? l : l.name
            );
            setLevels(configLevels);

            // Set default level if not set
            if (!newReq.level && configLevels.length > 0) {
                setNewReq(prev => ({ ...prev, level: configLevels[0] }));
            }

            if (settingsRes.ok) {
                const settingsData = await settingsRes.json();
                setSettings(settingsData);
            }
        } catch (err) {
            console.error('Error fetching data:', err);
            setError('Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [projectName]);

    const handleCreate = async (e) => {
        e.preventDefault();
        setError(null);

        const payload = {
            type: 'requirement',
            title: newReq.title,
            description: newReq.description,
            justification: newReq.justification,
            level: newReq.level,
            parent_ids: newReq.parent_ids
        };

        try {
            const res = await fetch(`/api/artifacts/${projectName}/artifacts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setShowAddForm(false);
                setNewReq({
                    title: '',
                    description: '',
                    justification: '',
                    level: levels[0] || '',
                    parent_ids: []
                });
                fetchData(); // Refresh list
            } else {
                const data = await res.json();
                setError(data.detail || 'Failed to create requirement');
            }
        } catch (err) {
            console.error('Error creating requirement:', err);
            setError('Failed to create requirement');
        }
    };

    const handleParentChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);

        if (settings.enforce_single_parent && selectedOptions.length > 1) {
            // If single parent enforced, only keep the last selected
            setNewReq({ ...newReq, parent_ids: [selectedOptions[selectedOptions.length - 1]] });
        } else {
            setNewReq({ ...newReq, parent_ids: selectedOptions });
        }
    };

    const requirements = Object.values(artifacts).filter(a => a.type === 'requirement');

    if (loading) return <div>Loading requirements...</div>;

    return (
        <div className="requirements-view">
            <div className="view-header">
                <h2>Requirements</h2>
                <button className="add-btn" onClick={() => setShowAddForm(!showAddForm)}>
                    {showAddForm ? 'Cancel' : 'Add Requirement'}
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {showAddForm && (
                <form onSubmit={handleCreate} className="add-form">
                    <div className="form-group">
                        <label>Title</label>
                        <input
                            type="text"
                            value={newReq.title}
                            onChange={e => setNewReq({ ...newReq, title: e.target.value })}
                            required
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Level</label>
                            <select
                                value={newReq.level}
                                onChange={e => setNewReq({ ...newReq, level: e.target.value })}
                            >
                                {levels.map(level => (
                                    <option key={level} value={level}>{level}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label>
                                Parent Requirement(s)
                                {settings.enforce_single_parent && <span className="hint"> (Single parent only)</span>}
                            </label>
                            <select
                                multiple={!settings.enforce_single_parent}
                                value={settings.enforce_single_parent ? (newReq.parent_ids[0] || '') : newReq.parent_ids}
                                onChange={handleParentChange}
                                className="parent-select"
                                size={5}
                            >
                                {!settings.enforce_single_parent && <option value="">None (Hold Ctrl/Cmd to select multiple)</option>}
                                {settings.enforce_single_parent && <option value="">None</option>}
                                {requirements.map(r => (
                                    <option key={r.id} value={r.id}>{r.title}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            value={newReq.description}
                            onChange={e => setNewReq({ ...newReq, description: e.target.value })}
                            rows={3}
                        />
                    </div>

                    <div className="form-group">
                        <label>Justification</label>
                        <textarea
                            value={newReq.justification}
                            onChange={e => setNewReq({ ...newReq, justification: e.target.value })}
                            placeholder="Rationale for this requirement..."
                            rows={2}
                        />
                    </div>

                    <button type="submit" className="submit-btn">Save Requirement</button>
                </form>
            )}

            <table className="artifacts-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Level</th>
                        <th>Parents</th>
                        <th>Description</th>
                        <th>Justification</th>
                    </tr>
                </thead>
                <tbody>
                    {requirements.map(req => (
                        <tr key={req.id}>
                            <td className="id-col" title={req.id}>{req.id.substring(0, 8)}...</td>
                            <td>{req.title}</td>
                            <td><span className={`badge level-${req.level.toLowerCase()}`}>{req.level}</span></td>
                            <td>
                                {req.parent_ids && req.parent_ids.length > 0 ? (
                                    <div className="parents-list">
                                        {req.parent_ids.map(pid => (
                                            <span key={pid} className="parent-tag" title={artifacts[pid]?.title || pid}>
                                                {artifacts[pid]?.title || pid.substring(0, 8)}
                                            </span>
                                        ))}
                                    </div>
                                ) : req.parent_id ? (
                                    <span className="parent-tag" title={artifacts[req.parent_id]?.title || req.parent_id}>
                                        {artifacts[req.parent_id]?.title || req.parent_id.substring(0, 8)}
                                    </span>
                                ) : '-'}
                            </td>
                            <td>{req.description}</td>
                            <td className="justification-col">{req.justification || '-'}</td>
                        </tr>
                    ))}
                    {requirements.length === 0 && (
                        <tr>
                            <td colSpan="6" className="empty-state">No requirements defined yet.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default RequirementsView;
