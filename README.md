# SEALMit - Engineering Lifecycle Management System

**SEALMit** is a comprehensive Engineering Lifecycle Management (ELM) application that provides flexible infrastructure and tooling for managing engineering projects with full traceability, integrated risk management, and version-controlled data.

---

## ✨ Key Features

- 🎯 **Multi-level Requirements Management** - Hierarchical requirements with configurable levels
- ⚠️ **Integrated Risk Management** - Hazard identification, cause analysis, and risk mitigation tracking
- ✅ **Verification Activities** - Test, analysis, and review tracking with pass/fail status
- 🔗 **Full Traceability** - Complete trace relationships (Satisfies, Verifies, Mitigates, Causes)
- 📝 **Git-based Version Control** - Every change tracked with full revision history
- � **Multi-User Collaboration** - Conflict detection, resolution, and draft management
- 🧠 **RAG Knowledge Base** - AI-powered source code analysis and troubleshooting
- 📤 **Advanced Export** - Template-based export to PDF, CSV, and more
- �🤖 **AI Assistant** - Integrated AI guidance and support (Strands Agents)
- 🌐 **Dual Deployment** - Web application (ASIG) or standalone desktop app
- ⚡ **Modern Tech Stack** - FastAPI backend + React frontend

---

## 📚 Documentation

Comprehensive documentation is organized following software engineering best practices:

| Document | Description |
|----------|-------------|
| **[REQUIREMENTS.md](REQUIREMENTS.md)** | System requirements specification (151 requirements) |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | High-level system architecture and design decisions |
| **[DETAILED_DESIGN_BACKEND.md](DETAILED_DESIGN_BACKEND.md)** | Backend implementation details & status |
| **[DETAILED_DESIGN_FRONTEND.md](DETAILED_DESIGN_FRONTEND.md)** | Frontend implementation details & status |
| **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** | Testing architecture and approach |
| **[KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)** | Comprehensive project knowledge base |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **uv** (Python package manager) - [Install uv](https://github.com/astral-sh/uv)
- **Git**

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Run development server (API only, port 8000)
uv run uvicorn main:app --reload --port 8000

# OR run ASIG server (serves frontend + API, port 8080)
uv run python asig_server.py

# OR run desktop application
uv run python desktop_app.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (port 5173)
npm run dev

# Build for production
npm run build
```

---

## 🏗️ Technology Stack

### Backend
- **Python** 3.11+ - Modern, type-safe backend
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and serialization
- **GitPython** - Git repository management
- **PyWebView** - Desktop application wrapper
- **Strands Agents** - AI assistant integration

### Frontend
- **React** 19 - Modern UI framework
- **React Router** 7 - Client-side routing
- **Vite** 7 - Fast build tool and dev server
- **ESLint** - Code quality and linting

### Storage
- **Git** - Version control for all project data
- **XML** - Human-readable, version-control-friendly data format

### Planned Additions
- **Qdrant/Chroma** - Vector database for RAG
- **Celery/RQ** - Background task queue
- **Authlib** - OAuth authentication
- **Jinja2/WeasyPrint** - Export engine

---

## 📁 Project Structure

```
sealmit/
├── backend/                    # Python backend
│   ├── api/                   # API endpoints
│   │   ├── projects.py        # Project management
│   │   ├── artifacts.py       # Artifact CRUD
│   │   └── ai.py              # AI assistant
│   ├── tests/                 # Integration tests
│   │   ├── conftest.py        # Test fixtures
│   │   └── integration/       # API integration tests
│   ├── main.py                # FastAPI application
│   ├── asig_server.py         # Web server
│   ├── desktop_app.py         # Desktop launcher
│   ├── models.py              # Data models
│   ├── storage.py             # Git storage layer
│   └── pyproject.toml         # Dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── tests/             # Integration tests
│   │   │   ├── setup.js       # Test configuration
│   │   │   └── integration/   # Component tests
│   │   ├── App.jsx            # Root component
│   │   └── main.jsx           # Entry point
│   ├── package.json           # Dependencies
│   └── vite.config.js         # Build config
├── projects_data/             # Project repositories
├── REQUIREMENTS.md            # Requirements specification
├── ARCHITECTURE.md            # System architecture
├── DETAILED_DESIGN_BACKEND.md # Backend design
├── DETAILED_DESIGN_FRONTEND.md # Frontend design
├── TESTING_STRATEGY.md        # Testing architecture
└── README.md                  # This file
```

---

## 🎯 Usage

### Create a Project

1. Start the backend server
2. Open the web interface (http://localhost:8080 for ASIG or http://localhost:5173 for dev)
3. Enter a project name and click "Create"
4. Configure requirement levels and risk matrix

### Manage Requirements

1. Navigate to a project
2. Click the "Requirements" tab
3. Create requirements with hierarchical relationships
4. Assign levels (User, System, Performance, etc.)

### Track Risks

1. Navigate to the "Risks" tab
2. Create risk hazards with severity ratings
3. Create risk causes with probability assessments
4. Link causes to hazards with CAUSES traces

### Verify Requirements

1. Navigate to the "Verification" tab
2. Create verification activities (Test, Analysis, Review)
3. Define procedures and test setups
4. Record pass/fail results
5. Link to requirements with VERIFIES traces

### Commit Changes

1. All changes are saved as drafts until you commit them:

```bash
# Via API
curl -X POST http://localhost:8000/api/artifacts/{project}/commit \
  -H "Content-Type: application/json" \
  -d '{"message": "Added new requirements"}'
```

---

## 🔧 Development

### Code Quality

```bash
# Backend
cd backend
ruff check .        # Lint
ruff format .       # Format
mypy .              # Type check

# Frontend
cd frontend
npm run lint        # ESLint
```

### Testing

SEALMit uses a multi-layered testing approach focused on integration testing to ensure reliability while minimizing maintenance overhead.

#### Backend Integration Tests

Tests verify API endpoints, data persistence, and business logic compliance with `DETAILED_DESIGN_BACKEND.md`.

```bash
# Navigate to backend
cd backend

# Run all integration tests
uv run pytest tests/integration/

# Run with verbose output
uv run pytest tests/integration/ -v

# Run specific test file
uv run pytest tests/integration/test_projects.py

# Run specific test
uv run pytest tests/integration/test_projects.py::test_create_project
```

**Coverage**: Project management, artifact CRUD, trace creation, Git commits

#### Frontend Integration Tests

Tests verify component structure, routing, and compliance with `DETAILED_DESIGN_FRONTEND.md`.

```bash
# Navigate to frontend
cd frontend

# Run all tests
npm test

# Run in watch mode (for development)
npm test -- --watch

# Run with UI
npm test -- --ui
```

**Coverage**: ProjectDashboard structure, data fetching, route navigation

#### E2E Testing (Manual/AI-Driven)

End-to-end testing is performed **dynamically** without persistent test scripts:
- Manual exploratory testing by users
- AI agent-driven testing on-demand (future)

See [TESTING_STRATEGY.md](TESTING_STRATEGY.md) for the complete testing architecture.

### Legacy Verification Scripts

```bash
# Quick API smoke test
python verify_backend.py

# Test ASIG server
python verify_asig.py

# Test AI integration
python verify_ai.py

# Comprehensive E2E test
python verify_e2e.py
```


---

## 🚢 Deployment

### Web Application (ASIG)

```bash
# Build frontend
cd frontend
npm run build

# Run ASIG server
cd ../backend
uv run python asig_server.py
```

Access at: http://localhost:8080

### Desktop Application

```bash
# Build frontend
cd frontend
npm run build

# Run desktop app
cd ../backend
uv run python desktop_app.py
```

A native window will open with the application.

---

## 🗺️ Roadmap

### Current Status (Phase 1)
- ✅ Core requirements management
- ✅ Risk management
- ✅ Verification tracking
- ✅ Traceability links
- ✅ Git-based version control
- ✅ Web and desktop deployment
- ✅ Integration testing (backend & frontend)
- ⚠️ AI assistant (placeholder implementation)

### Planned Features (Phases 2-5)
- 🔜 **Multi-User Collaboration**: Conflict resolution, auto-save, draft management
- 🔜 **AI Orchestrator & RAG**: Source code knowledge base, worker agents, code-aware assistance
- 🔜 **Export System**: Templates, PDF/CSV/Excel export, repeatable scripts
- 🔜 **User Management**: OAuth integration, session management, RBAC
- 🔜 **Advanced Traceability**: Transitive traces, partial verification, impact analysis
- 🔜 **Real-time Collaboration**: WebSocket-based live updates

---

## 🤝 Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 (Python) and ESLint rules (JavaScript)
2. **Type Hints**: Use type hints for all Python functions
3. **Documentation**: Document all public APIs and complex logic
4. **Testing**: Write tests for new features
5. **Commits**: Use descriptive commit messages

### Adding New Features

1. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Update [REQUIREMENTS.md](REQUIREMENTS.md) if adding new requirements
3. Implement backend changes (see [DETAILED_DESIGN_BACKEND.md](DETAILED_DESIGN_BACKEND.md))
4. Implement frontend changes (see [DETAILED_DESIGN_FRONTEND.md](DETAILED_DESIGN_FRONTEND.md))
5. Test thoroughly
6. Update documentation

---

## 📄 License

*License information to be added*

---

## 🆘 Troubleshooting

### Frontend not building
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend not starting
```bash
cd backend
uv sync --reinstall
```

### CORS errors
- Ensure frontend dev server is on port 5173
- Check CORS configuration in `backend/main.py`

### Git repository issues
- Each project should have its own `.git` directory
- Check file permissions in `projects_data/`

---

## 📞 Support

For questions, issues, or feature requests, please refer to the documentation:

- **Requirements**: [REQUIREMENTS.md](REQUIREMENTS.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Backend Details**: [DETAILED_DESIGN_BACKEND.md](DETAILED_DESIGN_BACKEND.md)
- **Frontend Details**: [DETAILED_DESIGN_FRONTEND.md](DETAILED_DESIGN_FRONTEND.md)
- **Knowledge Base**: [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)

---

**Built with ❤️ for engineering excellence**
