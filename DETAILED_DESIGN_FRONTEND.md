# SEALMit - Frontend Detailed Design

## 1. Overview

The SEALMit frontend is a modern **React 19** single-page application (SPA) built with **Vite** for fast development and optimized production builds. The application provides an intuitive interface for managing engineering projects, requirements, risks, and verification activities.

---

## 2. Technology Stack

### 2.1 Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | ^19.2.0 | UI framework with component-based architecture |
| **React Router** | ^7.9.6 | Client-side routing and navigation |
| **Vite** | ^7.2.4 | Build tool, dev server, and bundler |
| **ESLint** | ^9.39.1 | Code linting and quality checks |

### 2.2 Build Configuration

**Vite Configuration** (`vite.config.js`):
- Development server on port 5173
- Hot Module Replacement (HMR) for instant updates
- Production build optimization
- React Fast Refresh for component state preservation

---

## 3. Application Structure

### 3.1 Directory Layout

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Layout.jsx       # Main layout wrapper
│   │   ├── Layout.css
│   │   ├── Assistant.jsx    # AI assistant chat
│   │   └── Assistant.css
│   ├── pages/               # Page components
│   │   ├── ProjectList.jsx  # Project listing and creation
│   │   ├── ProjectList.css
│   │   ├── ProjectDashboard.jsx  # Project overview
│   │   ├── ProjectDashboard.css
│   │   ├── RequirementsView.jsx  # Requirements management
│   │   ├── RequirementsView.css
│   │   ├── RiskView.jsx     # Risk management
│   │   ├── RiskView.css
│   │   ├── VerificationView.jsx  # Verification activities
│   │   └── VerificationView.css
│   ├── App.jsx              # Root component with routing
│   ├── App.css              # Global app styles
│   ├── main.jsx             # Application entry point
│   └── index.css            # Global CSS and design system
├── public/                  # Static assets
├── dist/                    # Production build output
├── package.json             # Dependencies and scripts
├── vite.config.js           # Vite configuration
└── eslint.config.js         # ESLint configuration
```

### 3.2 Component Hierarchy

```
App (Router)
└── Layout
    ├── Header
    │   └── Logo (Link to /)
    ├── Main Content (Outlet)
    │   ├── ProjectList (/)
    │   └── ProjectDashboard (/project/:projectName/*)
    │       ├── RequirementsView
    │       ├── RiskView
    │       └── VerificationView
    └── Assistant (Floating)
```

---

## 4. Routing

### 4.1 Route Configuration

**File**: `App.jsx`

```jsx
<Router>
  <Routes>
    <Route path="/" element={<Layout />}>
      <Route index element={<ProjectList />} />
      <Route path="project/:projectName/*" element={<ProjectDashboard />} />
    </Route>
  </Routes>
</Router>
```

### 4.2 Route Descriptions

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | ProjectList | Home page with project list and creation form |
| `/project/:projectName/*` | ProjectDashboard | Project-specific dashboard with tabs |

**Nested Routing**: ProjectDashboard uses internal tab-based navigation (not URL-based).

---

## 5. Component Details

### 5.1 Layout Component

**File**: `components/Layout.jsx`

**Purpose**: Application shell with header and AI assistant.

**Structure**:
```jsx
function Layout() {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo">
          <Link to="/">SealMit</Link>
        </div>
        <nav>{/* Global nav items */}</nav>
      </header>
      <main className="app-content">
        <Outlet />  {/* Child routes render here */}
      </main>
      <Assistant />
    </div>
  );
}
```

**Key Features**:
- **Header**: Logo with link to home
- **Outlet**: React Router outlet for child routes
- **Assistant**: Floating AI chat interface

**Styling**: Minimal layout CSS for flexbox structure.

---

### 5.2 ProjectList Component

**File**: `pages/ProjectList.jsx`

**Purpose**: Display all projects and provide project creation form.

**State**:
```jsx
const [projects, setProjects] = useState([]);      // Array of project names
const [newProjectName, setNewProjectName] = useState('');  // Form input
```

**API Integration**:
```jsx
// Fetch projects on mount
useEffect(() => {
  fetch('http://localhost:8000/api/projects/')
    .then(res => res.json())
    .then(data => setProjects(data))
    .catch(err => console.error('Error fetching projects:', err));
}, []);

// Create new project
const handleCreateProject = async (e) => {
  e.preventDefault();
  const res = await fetch('http://localhost:8000/api/projects/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      name: newProjectName, 
      levels: ['User', 'System'] 
    })
  });
  if (res.ok) {
    navigate(`/project/${newProjectName}`);
  }
};
```

**UI Elements**:
- **Title**: "Projects" heading
- **Create Form**: Input field and submit button
- **Project Grid**: Cards for each project (clickable links)

**Navigation**: Clicking a project card navigates to `/project/{projectName}`.

**Styling**: Grid layout for project cards, form styling.

---

### 5.3 ProjectDashboard Component

**File**: `pages/ProjectDashboard.jsx`

**Purpose**: Project overview with tabbed navigation to different views.

**State**:
```jsx
const [activeTab, setActiveTab] = useState('requirements');
const [projectData, setProjectData] = useState(null);
```

**API Integration**:
```jsx
// Fetch project data on mount or when projectName changes
useEffect(() => {
  fetch(`http://localhost:8000/api/projects/${projectName}`)
    .then(res => res.json())
    .then(data => setProjectData(data))
    .catch(err => console.error('Error fetching project:', err));
}, [projectName]);
```

**Tab Navigation**:
```jsx
<div className="tabs">
  <button onClick={() => setActiveTab('requirements')}>Requirements</button>
  <button onClick={() => setActiveTab('risks')}>Risks</button>
  <button onClick={() => setActiveTab('verification')}>Verification</button>
</div>

<div className="tab-content">
  {activeTab === 'requirements' && <RequirementsView projectData={projectData} />}
  {activeTab === 'risks' && <RiskView projectData={projectData} />}
  {activeTab === 'verification' && <VerificationView projectData={projectData} />}
</div>
```

**Props Passed to Views**:
- `projectData`: Complete ProjectState object
- `projectName`: Project name from URL parameter

**Styling**: Tab bar with active state, content area.

---

### 5.4 RequirementsView Component

**File**: `pages/RequirementsView.jsx`

**Purpose**: Display and manage requirements in hierarchical structure.

**State**:
```jsx
const [requirements, setRequirements] = useState([]);
const [showCreateForm, setShowCreateForm] = useState(false);
const [newRequirement, setNewRequirement] = useState({
  title: '',
  description: '',
  level: 'User',
  parent_id: null
});
```

**Data Processing**:
```jsx
// Filter requirements from artifacts
useEffect(() => {
  if (projectData?.artifacts) {
    const reqs = Object.values(projectData.artifacts)
      .filter(a => a.type === 'requirement');
    setRequirements(reqs);
  }
}, [projectData]);
```

**Create Requirement**:
```jsx
const handleCreateRequirement = async (e) => {
  e.preventDefault();
  const res = await fetch(
    `http://localhost:8000/api/artifacts/${projectName}/artifacts`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'requirement',
        ...newRequirement
      })
    }
  );
  if (res.ok) {
    // Refresh project data
  }
};
```

**UI Elements**:
- **Requirements List**: Hierarchical display with parent-child relationships
- **Create Button**: Toggle form visibility
- **Create Form**: Fields for title, description, level, parent
- **Requirement Cards**: Display individual requirements

**Hierarchy Display**: Requirements with `parent_id` are indented under their parent.

**Styling**: Tree-like structure with indentation, form styling.

---

### 5.5 RiskView Component

**File**: `pages/RiskView.jsx`

**Purpose**: Display and manage risk hazards and causes.

**State**:
```jsx
const [hazards, setHazards] = useState([]);
const [causes, setCauses] = useState([]);
const [showCreateHazard, setShowCreateHazard] = useState(false);
const [showCreateCause, setShowCreateCause] = useState(false);
```

**Data Processing**:
```jsx
useEffect(() => {
  if (projectData?.artifacts) {
    const h = Object.values(projectData.artifacts)
      .filter(a => a.type === 'risk_hazard');
    const c = Object.values(projectData.artifacts)
      .filter(a => a.type === 'risk_cause');
    setHazards(h);
    setCauses(c);
  }
}, [projectData]);
```

**Create Hazard/Cause**: Similar pattern to RequirementsView.

**UI Elements**:
- **Hazards Section**: List of risk hazards with severity
- **Causes Section**: List of risk causes with probability
- **Create Forms**: Separate forms for hazards and causes
- **Trace Display**: Show CAUSES traces linking causes to hazards

**Styling**: Two-column layout for hazards and causes.

---

### 5.6 VerificationView Component

**File**: `pages/VerificationView.jsx`

**Purpose**: Display and manage verification activities.

**State**:
```jsx
const [verifications, setVerifications] = useState([]);
const [showCreateForm, setShowCreateForm] = useState(false);
const [newVerification, setNewVerification] = useState({
  title: '',
  description: '',
  method: 'test',
  procedure: '',
  setup: '',
  passed: false
});
```

**Data Processing**:
```jsx
useEffect(() => {
  if (projectData?.artifacts) {
    const vers = Object.values(projectData.artifacts)
      .filter(a => a.type === 'verification_activity');
    setVerifications(vers);
  }
}, [projectData]);
```

**UI Elements**:
- **Verification List**: Cards for each verification activity
- **Method Badge**: Visual indicator for TEST/ANALYSIS/REVIEW
- **Pass/Fail Status**: Color-coded status indicator
- **Create Form**: Fields for all verification properties
- **Trace Display**: Show VERIFIES traces to requirements

**Styling**: Card-based layout with status colors.

---

### 5.7 Assistant Component

**File**: `components/Assistant.jsx`

**Purpose**: Floating AI chat interface for user assistance.

**State**:
```jsx
const [isOpen, setIsOpen] = useState(false);
const [messages, setMessages] = useState([]);
const [input, setInput] = useState('');
```

**Chat Functionality**:
```jsx
const handleSendMessage = async () => {
  const userMessage = { role: 'user', content: input };
  setMessages([...messages, userMessage]);
  
  const res = await fetch('http://localhost:8000/api/ai/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: input,
      history: messages
    })
  });
  
  const data = await res.json();
  const assistantMessage = { role: 'assistant', content: data.response };
  setMessages([...messages, userMessage, assistantMessage]);
  setInput('');
};
```

**UI Elements**:
- **Toggle Button**: Floating button in bottom-right corner
- **Chat Window**: Expandable panel with message history
- **Message List**: Scrollable conversation history
- **Input Field**: Text input with send button

**Styling**: Fixed position, z-index for overlay, chat bubble styling.

---

## 6. State Management

### 6.1 Component State

**Pattern**: Each component manages its own state using `useState`.

**No Global State**: Currently no Redux or Context API (simple enough without).

**State Lifting**: ProjectDashboard fetches project data and passes to child views.

### 6.2 API Communication Pattern

**Fetch Pattern**:
```jsx
// GET request
fetch('http://localhost:8000/api/...')
  .then(res => res.json())
  .then(data => setState(data))
  .catch(err => console.error(err));

// POST request
fetch('http://localhost:8000/api/...', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
  .then(res => res.json())
  .then(data => handleSuccess(data))
  .catch(err => console.error(err));
```

**Error Handling**: Basic console logging (future: user-facing error messages).

**Loading States**: Future enhancement (currently no loading indicators).

---

## 7. Styling Strategy

### 7.1 CSS Architecture

**Approach**: Component-scoped CSS files (not CSS modules, just naming convention).

**File Pattern**: `ComponentName.jsx` + `ComponentName.css`

**Global Styles**: `index.css` contains design system tokens and resets.

### 7.2 Design System (`index.css`)

**CSS Variables**:
```css
:root {
  /* Colors */
  --primary-color: #4a90e2;
  --secondary-color: #50c878;
  --danger-color: #e74c3c;
  --background: #f5f7fa;
  --surface: #ffffff;
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
  
  /* Borders */
  --border-radius: 8px;
  --border-color: #e1e8ed;
}
```

**Usage**: Components reference CSS variables for consistency.

### 7.3 Responsive Design

**Breakpoints**:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Approach**: Mobile-first with media queries for larger screens.

---

## 8. Build and Development

### 8.1 Development Workflow

**Start Dev Server**:
```bash
cd frontend
npm install
npm run dev
```

**Dev Server**: Runs on `http://localhost:5173` with HMR.

**API Proxy**: Frontend makes requests to `http://localhost:8000` (backend must be running).

### 8.2 Production Build

**Build Command**:
```bash
npm run build
```

**Output**: `dist/` directory with optimized static files.

**Optimization**:
- Minification
- Tree shaking
- Code splitting
- Asset optimization

### 8.3 Linting

**Run ESLint**:
```bash
npm run lint
```

**Configuration**: `eslint.config.js` with React and hooks rules.

---

## 9. Component Communication

### 9.1 Props Flow

```
ProjectDashboard
  ↓ (projectData, projectName)
RequirementsView / RiskView / VerificationView
```

**Pattern**: Parent fetches data, children display and mutate.

### 9.2 Event Handling

**Pattern**: Child components handle their own form submissions and API calls.

**Refresh Strategy**: After mutations, components can:
1. Refetch project data from parent
2. Optimistically update local state
3. Navigate to trigger re-render

**Future**: Implement proper state management or React Query for caching.

---

## 10. Future Enhancements

### 10.1 Planned Features

- **Loading States**: Skeleton screens and spinners
- **Error Boundaries**: Graceful error handling
- **Toast Notifications**: User feedback for actions
- **Confirmation Dialogs**: For destructive actions
- **Search and Filter**: Advanced artifact filtering
- **Drag and Drop**: Reorder requirements, create traces visually
- **Dark Mode**: Theme toggle
- **Accessibility**: ARIA labels, keyboard navigation

### 10.2 Performance Optimizations

- **React.memo**: Memoize expensive components
- **useMemo/useCallback**: Optimize re-renders
- **Virtualization**: For large lists (react-window)
- **Code Splitting**: Lazy load routes
- **Service Worker**: Offline support

### 10.3 State Management

**Consider**:
- **React Query**: For API caching and synchronization
- **Zustand**: Lightweight global state
- **Context API**: For theme, user preferences

---

## 11. Testing Strategy

### 11.1 Current Status

No automated tests currently implemented.

### 11.2 Planned Testing

**Unit Tests** (Vitest + React Testing Library):
- Component rendering
- User interactions
- Form validation

**Integration Tests**:
- API integration
- Routing
- Multi-component workflows

**E2E Tests** (Playwright):
- Complete user workflows
- Cross-browser testing

---

## 12. Accessibility

### 12.1 Current Implementation

- Semantic HTML elements
- Keyboard navigation (browser default)

### 12.2 Future Improvements

- ARIA labels for all interactive elements
- Focus management for modals and forms
- Screen reader testing
- Color contrast compliance (WCAG AA)
- Keyboard shortcuts for common actions

---

## 13. Browser Compatibility

**Target Browsers**:
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

**Polyfills**: Vite handles modern JavaScript transpilation.

---

## 14. Development Guidelines

### 14.1 Component Creation

**Template**:
```jsx
import React, { useState, useEffect } from 'react';
import './ComponentName.css';

function ComponentName({ prop1, prop2 }) {
  const [state, setState] = useState(initialValue);
  
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  const handleAction = () => {
    // Event handler
  };
  
  return (
    <div className="component-name">
      {/* JSX */}
    </div>
  );
}

export default ComponentName;
```

### 14.2 Naming Conventions

- **Components**: PascalCase (e.g., `ProjectList`)
- **Files**: PascalCase for components (e.g., `ProjectList.jsx`)
- **CSS Classes**: kebab-case (e.g., `project-list-container`)
- **Functions**: camelCase (e.g., `handleCreateProject`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

### 14.3 Code Style

- **Indentation**: 2 spaces
- **Quotes**: Single quotes for JSX attributes, strings
- **Semicolons**: Required
- **Arrow Functions**: Preferred for event handlers
- **Destructuring**: Use for props and state

---

## 14. Implementation Status

### 14.1 ✅ Fully Implemented (Core Components)

The following components are **fully implemented** and align with REQUIREMENTS.md core requirements:

#### Layout & Navigation
- ✅ Layout component with header and outlet
- ✅ Logo with home link
- ✅ React Router setup with nested routes
- **Requirements**: FR-UI-001, FR-UI-002, FR-UI-003

#### ProjectList Component
- ✅ Project listing from API
- ✅ Project creation form
- ✅ Navigation to project dashboard
- ✅ Grid layout for projects
- **Requirements**: FR-PM-001, FR-PM-002, FR-PM-004

#### ProjectDashboard Component
- ✅ Tab-based navigation
- ✅ Project data fetching
- ✅ Tab switching (Requirements, Risks, Verification)
- ✅ Props passing to child views
- **Requirements**: FR-PM-005, FR-UI-003, FR-UI-004

#### RequirementsView Component
- ✅ Requirements listing
- ✅ Hierarchical display (parent-child)
- ✅ Create requirement form
- ✅ Level selection
- ✅ API integration (create, list)
- **Requirements**: FR-REQ-001 through FR-REQ-008, FR-UI-004, FR-UI-005

#### RiskView Component
- ✅ Hazards listing
- ✅ Causes listing
- ✅ Create hazard form
- ✅ Create cause form
- ✅ Severity and probability display
- ✅ API integration
- **Requirements**: FR-RISK-001 through FR-RISK-007, FR-UI-004, FR-UI-005

#### VerificationView Component
- ✅ Verification activities listing
- ✅ Method badges (TEST/ANALYSIS/REVIEW)
- ✅ Pass/fail status display
- ✅ Create verification form
- ✅ Procedure and setup fields
- ✅ API integration
- **Requirements**: FR-VER-001 through FR-VER-006, FR-UI-004, FR-UI-005

#### Assistant Component
- ✅ Floating chat interface
- ✅ Toggle open/close
- ✅ Message history display
- ✅ Chat input and send
- ✅ API integration (placeholder)
- **Requirements**: FR-AI-001, FR-AI-002 (partial), FR-AI-005

### 14.2 ⏳ Planned (Advanced Features)

The following features are **documented in REQUIREMENTS.md and ARCHITECTURE.md** but **not yet implemented**:

#### ConflictResolutionView Component
- ❌ Side-by-side diff view
- ❌ Merge conflict resolution UI
- ❌ Accept theirs/ours/manual merge options
- ❌ Conflict highlighting
- ❌ Three-way merge visualization
- **Requirements**: FR-COLLAB-007, FR-COLLAB-008
- **Documentation**: ARCHITECTURE.md Section 9.2

#### ExportManager Component
- ❌ Template editor with syntax highlighting
- ❌ Export preview (Markdown rendering)
- ❌ Export script viewer
- ❌ Format selection (MD/CSV/XLS/PDF)
- ❌ PDF preview
- ❌ Template customization UI
- **Requirements**: FR-EXP-001 through FR-EXP-010
- **Documentation**: ARCHITECTURE.md Section 7.3
- **Dependencies** (needed):
  - `marked` - Markdown rendering
  - `monaco-editor` - Code editor
  - `pdfjs-dist` - PDF preview

#### UserManagement Component
- ❌ User list and permissions
- ❌ OAuth configuration UI
- ❌ Organization settings
- ❌ Session management UI
- ❌ Role assignment
- **Requirements**: FR-USER-001 through FR-USER-007
- **Documentation**: ARCHITECTURE.md Section 7.4

#### TaskManager Component
- ❌ Background task list
- ❌ Task status monitoring
- ❌ Progress bars
- ❌ Stop/edit/continue controls
- ❌ Task history
- **Requirements**: FR-AI-008, FR-AI-009
- **Documentation**: ARCHITECTURE.md Section 7.2

#### Auto-Save Strategy
- ❌ Debounced save on keystroke (300-500ms)
- ❌ Draft state persistence (localStorage/IndexedDB)
- ❌ Optimistic UI updates
- ❌ Conflict detection on save
- ❌ Recovery on page reload
- ❌ Auto-save indicators
- **Requirements**: FR-COLLAB-003, FR-COLLAB-004, FR-UI-013, FR-UI-014
- **Documentation**: ARCHITECTURE.md Section 9.2

#### Real-Time Collaboration
- ❌ WebSocket connection management
- ❌ Real-time draft updates from other users
- ❌ Conflict notifications
- ❌ Presence indicators
- ❌ Live editing awareness
- **Requirements**: FR-COLLAB-010 (future)
- **Documentation**: ARCHITECTURE.md Section 9.2

#### Enhanced AI Features
- ❌ Task management UI in assistant
- ❌ File upload interface
- ❌ Progress tracking for long tasks
- ❌ Stop/edit/continue buttons
- ❌ Code-aware responses display
- ❌ RAG context visualization
- **Requirements**: FR-AI-006 through FR-AI-019
- **Documentation**: ARCHITECTURE.md Section 7.2

#### Advanced UI Features
- ❌ Tooltips for all interactive elements
- ❌ Integrated help panels
- ❌ Loading states and skeletons
- ❌ Error boundaries
- ❌ Toast notifications
- ❌ Confirmation dialogs
- ❌ Search and filter
- ❌ Drag and drop
- **Requirements**: FR-UI-006, FR-UI-011, FR-UI-012
- **Documentation**: Section 10.1

### 14.3 Implementation Roadmap

**Phase 1: Core Features** ✅ **COMPLETE**
- All basic components
- Project and artifact management
- Basic AI assistant
- Tab-based navigation

**Phase 2: Auto-Save & Draft State** (Planned)
- localStorage/IndexedDB persistence
- Debounced auto-save
- Draft recovery on reload
- **Effort**: 1 week

**Phase 3: Multi-User UI** (Planned)
- ConflictResolutionView
- Conflict notifications
- Resync button
- **Effort**: 1-2 weeks

**Phase 4: Export UI** (Planned)
- ExportManager component
- Template editor
- Preview functionality
- **Effort**: 1-2 weeks

**Phase 5: Advanced AI UI** (Planned)
- TaskManager component
- Enhanced assistant
- File upload interface
- **Effort**: 1 week

**Phase 6: User Management UI** (Planned)
- UserManagement component
- OAuth login flow
- Session display
- **Effort**: 1 week

### 14.4 Code Alignment Notes

**Current Implementation**:
- Clean component structure
- Proper React patterns (hooks, props)
- Responsive design basics
- API integration working

**Future Work**:
- Add requirement ID comments in components
- Implement proper error handling
- Add loading states
- Add tooltips and help text
- Implement auto-save
- Add comprehensive tests

---

## 15. Future Enhancements

See **Section 14.2** for detailed list of planned features.

**Priority Recommendations**:
1. **Auto-save draft state** - Critical for data safety, high user value
2. **Loading states & error handling** - Better UX, medium effort
3. **Tooltips and help** - Improves usability, low effort
4. **Export UI** - High user value, medium effort

---

## 16. Development Guidelines

### 16.1 Component Creation

**Template**:
```jsx
import React, { useState, useEffect } from 'react';
import './ComponentName.css';

function ComponentName({ prop1, prop2 }) {
  const [state, setState] = useState(initialValue);
  
  useEffect(() => {
    // Side effects
  }, [dependencies]);
  
  const handleAction = () => {
    // Event handler
  };
  
  return (
    <div className="component-name">
      {/* JSX */}
    </div>
  );
}

export default ComponentName;
```

### 16.2 Naming Conventions

- **Components**: PascalCase (e.g., `ProjectList`)
- **Files**: PascalCase for components (e.g., `ProjectList.jsx`)
- **CSS Classes**: kebab-case (e.g., `project-list-container`)
- **Functions**: camelCase (e.g., `handleCreateProject`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

### 16.3 Code Style

- **Indentation**: 2 spaces
- **Quotes**: Single quotes for JSX attributes, strings
- **Semicolons**: Required
- **Arrow Functions**: Preferred for event handlers
- **Destructuring**: Use for props and state

---

## 17. References

- [React Documentation](https://react.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Vite Documentation](https://vite.dev/)
- [ESLint React Plugin](https://github.com/jsx-eslint/eslint-plugin-react)
- [REQUIREMENTS.md](file:///c:/projects/sealmit/REQUIREMENTS.md) - System requirements
- [ARCHITECTURE.md](file:///c:/projects/sealmit/ARCHITECTURE.md) - System architecture
