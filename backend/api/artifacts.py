import os
import logging
from fastapi import APIRouter, HTTPException, Body
from typing import List, Union
from models import ProjectState, BaseArtifact, Requirement, RiskHazard, RiskCause, VerificationActivity, Trace
from storage import GitStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

PROJECTS_ROOT = "c:/projects/sealmit/projects_data"

def get_storage(project_name: str) -> GitStorage:
    """Get GitStorage instance for a project with error handling."""
    try:
        project_path = os.path.join(PROJECTS_ROOT, project_name)
        if not os.path.exists(project_path):
            logger.warning(f"Project not found: {project_name}")
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        return GitStorage(project_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accessing project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error accessing project")

@router.post("/{project_name}/artifacts", response_model=BaseArtifact)
def create_artifact(project_name: str, artifact: Union[Requirement, RiskHazard, RiskCause, VerificationActivity] = Body(...)):
    """Create a new artifact in the project."""
    try:
        logger.info(f"Creating artifact in project {project_name}: {artifact.type}")
        storage = get_storage(project_name)
        state = storage.load_project()
        
        # Validate artifact doesn't already exist
        if artifact.id in state.artifacts:
            logger.warning(f"Artifact {artifact.id} already exists in project {project_name}")
            raise HTTPException(status_code=400, detail="Artifact with this ID already exists")
        
        state.artifacts[artifact.id] = artifact
        storage.save_draft(state)
        
        logger.info(f"Successfully created artifact {artifact.id} in project {project_name}")
        return artifact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating artifact in project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create artifact")

@router.put("/{project_name}/artifacts/{artifact_id}", response_model=BaseArtifact)
def update_artifact(project_name: str, artifact_id: str, artifact: Union[Requirement, RiskHazard, RiskCause, VerificationActivity] = Body(...)):
    """Update an existing artifact."""
    try:
        logger.info(f"Updating artifact {artifact_id} in project {project_name}")
        storage = get_storage(project_name)
        state = storage.load_project()
        
        if artifact_id not in state.artifacts:
            logger.warning(f"Artifact {artifact_id} not found in project {project_name}")
            raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found")
        
        # Ensure ID matches
        if artifact.id != artifact_id:
            logger.warning(f"Artifact ID mismatch: URL={artifact_id}, Body={artifact.id}")
            raise HTTPException(status_code=400, detail="Artifact ID in URL must match ID in request body")
            
        state.artifacts[artifact_id] = artifact
        storage.save_draft(state)
        
        logger.info(f"Successfully updated artifact {artifact_id} in project {project_name}")
        return artifact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating artifact {artifact_id} in project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update artifact")

@router.delete("/{project_name}/artifacts/{artifact_id}")
def delete_artifact(project_name: str, artifact_id: str):
    """Delete an artifact and all its associated traces."""
    try:
        logger.info(f"Deleting artifact {artifact_id} from project {project_name}")
        storage = get_storage(project_name)
        state = storage.load_project()
        
        if artifact_id not in state.artifacts:
            logger.warning(f"Artifact {artifact_id} not found in project {project_name}")
            raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found")
        
        # Count traces that will be removed
        traces_to_remove = [t for t in state.traces if t.source_id == artifact_id or t.target_id == artifact_id]
        
        del state.artifacts[artifact_id]
        state.traces = [t for t in state.traces if t.source_id != artifact_id and t.target_id != artifact_id]
        
        storage.save_draft(state)
        logger.info(f"Successfully deleted artifact {artifact_id} and {len(traces_to_remove)} associated traces")
        return {"status": "success", "traces_removed": len(traces_to_remove)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting artifact {artifact_id} from project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete artifact")

@router.post("/{project_name}/traces", response_model=Trace)
def create_trace(project_name: str, trace: Trace):
    """Create a traceability link between two artifacts."""
    try:
        logger.info(f"Creating trace in project {project_name}: {trace.source_id} -> {trace.target_id} ({trace.type})")
        storage = get_storage(project_name)
        state = storage.load_project()
        
        # Validate IDs
        if trace.source_id not in state.artifacts:
            logger.warning(f"Source artifact {trace.source_id} not found in project {project_name}")
            raise HTTPException(status_code=400, detail=f"Source artifact '{trace.source_id}' not found")
        if trace.target_id not in state.artifacts:
            logger.warning(f"Target artifact {trace.target_id} not found in project {project_name}")
            raise HTTPException(status_code=400, detail=f"Target artifact '{trace.target_id}' not found")
        
        # Check for duplicate traces
        for existing_trace in state.traces:
            if (existing_trace.source_id == trace.source_id and 
                existing_trace.target_id == trace.target_id and 
                existing_trace.type == trace.type):
                logger.warning(f"Duplicate trace detected in project {project_name}")
                raise HTTPException(status_code=400, detail="This trace already exists")
        
        state.traces.append(trace)
        storage.save_draft(state)
        logger.info(f"Successfully created trace in project {project_name}")
        return trace
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trace in project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create trace")

@router.post("/{project_name}/commit")
def commit_changes(project_name: str, message: str = Body(..., embed=True)):
    """Commit all pending changes to Git repository."""
    try:
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Commit message cannot be empty")
        
        logger.info(f"Committing changes to project {project_name}: {message}")
        storage = get_storage(project_name)
        storage.commit(message)
        logger.info(f"Successfully committed changes to project {project_name}")
        return {"status": "committed", "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error committing changes to project {project_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to commit changes")
