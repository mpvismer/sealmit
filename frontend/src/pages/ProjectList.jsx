import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './ProjectList.css';

function ProjectList() {
    const [projects, setProjects] = useState([]);
    const [newProjectName, setNewProjectName] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetch('/api/projects/')
            .then(res => res.json())
            .then(data => setProjects(data))
            .catch(err => console.error('Error fetching projects:', err));
    }, []);

    const handleCreateProject = async (e) => {
        e.preventDefault();
        if (!newProjectName) return;

        try {
            const res = await fetch('/api/projects/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newProjectName, levels: ['User', 'System'] })
            });

            if (res.ok) {
                navigate(`/project/${newProjectName}`);
            } else {
                alert('Failed to create project');
            }
        } catch (err) {
            console.error('Error creating project:', err);
        }
    };

    return (
        <div className="project-list-container">
            <h1>Projects</h1>

            <div className="create-project-section">
                <h2>Create New Project</h2>
                <form onSubmit={handleCreateProject} className="create-project-form">
                    <input
                        type="text"
                        value={newProjectName}
                        onChange={(e) => setNewProjectName(e.target.value)}
                        placeholder="Project Name"
                        className="project-input"
                    />
                    <button type="submit" className="create-btn">Create</button>
                </form>
            </div>

            <div className="projects-grid">
                {projects.map(project => (
                    <Link key={project} to={`/project/${project}`} className="project-card">
                        <h3>{project}</h3>
                    </Link>
                ))}
            </div>
        </div>
    );
}

export default ProjectList;
