import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './RequirementsView.css';

function RequirementsView() {
    const { projectName } = useParams();
    const [artifacts, setArtifacts] = useState({});
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);

    // Form State
    const [newReq, setNewReq] = useState({
        title: '',
        description: '',
        level: 'User',
        parent_id: ''
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
            type: 'requirement',
            title: newReq.title,
            description: newReq.description,
            level: newReq.level,
            parent_id: newReq.parent_id || null
        };

        try {
            const res = await fetch(`/api/artifacts/${projectName}/artifacts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setShowAddForm(false);
                setNewReq({ title: '', description: '', level: 'User', parent_id: '' });
                fetchArtifacts(); // Refresh list
            } else {
                alert('Failed to create requirement');
            }
        } catch (err) {
            console.error('Error creating requirement:', err);
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
                    <div className="form-group">
                        <label>Level</label>
                        <select
                            value={newReq.level}
                            onChange={e => setNewReq({ ...newReq, level: e.target.value })}
                        >
                            <option value="User">User</option>
                            <option value="System">System</option>
                            <option value="Performance">Performance</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Parent Requirement</label>
                        <select
                            value={newReq.parent_id}
                            onChange={e => setNewReq({ ...newReq, parent_id: e.target.value })}
                        >
                            <option value="">None</option>
                            {requirements.map(r => (
                                <option key={r.id} value={r.id}>{r.title}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            value={newReq.description}
                            onChange={e => setNewReq({ ...newReq, description: e.target.value })}
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
                        <th>Parent</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {requirements.map(req => (
                        <tr key={req.id}>
                            <td className="id-col" title={req.id}>{req.id.substring(0, 8)}...</td>
                            <td>{req.title}</td>
                            <td><span className={`badge level-${req.level.toLowerCase()}`}>{req.level}</span></td>
                            <td>
                                {req.parent_id ? (
                                    <span title={req.parent_id}>
                                        {artifacts[req.parent_id]?.title || req.parent_id.substring(0, 8)}
                                    </span>
                                ) : '-'}
                            </td>
                            <td>{req.description}</td>
                        </tr>
                    ))}
                    {requirements.length === 0 && (
                        <tr>
                            <td colSpan="5" className="empty-state">No requirements defined yet.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default RequirementsView;
