# SEALMit - Backend Detailed Design

## 1. Overview

The SEALMit backend is a Python-based REST API built with **FastAPI**, providing comprehensive project management, artifact lifecycle, and version control capabilities. The backend follows a layered architecture with clear separation between API routes, business logic (models), and data persistence (storage).

---

## 2. Module Structure

### 2.1 Directory Layout

```
backend/
├── api/                        # API route modules
│   ├── __init__.py
│   ├── projects.py            # Project management endpoints
│   ├── artifacts.py           # Artifact and trace CRUD
│   └── ai.py                  # AI assistant integration
├── main.py                    # FastAPI application entry point
├── asig_server.py             # ASIG web server (serves frontend + API)
├── desktop_app.py             # Desktop application launcher
├── models.py                  # Pydantic data models
├── storage.py                 # Git-based XML storage layer
├── pyproject.toml             # Dependencies and project metadata
└── README.md                  # Backend-specific documentation
```

### 2.2 Module Responsibilities

| Module | Responsibility | Key Components |
|--------|---------------|----------------|
| **models.py** | Data structures and validation | Enums, Pydantic models |
| **storage.py** | Persistence and version control | GitStorage class |
| **api/projects.py** | Project lifecycle management | List, create, get projects |
| **api/artifacts.py** | Artifact and trace operations | CRUD for artifacts and traces |
| **api/ai.py** | AI assistant integration | Chat endpoint |
| **main.py** | FastAPI application setup | CORS, routing, middleware |
| **asig_server.py** | Web deployment server | Static file serving, API proxy |
| **desktop_app.py** | Desktop deployment launcher | PyWebView integration |

---

## 3. Data Models (`models.py`)

### 3.1 Enumerations

#### TraceType
```python
class TraceType(str, Enum):
    SATISFIES = "satisfies"    # Design satisfies requirement
    VERIFIES = "verifies"      # Verification verifies requirement
    MITIGATES = "mitigates"    # Control mitigates risk
    CAUSES = "causes"          # Cause leads to hazard
```

**Usage**: Defines valid trace relationship types between artifacts.

#### ArtifactType
```python
class ArtifactType(str, Enum):
    REQUIREMENT = "requirement"
    RISK_HAZARD = "risk_hazard"
    RISK_CAUSE = "risk_cause"
    VERIFICATION_ACTIVITY = "verification_activity"
```

**Usage**: Discriminator for artifact polymorphism.

#### VerificationMethod
```python
class VerificationMethod(str, Enum):
    TEST = "test"              # Physical or software testing
    ANALYSIS = "analysis"      # Mathematical or simulation analysis
    REVIEW = "review"          # Design review or inspection
```

**Usage**: Categorizes verification approaches.

### 3.2 Core Models

#### Trace
```python
class Trace(BaseModel):
    source_id: str                    # UUID of source artifact
    target_id: str                    # UUID of target artifact
    type: TraceType                   # Relationship type
    description: Optional[str] = None # Optional explanation
```

**Purpose**: Represents a traceability link between two artifacts.

**Validation**:
- Source and target IDs must reference existing artifacts
- Type must be valid TraceType enum value

#### BaseArtifact
```python
class BaseArtifact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ArtifactType
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    attributes: Dict[str, Any] = Field(default_factory=dict)
```

**Purpose**: Base class for all artifact types.

**Fields**:
- `id`: Auto-generated UUID (immutable after creation)
- `type`: Artifact type discriminator
- `title`: Human-readable title (required)
- `description`: Detailed description (optional)
- `created_at`: Timestamp of creation (auto-generated)
- `updated_at`: Timestamp of last modification (auto-updated)
- `attributes`: Extensible key-value storage for custom fields

### 3.3 Specialized Artifacts

#### Requirement
```python
class Requirement(BaseArtifact):
    type: ArtifactType = ArtifactType.REQUIREMENT
    level: str                        # e.g., "User", "System", "Performance"
    parent_id: Optional[str] = None   # UUID of parent requirement
```

**Purpose**: Represents a system requirement at any level.

**Hierarchy**: Requirements can form parent-child relationships via `parent_id`.

**Levels**: Configurable per project (e.g., User, System, Performance, Interface).

#### RiskHazard
```python
class RiskHazard(BaseArtifact):
    type: ArtifactType = ArtifactType.RISK_HAZARD
    severity: Optional[str] = None    # e.g., "Catastrophic", "Critical", "Marginal"
```

**Purpose**: Represents an identified hazard or risk.

**Severity**: Typically from a risk matrix (configurable per project).

#### RiskCause
```python
class RiskCause(BaseArtifact):
    type: ArtifactType = ArtifactType.RISK_CAUSE
    probability: Optional[str] = None # e.g., "Frequent", "Probable", "Remote"
```

**Purpose**: Represents a cause that can lead to a hazard.

**Probability**: Typically from a risk matrix (configurable per project).

**Traceability**: Use CAUSES trace to link to RiskHazard.

#### VerificationActivity
```python
class VerificationActivity(BaseArtifact):
    type: ArtifactType = ArtifactType.VERIFICATION_ACTIVITY
    method: VerificationMethod        # TEST, ANALYSIS, or REVIEW
    procedure: Optional[str] = None   # Test procedure or analysis method
    setup: Optional[str] = None       # Test setup or configuration
    passed: bool = False              # Pass/fail status
```

**Purpose**: Represents a verification activity (test, analysis, or review).

**Workflow**:
1. Create verification activity with procedure and setup
2. Execute verification
3. Update `passed` field with result
4. Create VERIFIES trace to requirement

### 3.4 Project Models

#### ProjectConfig
```python
class ProjectConfig(BaseModel):
    name: str                         # Project name (unique identifier)
    levels: List[str] = ["User", "System"]  # Requirement levels
    risk_matrix: Dict[str, Any] = {}  # Risk assessment configuration
```

**Purpose**: Project-wide configuration and settings.

**Validation**:
- Name must be 1-100 characters, alphanumeric + underscores/hyphens
- Levels list defines valid requirement levels
- Risk matrix is extensible for future risk assessment features

#### ProjectState
```python
class ProjectState(BaseModel):
    config: ProjectConfig
    artifacts: Dict[str, BaseArtifact]  # Keyed by artifact ID
    traces: List[Trace]
```

**Purpose**: Complete snapshot of project data.

**Usage**: 
- Loaded from XML files by storage layer
- Passed to API endpoints for manipulation
- Saved back to XML files

---

## 4. Storage Layer (`storage.py`)

### 4.1 GitStorage Class

The `GitStorage` class provides Git-based persistence with XML serialization.

#### Constructor
```python
def __init__(self, project_path: str):
    """Initialize Git storage for a project."""
```

**Responsibilities**:
- Set up project paths (artifacts directory)
- Initialize or open Git repository
- Create initial commit if new repository

#### Key Methods

##### `_init_repo()`
```python
def _init_repo(self):
    """Initialize or open Git repository."""
```

**Behavior**:
- If `.git` exists: Open existing repository
- If not: Initialize new repository with initial commit

##### `save_draft(state: ProjectState)`
```python
def save_draft(self, state: ProjectState):
    """Save project state to XML files without committing."""
```

**Process**:
1. Serialize `ProjectConfig` to `project.xml`
2. Serialize each artifact to `artifacts/{uuid}.xml`
3. Serialize all traces to `traces.xml`
4. Write files to disk (no Git commit)

**XML Serialization**:
- Uses `xml.etree.ElementTree` for XML generation
- UTF-8 encoding with XML declaration
- Pretty-printed for readability

##### `_save_artifact(artifact: BaseArtifact)`
```python
def _save_artifact(self, artifact: BaseArtifact):
    """Save a single artifact to XML file."""
```

**File Naming**: `artifacts/{artifact.id}.xml`

**XML Structure**:
```xml
<Artifact>
  <ID>uuid</ID>
  <Type>requirement</Type>
  <Title>...</Title>
  <Description>...</Description>
  <CreatedAt>2025-11-29T12:00:00</CreatedAt>
  <UpdatedAt>2025-11-29T12:00:00</UpdatedAt>
  <!-- Type-specific fields -->
  <Level>System</Level>
  <ParentID>parent-uuid</ParentID>
</Artifact>
```

##### `load_project()`
```python
def load_project(self) -> ProjectState:
    """Load project state from XML files."""
```

**Process**:
1. Parse `project.xml` → `ProjectConfig`
2. Parse `traces.xml` → `List[Trace]`
3. Parse each `artifacts/*.xml` → `BaseArtifact` (polymorphic)
4. Reconstruct `ProjectState`

**Polymorphic Deserialization**:
- Read `<Type>` element to determine artifact class
- Instantiate appropriate subclass (Requirement, RiskHazard, etc.)
- Populate type-specific fields

##### `commit(message: str)`
```python
def commit(self, message: str):
    """Commit all changes to Git repository."""
```

**Process**:
1. Stage all files (`git add .`)
2. Create commit with provided message
3. Log commit hash

**Error Handling**: Raises exception if commit fails.

##### `get_history()`
```python
def get_history(self):
    """Get Git commit history."""
```

**Returns**: List of commits with hash, author, date, message.

##### `checkout(commit_hash: str)`
```python
def checkout(self, commit_hash: str):
    """Restore project to a previous commit."""
```

**Warning**: Destructive operation, overwrites current state.

### 4.2 XML Schema Design

#### Project Configuration
```xml
<?xml version="1.0" encoding="utf-8"?>
<ProjectConfig>
  <Name>ProjectName</Name>
  <Levels>
    <Level>User</Level>
    <Level>System</Level>
  </Levels>
</ProjectConfig>
```

#### Traces
```xml
<?xml version="1.0" encoding="utf-8"?>
<Traces>
  <Trace>
    <SourceID>uuid-1</SourceID>
    <TargetID>uuid-2</TargetID>
    <Type>verifies</Type>
    <Description>Optional description</Description>
  </Trace>
</Traces>
```

#### Artifact (Requirement Example)
```xml
<?xml version="1.0" encoding="utf-8"?>
<Artifact>
  <ID>uuid</ID>
  <Type>requirement</Type>
  <Title>System shall respond within 2 seconds</Title>
  <Description>Performance requirement for API</Description>
  <CreatedAt>2025-11-29T10:00:00</CreatedAt>
  <UpdatedAt>2025-11-29T12:00:00</UpdatedAt>
  <Level>Performance</Level>
  <ParentID>parent-uuid</ParentID>
</Artifact>
```

---

## 5. API Endpoints

### 5.1 Projects API (`api/projects.py`)

#### List Projects
```http
GET /api/projects/
```

**Response**: `List[str]` - Array of project names

**Implementation**:
```python
@router.get("/", response_model=List[str])
def list_projects():
    # List directories in PROJECTS_ROOT
    # Return directory names
```

**Error Handling**:
- Returns empty list if projects directory doesn't exist
- Returns 500 if filesystem error occurs

#### Create Project
```http
POST /api/projects/
Content-Type: application/json

{
  "name": "MyProject",
  "levels": ["User", "System", "Performance"],
  "risk_matrix": {}
}
```

**Response**: `ProjectConfig` - Created project configuration

**Validation**:
- Name: 1-100 characters, alphanumeric + underscores/hyphens
- Name must be unique (no existing project with same name)

**Implementation**:
```python
@router.post("/", response_model=ProjectConfig)
def create_project(config: ProjectConfig):
    # Validate project name
    # Check if project already exists
    # Create project directory
    # Initialize GitStorage
    # Create initial ProjectState
    # Save and commit
```

**Error Handling**:
- 400: Invalid project name or duplicate name
- 500: Filesystem or Git error

#### Get Project
```http
GET /api/projects/{name}
```

**Response**: `ProjectState` - Complete project state

**Implementation**:
```python
@router.get("/{name}", response_model=ProjectState)
def get_project(name: str):
    # Check if project exists
    # Load project via GitStorage
    # Return ProjectState
```

**Error Handling**:
- 404: Project not found
- 500: Load error

### 5.2 Artifacts API (`api/artifacts.py`)

#### Create Artifact
```http
POST /api/artifacts/{project_name}/artifacts
Content-Type: application/json

{
  "type": "requirement",
  "title": "User shall be able to login",
  "level": "User",
  "parent_id": null
}
```

**Response**: `BaseArtifact` - Created artifact (polymorphic)

**Implementation**:
```python
@router.post("/{project_name}/artifacts", response_model=BaseArtifact)
def create_artifact(
    project_name: str, 
    artifact: Union[Requirement, RiskHazard, RiskCause, VerificationActivity]
):
    # Load project state
    # Validate artifact ID is unique
    # Add artifact to state
    # Save draft (no commit)
```

**Polymorphism**: Request body type determined by `type` field.

**Error Handling**:
- 400: Duplicate artifact ID
- 404: Project not found
- 500: Save error

#### Update Artifact
```http
PUT /api/artifacts/{project_name}/artifacts/{artifact_id}
Content-Type: application/json

{
  "id": "artifact-uuid",
  "type": "requirement",
  "title": "Updated title",
  ...
}
```

**Response**: `BaseArtifact` - Updated artifact

**Validation**:
- Artifact ID in URL must match ID in body
- Artifact must exist

**Implementation**:
```python
@router.put("/{project_name}/artifacts/{artifact_id}", response_model=BaseArtifact)
def update_artifact(project_name: str, artifact_id: str, artifact: ...):
    # Load project state
    # Validate artifact exists
    # Validate ID match
    # Update artifact in state
    # Save draft
```

**Error Handling**:
- 400: ID mismatch
- 404: Artifact not found
- 500: Save error

#### Delete Artifact
```http
DELETE /api/artifacts/{project_name}/artifacts/{artifact_id}
```

**Response**: `{"status": "success", "traces_removed": N}`

**Cascade Behavior**: Automatically deletes all traces referencing the artifact.

**Implementation**:
```python
@router.delete("/{project_name}/artifacts/{artifact_id}")
def delete_artifact(project_name: str, artifact_id: str):
    # Load project state
    # Validate artifact exists
    # Remove artifact from state
    # Remove all traces referencing artifact
    # Save draft
```

**Error Handling**:
- 404: Artifact not found
- 500: Delete error

#### Create Trace
```http
POST /api/artifacts/{project_name}/traces
Content-Type: application/json

{
  "source_id": "uuid-1",
  "target_id": "uuid-2",
  "type": "verifies",
  "description": "Test verifies requirement"
}
```

**Response**: `Trace` - Created trace

**Validation**:
- Source and target artifacts must exist
- No duplicate traces (same source, target, and type)

**Implementation**:
```python
@router.post("/{project_name}/traces", response_model=Trace)
def create_trace(project_name: str, trace: Trace):
    # Load project state
    # Validate source and target exist
    # Check for duplicate trace
    # Add trace to state
    # Save draft
```

**Error Handling**:
- 400: Invalid artifact IDs or duplicate trace
- 404: Project not found
- 500: Save error

#### Commit Changes
```http
POST /api/artifacts/{project_name}/commit
Content-Type: application/json

{
  "message": "Added new requirements"
}
```

**Response**: `{"status": "committed", "message": "..."}`

**Validation**: Message cannot be empty.

**Implementation**:
```python
@router.post("/{project_name}/commit")
def commit_changes(project_name: str, message: str):
    # Validate message not empty
    # Get storage
    # Commit with message
```

**Error Handling**:
- 400: Empty message
- 404: Project not found
- 500: Commit error

### 5.3 AI API (`api/ai.py`)

#### Chat with AI
```http
POST /api/ai/chat
Content-Type: application/json

{
  "message": "How do I create a requirement?",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response**: `{"response": "AI response text"}`

**Current Implementation**: Placeholder (returns canned response).

**Planned**: Full Strands Agents integration with project context.

---

## 6. Application Entry Points

### 6.1 FastAPI Application (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import projects, artifacts, ai

app = FastAPI(title="SEALMit API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
```

**Purpose**: Main FastAPI application with CORS and routing.

**Port**: 8000 (default for Uvicorn)

**Run**: `uv run uvicorn main:app --reload --port 8000`

### 6.2 ASIG Server (`asig_server.py`)

**Purpose**: Serve React frontend and proxy API requests.

**Architecture**:
- Serves static files from `../frontend/dist/`
- Proxies `/api/*` requests to FastAPI backend
- Single port (8080) for both frontend and API

**Run**: `uv run python asig_server.py`

### 6.3 Desktop Application (`desktop_app.py`)

**Purpose**: Launch desktop application with PyWebView.

**Architecture**:
- Starts FastAPI server in background thread
- Opens PyWebView window pointing to localhost
- Provides native window experience

**Run**: `uv run python desktop_app.py`

---

## 7. Dependencies (`pyproject.toml`)

```toml
[project]
name = "sealmit-backend"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.122.0",
    "uvicorn>=0.38.0",
    "pydantic>=2.12.5",
    "gitpython>=3.1.45",
    "pywebview>=6.1",
    "strands-agents>=1.18.0",
]
```

**Package Manager**: `uv` for fast, reliable dependency management.

**Python Version**: 3.11+ required for modern type hints.

---

## 8. Code Quality

### 8.1 Type Hints

**Requirement**: All functions must have type hints.

**Example**:
```python
def get_storage(project_name: str) -> GitStorage:
    """Get GitStorage instance for a project."""
    project_path = os.path.join(PROJECTS_ROOT, project_name)
    return GitStorage(project_path)
```

### 8.2 Linting and Formatting

**Tool**: Ruff (extremely fast Python linter and formatter)

**Configuration**: Follows PEP 8 with project-specific overrides.

**Run**: `ruff check .` and `ruff format .`

### 8.3 Type Checking

**Tool**: MyPy (static type checker)

**Run**: `mypy .`

**Goal**: Zero type errors in production code.

### 8.4 Logging

**Strategy**: Comprehensive logging at INFO level.

**Pattern**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Creating project: {name}")
logger.warning(f"Project already exists: {name}")
logger.error(f"Error creating project: {str(e)}")
```

**Benefits**:
- Debugging and troubleshooting
- Audit trail
- Performance monitoring

---

## 9. Error Handling

### 9.1 HTTP Exception Pattern

```python
try:
    # Business logic
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise HTTPException(status_code=500, detail="Error message")
```

**Benefits**:
- Consistent error responses
- Proper HTTP status codes
- Logged errors for debugging

### 9.2 Common Status Codes

| Code | Usage |
|------|-------|
| **200** | Successful GET, PUT, DELETE |
| **201** | Successful POST (resource created) |
| **400** | Invalid input, validation error |
| **404** | Resource not found |
| **500** | Internal server error |

---

## 10. Testing Strategy

### 10.1 Verification Scripts

**Location**: Project root

**Scripts**:
### 10.3 Manual Testing

**Approach**: Use API client (Postman, curl, or browser) to test workflows.

**Example Workflow**:
1. Create project
2. Add requirements
3. Add risks
4. Create traces
5. Commit changes
6. Verify Git history

---

## 11. Implementation Status

### 11.1 ✅ Fully Implemented (Core Features)

The following features are **fully implemented** and align with REQUIREMENTS.md core requirements:

#### Data Models (Section 3)
- ✅ All enumerations (TraceType, ArtifactType, VerificationMethod)
- ✅ All core models (Trace, BaseArtifact, ProjectConfig, ProjectState)
- ✅ All specialized artifacts (Requirement, RiskHazard, RiskCause, VerificationActivity)
- **Requirements**: FR-REQ-001 through FR-REQ-008, FR-RISK-001 through FR-RISK-007, FR-VER-001 through FR-VER-006

#### Git Storage Layer (Section 4)
- ✅ GitStorage class with full Git integration
- ✅ XML serialization/deserialization
- ✅ Draft state management (save without commit)
- ✅ Commit functionality
- ✅ History retrieval
- ✅ Checkout previous states
- **Requirements**: FR-VC-001 through FR-VC-007, FR-DS-001 through FR-DS-005

#### Projects API (Section 5.1)
- ✅ List projects (GET /api/projects/)
- ✅ Create project (POST /api/projects/)
- ✅ Get project state (GET /api/projects/{name})
- ✅ Project name validation
- ✅ Error handling and logging
- **Requirements**: FR-PM-001 through FR-PM-005

#### Artifacts API (Section 5.2)
- ✅ Create artifact (POST /{project}/artifacts)
- ✅ Update artifact (PUT /{project}/artifacts/{id})
- ✅ Delete artifact (DELETE /{project}/artifacts/{id})
- ✅ Create trace (POST /{project}/traces)
- ✅ Commit changes (POST /{project}/commit)
- ✅ Polymorphic artifact handling
- ✅ Trace validation and duplicate detection
- ✅ Cascade delete for traces
- **Requirements**: FR-TRC-001 through FR-TRC-008

#### AI API (Section 5.3)
- ✅ Basic chat endpoint (placeholder implementation)
- **Requirements**: FR-AI-001, FR-AI-002 (partial)

#### Application Entry Points (Section 6)
- ✅ FastAPI application with CORS
- ✅ ASIG server for web deployment
- ✅ Desktop application launcher
- **Requirements**: NFR-PORT-001, NFR-PORT-002

### 11.2 ⏳ Planned (Advanced Features)

The following features are **documented in REQUIREMENTS.md and ARCHITECTURE.md** but **not yet implemented**:

#### Advanced Risk Traceability
- ❌ Transitive trace resolution algorithm
- ❌ Cause-hazard-requirement combination support
- ❌ Flexible trace patterns (req→cause, req→hazard, req→combo)
- ❌ Automatic trace propagation
- **Requirements**: FR-RISK-008 through FR-RISK-012
- **Documentation**: ARCHITECTURE.md Section 4.4

#### Partial Verification
- ❌ Automatic sub-requirement verification
- ❌ Verification coverage calculation
- ❌ Partial verification propagation to parents
- ❌ Test case combinations (procedure + setup)
- **Requirements**: FR-VER-007 through FR-VER-010
- **Documentation**: ARCHITECTURE.md Section 4.4

#### Multi-User Collaboration
- ❌ Per-user draft state management
- ❌ Conflict detection (three-way merge)
- ❌ Conflict resolution API endpoints
- ❌ Resync functionality
- ❌ Auto-save backend support
- ❌ WebSocket real-time updates
- **Requirements**: FR-COLLAB-001 through FR-COLLAB-010
- **Documentation**: ARCHITECTURE.md Section 9.2
- **API Endpoints** (planned):
  - `GET /api/projects/{name}/conflicts`
  - `POST /api/projects/{name}/resync`
  - `POST /api/projects/{name}/resolve`

#### AI Orchestrator & RAG
- ❌ Worker agent management
- ❌ Parallel tool execution
- ❌ Background task queue (Celery/RQ)
- ❌ Long-running task management
- ❌ RAG knowledge base with vector search
- ❌ Source code indexing pipeline
- ❌ Code-aware assistance
- ❌ File upload analysis
- ❌ Configurable LLM API
- **Requirements**: FR-AI-006 through FR-AI-019
- **Documentation**: ARCHITECTURE.md Section 7.2
- **Dependencies** (needed):
  - `celery` or `rq` - Task queue
  - `qdrant-client` or `chromadb` - Vector database
  - `sentence-transformers` - Embeddings
  - `tree-sitter` - Code parsing

#### Export System
- ❌ Template engine (Jinja2)
- ❌ Export script generation
- ❌ Multiple format support (MD, CSV, XLS, PDF)
- ❌ Markdown renderer
- ❌ PDF generator (WeasyPrint/ReportLab)
- ❌ Repeatable export scripts
- **Requirements**: FR-EXP-001 through FR-EXP-010
- **Documentation**: ARCHITECTURE.md Section 7.3
- **API Endpoints** (planned):
  - `GET /api/export/templates`
  - `POST /api/export/templates`
  - `POST /api/export/generate`
  - `POST /api/export/scripts`
  - `POST /api/export/scripts/{id}/execute`
- **Dependencies** (needed):
  - `jinja2` - Template engine
  - `weasyprint` or `reportlab` - PDF generation
  - `pandas` - CSV/Excel export

#### User Management & OAuth
- ❌ OAuth integration (Authlib)
- ❌ User account management
- ❌ Session management
- ❌ User attribution for commits
- ❌ Role-based access control
- **Requirements**: FR-USER-001 through FR-USER-007
- **Documentation**: ARCHITECTURE.md Section 7.4
- **API Endpoints** (planned):
  - `GET /auth/login`
  - `GET /auth/callback`
  - `POST /auth/logout`
  - `GET /api/users`
  - `POST /api/users`
- **Dependencies** (needed):
  - `authlib` - OAuth integration
  - `redis` - Session storage

### 11.3 Implementation Roadmap

**Phase 1: Core Features** ✅ **COMPLETE**
- Data models
- Git storage
- Basic APIs
- Web and desktop deployment

**Phase 2: Multi-User** (Planned)
- Per-user draft state
- Conflict detection and resolution
- Auto-save backend support
- **Effort**: 2-3 weeks

**Phase 3: AI Orchestrator** (Planned)
- Worker agents and task queue
- RAG knowledge base
- Source code indexing
- Code-aware assistance
- **Effort**: 3-4 weeks

**Phase 4: Export System** (Planned)
- Template engine
- Export scripts
- Multiple formats
- PDF generation
- **Effort**: 1-2 weeks

**Phase 5: User Management** (Planned)
- OAuth integration
- User accounts
- Session management
- **Effort**: 1-2 weeks

### 11.4 Code Alignment Notes

**Current Implementation**:
- Code is clean, well-structured, and follows architecture
- All core requirements are satisfied
- Proper error handling and logging throughout
- Type hints and validation in place

**Future Work**:
- Add requirement ID comments in code (e.g., `# Implements FR-REQ-001`)
- Extract hardcoded paths to configuration
- Add comprehensive unit tests
- Implement advanced features per roadmap

---

## 12. Future Enhancements

See **Section 11.2** for detailed list of planned features.

**Priority Recommendations**:
1. **Auto-save draft state** - High user value, medium effort
2. **RAG knowledge base** - Unique differentiator, high value
3. **Export templates** - High user value, medium effort
4. **Multi-user collaboration** - Enterprise feature, high effort

---

## 13. References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [REQUIREMENTS.md](file:///c:/projects/sealmit/REQUIREMENTS.md) - System requirements
- [ARCHITECTURE.md](file:///c:/projects/sealmit/ARCHITECTURE.md) - System architecture
- `verify_asig.py`: Test ASIG server
- `verify_ai.py`: Test AI integration

**Run**: `python verify_backend.py`

### 10.2 Future Testing

**Planned**:
- Unit tests for models and storage layer (pytest)
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Performance tests for large projects

---

## 11. Development Workflow

### 11.1 Setup

```bash
cd backend
uv sync                    # Install dependencies
uv run uvicorn main:app --reload --port 8000  # Run dev server
```

### 11.2 Code Quality Checks

```bash
ruff check .               # Lint code
ruff format .              # Format code
mypy .                     # Type check
```

### 11.3 Adding New Artifact Type

1. Add enum value to `ArtifactType` in `models.py`
2. Create new class inheriting from `BaseArtifact`
3. Update `_save_artifact()` in `storage.py` for serialization
4. Update `load_project()` in `storage.py` for deserialization
5. Update API type hints in `api/artifacts.py`

### 11.4 Adding New API Endpoint

1. Create route handler in appropriate API module
2. Define request/response models
3. Add validation logic
4. Implement error handling
5. Update API documentation

---

## 12. Future Enhancements

### 12.1 Planned Features

- **Database Caching**: PostgreSQL/SQLite for faster queries
- **Authentication**: OAuth 2.0 integration
- **WebSockets**: Real-time updates for collaboration
- **Batch Operations**: Bulk create/update/delete
- **Advanced Queries**: Filter, search, pagination
- **Export/Import**: ReqIF, CSV, JSON formats
- **Audit Logging**: Track all modifications with user attribution

### 12.2 Performance Optimizations

- **Lazy Loading**: Load artifacts on-demand instead of entire project
- **Caching**: Cache frequently accessed projects in memory
- **Async I/O**: Leverage FastAPI's async capabilities for file operations
- **Compression**: Compress large XML files

---

## 13. References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
