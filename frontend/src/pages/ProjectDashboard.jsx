import React, { useState, useEffect } from 'react';
import { useParams, Routes, Route, Link, useLocation } from 'react-router-dom';
import './ProjectDashboard.css';

import RequirementsView from './RequirementsView';
import RiskView from './RiskView';
import VerificationView from './VerificationView';

function ProjectDashboard() {
    const { projectName } = useParams();
    const [projectData, setProjectData] = useState(null);
    const location = useLocation();

    useEffect(() => {
        fetch(`/api/projects/${projectName}`)
            .then(res => res.json())
            .then(data => setProjectData(data))
            .catch(err => console.error('Error fetching project:', err));
    }, [projectName]);

    if (!projectData) return <div>Loading...</div>;

    return (
        <div className="dashboard-container">
            <aside className="dashboard-sidebar">
                <h2>{projectName}</h2>
                <nav className="dashboard-nav">
                    <Link to={`/project/${projectName}`} className={location.pathname === `/project/${projectName}` ? 'active' : ''}>Overview</Link>
                    <Link to={`/project/${projectName}/requirements`} className={location.pathname.includes('requirements') ? 'active' : ''}>Requirements</Link>
                    <Link to={`/project/${projectName}/risks`} className={location.pathname.includes('risks') ? 'active' : ''}>Risk Management</Link>
                    <Link to={`/project/${projectName}/verification`} className={location.pathname.includes('verification') ? 'active' : ''}>Verification</Link>
                </nav>
            </aside>
            <main className="dashboard-content">
                <Routes>
                    <Route index element={
                        <div className="overview-panel">
                            <h3>Project Overview</h3>
                            <p>Artifacts: {Object.keys(projectData.artifacts).length}</p>
                            <p>Traces: {projectData.traces.length}</p>
                            {/* Add commit history or recent activity here */}
                        </div>
                    } />
                    <Route path="requirements" element={<RequirementsView />} />
                    <Route path="risks" element={<RiskView />} />
                    <Route path="verification" element={<VerificationView />} />
                </Routes>
            </main>
        </div>
    );
}

export default ProjectDashboard;
