import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './ProjectSettings.css';

function ProjectSettings() {
    const { projectName } = useParams();
    const [settings, setSettings] = useState({
        enforce_single_parent: false,
        prevent_orphans_at_lower_levels: false
    });
    const [levels, setLevels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        fetchData();
    }, [projectName]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [settingsRes, projectRes] = await Promise.all([
                fetch(`/api/projects/${projectName}/settings`),
                fetch(`/api/projects/${projectName}`)
            ]);

            if (!settingsRes.ok || !projectRes.ok) throw new Error('Failed to fetch data');

            const settingsData = await settingsRes.json();
            const projectData = await projectRes.json();

            setSettings(settingsData);
            
            // Normalize levels to object format if they are strings
            const normalizedLevels = projectData.config.levels.map(level => {
                if (typeof level === 'string') {
                    return { name: level, description: '' };
                }
                return level;
            });
            setLevels(normalizedLevels);
        } catch (err) {
            console.error('Error fetching settings:', err);
            setMessage({ type: 'error', text: 'Failed to load settings' });
        } finally {
            setLoading(false);
        }
    };

    const handleSettingChange = (key) => {
        setSettings(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    const handleLevelChange = (index, field, value) => {
        const newLevels = [...levels];
        newLevels[index] = { ...newLevels[index], [field]: value };
        setLevels(newLevels);
    };

    const addLevel = () => {
        setLevels([...levels, { name: 'New Level', description: '' }]);
    };

    const removeLevel = (index) => {
        const newLevels = levels.filter((_, i) => i !== index);
        setLevels(newLevels);
    };

    const saveSettings = async () => {
        try {
            setSaving(true);
            setMessage(null);

            // Save settings
            const settingsRes = await fetch(`/api/projects/${projectName}/settings`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });

            if (!settingsRes.ok) throw new Error('Failed to save settings');

            // Save levels
            const levelsRes = await fetch(`/api/projects/${projectName}/levels`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(levels)
            });

            if (!levelsRes.ok) throw new Error('Failed to save levels');

            setMessage({ type: 'success', text: 'Settings saved successfully' });
        } catch (err) {
            console.error('Error saving settings:', err);
            setMessage({ type: 'error', text: 'Failed to save settings' });
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="loading">Loading settings...</div>;

    return (
        <div className="settings-container">
            <div className="settings-header">
                <h2>Project Settings</h2>
                <button 
                    className="save-button" 
                    onClick={saveSettings} 
                    disabled={saving}
                >
                    {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>

            {message && (
                <div className={`message ${message.type}`}>
                    {message.text}
                </div>
            )}

            <div className="settings-section">
                <h3>Traceability Rules</h3>
                <div className="setting-card">
                    <div className="setting-info">
                        <h4>Single Parent Requirement</h4>
                        <p>When enabled, each requirement can only trace to one parent requirement. This enforces clean hierarchical decomposition following systems engineering best practices. When disabled (default), requirements can trace to multiple parents for flexibility in complex projects.</p>
                    </div>
                    <div className="setting-control">
                        <label className="switch">
                            <input 
                                type="checkbox" 
                                checked={settings.enforce_single_parent}
                                onChange={() => handleSettingChange('enforce_single_parent')}
                            />
                            <span className="slider round"></span>
                        </label>
                    </div>
                </div>

                <div className="setting-card">
                    <div className="setting-info">
                        <h4>Prevent Orphan Requirements</h4>
                        <p>When enabled, all requirements below the top level must have at least one parent requirement. This ensures complete traceability throughout the requirement hierarchy. Top-level requirements are always allowed to have no parent. When disabled, orphan requirements are permitted at any level.</p>
                    </div>
                    <div className="setting-control">
                        <label className="switch">
                            <input 
                                type="checkbox" 
                                checked={settings.prevent_orphans_at_lower_levels}
                                onChange={() => handleSettingChange('prevent_orphans_at_lower_levels')}
                            />
                            <span className="slider round"></span>
                        </label>
                    </div>
                </div>
            </div>

            <div className="settings-section">
                <h3>Requirement Levels</h3>
                <p className="section-desc">Define the hierarchy levels for requirements in this project. Order matters - top to bottom corresponds to high-level to low-level.</p>
                
                <div className="levels-list">
                    {levels.map((level, index) => (
                        <div key={index} className="level-item">
                            <div className="level-header">
                                <span className="level-number">{index + 1}</span>
                                <button 
                                    className="remove-level-btn"
                                    onClick={() => removeLevel(index)}
                                    title="Remove Level"
                                >
                                    ×
                                </button>
                            </div>
                            <div className="level-fields">
                                <div className="form-group">
                                    <label>Level Name</label>
                                    <input 
                                        type="text" 
                                        value={level.name}
                                        onChange={(e) => handleLevelChange(index, 'name', e.target.value)}
                                        placeholder="e.g. User, System"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Description</label>
                                    <input 
                                        type="text" 
                                        value={level.description}
                                        onChange={(e) => handleLevelChange(index, 'description', e.target.value)}
                                        placeholder="Purpose of this level..."
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                
                <button className="add-level-btn" onClick={addLevel}>
                    + Add Requirement Level
                </button>
            </div>
        </div>
    );
}

export default ProjectSettings;
