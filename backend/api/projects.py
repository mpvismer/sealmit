import os
import re
import logging
from fastapi import APIRouter, HTTPException
from typing import List
from models import ProjectConfig, ProjectState
from storage import GitStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

PROJECTS_ROOT = "c:/projects/sealmit/projects_data"
os.makedirs(PROJECTS_ROOT, exist_ok=True)

def get_storage(project_name: str) -> GitStorage:
    """Get GitStorage instance for a project."""
    project_path = os.path.join(PROJECTS_ROOT, project_name)
    return GitStorage(project_path)

def validate_project_name(name: str) -> bool:
    """Validate project name - alphanumeric, underscores, hyphens only."""
    if not name or len(name) < 1 or len(name) > 100:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))

@router.get("/", response_model=List[str])
def list_projects():
    """List all available projects."""
    try:
        if not os.path.exists(PROJECTS_ROOT):
            logger.info("Projects root directory doesn't exist yet")
            return []
        projects = [d for d in os.listdir(PROJECTS_ROOT) if os.path.isdir(os.path.join(PROJECTS_ROOT, d))]
        logger.info(f"Listed {len(projects)} projects")
        return projects
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list projects")

@router.post("/", response_model=ProjectConfig)
def create_project(config: ProjectConfig):
    """Create a new project with Git repository."""
    try:
        # Validate project name
        if not validate_project_name(config.name):
            logger.warning(f"Invalid project name: {config.name}")
            raise HTTPException(
                status_code=400, 
                detail="Project name must be 1-100 characters and contain only letters, numbers, underscores, and hyphens"
            )
        
        project_path = os.path.join(PROJECTS_ROOT, config.name)
        if os.path.exists(project_path):
            logger.warning(f"Project already exists: {config.name}")
            raise HTTPException(status_code=400, detail=f"Project '{config.name}' already exists")
        
        logger.info(f"Creating new project: {config.name}")
        os.makedirs(project_path)
        storage = GitStorage(project_path)
        
        # Create initial state
        state = ProjectState(config=config, artifacts={}, traces=[])
        storage.save_draft(state)
        storage.commit("Initial project creation")
        
        logger.info(f"Successfully created project: {config.name}")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project {config.name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@router.get("/{name}", response_model=ProjectState)
def get_project(name: str):
    """Get complete project state including config, artifacts, and traces."""
    try:
        project_path = os.path.join(PROJECTS_ROOT, name)
        if not os.path.exists(project_path):
            logger.warning(f"Project not found: {name}")
            raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
        
        logger.info(f"Loading project: {name}")
        storage = GitStorage(project_path)
        state = storage.load_project()
        logger.info(f"Successfully loaded project {name} with {len(state.artifacts)} artifacts and {len(state.traces)} traces")
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading project {name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load project")

