import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import ProjectDashboard from '../../pages/ProjectDashboard';

// Mock child components to avoid complex rendering and focus on dashboard structure
vi.mock('../../pages/RequirementsView', () => ({ default: () => <div>Requirements View</div> }));
vi.mock('../../pages/RiskView', () => ({ default: () => <div>Risk View</div> }));
vi.mock('../../pages/VerificationView', () => ({ default: () => <div>Verification View</div> }));
vi.mock('../../pages/ProjectSettings', () => ({ default: () => <div>Settings View</div> }));

global.fetch = vi.fn();

describe('ProjectDashboard Integration', () => {
    beforeEach(() => {
        fetch.mockClear();
        fetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({
                config: { name: 'TestProject' },
                artifacts: {},
                traces: []
            })
        });
    });

    test('renders dashboard and fetches project data', async () => {
        render(
            <MemoryRouter initialEntries={['/project/TestProject']}>
                <Routes>
                    <Route path="/project/:projectName/*" element={<ProjectDashboard />} />
                </Routes>
            </MemoryRouter>
        );

        // Initial loading state
        expect(screen.getByText('Loading...')).toBeInTheDocument();

        // Wait for data load
        await waitFor(() => {
            expect(screen.getByText('TestProject')).toBeInTheDocument();
        });

        // Verify navigation links
        expect(screen.getByText('Overview')).toBeInTheDocument();
        expect(screen.getByText('Requirements')).toBeInTheDocument();
        expect(screen.getByText('Risk Management')).toBeInTheDocument();
    });

    test('navigates to requirements view', async () => {
        render(
            <MemoryRouter initialEntries={['/project/TestProject/requirements']}>
                <Routes>
                    <Route path="/project/:projectName/*" element={<ProjectDashboard />} />
                </Routes>
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('Requirements View')).toBeInTheDocument();
        });
    });

    test('navigates to settings view', async () => {
        render(
            <MemoryRouter initialEntries={['/project/TestProject/settings']}>
                <Routes>
                    <Route path="/project/:projectName/*" element={<ProjectDashboard />} />
                </Routes>
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('Settings View')).toBeInTheDocument();
        });
    });
});
