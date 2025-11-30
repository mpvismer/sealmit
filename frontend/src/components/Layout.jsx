import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import Assistant from './Assistant';
import './Layout.css';

function Layout() {
    return (
        <div className="app-container">
            <header className="app-header">
                <div className="logo">
                    <Link to="/">SEALMit</Link>
                </div>
                <nav>
                    {/* Global nav items if any */}
                </nav>
            </header>
            <main className="app-content">
                <Outlet />
            </main>
            <Assistant />
        </div>
    );
}

export default Layout;
