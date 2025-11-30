from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class TraceType(str, Enum):
    SATISFIES = "satisfies"
    VERIFIES = "verifies"
    MITIGATES = "mitigates"
    CAUSES = "causes"

class ArtifactType(str, Enum):
    REQUIREMENT = "requirement"
    RISK_HAZARD = "risk_hazard"
    RISK_CAUSE = "risk_cause"
    VERIFICATION_ACTIVITY = "verification_activity"

class Trace(BaseModel):
    source_id: str
    target_id: str
    type: TraceType
    description: Optional[str] = None

class BaseArtifact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ArtifactType
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    attributes: Dict[str, Any] = Field(default_factory=dict)

class Requirement(BaseArtifact):
    type: ArtifactType = ArtifactType.REQUIREMENT
    level: str  # e.g., "User", "System", "Performance"
    parent_id: Optional[str] = None  # Deprecated, kept for backward compatibility
    parent_ids: List[str] = Field(default_factory=list)  # Multiple parents support
    justification: Optional[str] = None  # Rationale for the requirement

class RiskHazard(BaseArtifact):
    type: ArtifactType = ArtifactType.RISK_HAZARD
    severity: Optional[str] = None

class RiskCause(BaseArtifact):
    type: ArtifactType = ArtifactType.RISK_CAUSE
    probability: Optional[str] = None

class VerificationMethod(str, Enum):
    TEST = "test"
    ANALYSIS = "analysis"
    REVIEW = "review"

class VerificationActivity(BaseArtifact):
    type: ArtifactType = ArtifactType.VERIFICATION_ACTIVITY
    method: VerificationMethod
    procedure: Optional[str] = None
    setup: Optional[str] = None
    passed: bool = False

class RequirementLevel(BaseModel):
    """Requirement level with name and description."""
    name: str
    description: str = ""

class ProjectSettings(BaseModel):
    """Project-wide settings for validation and behavior."""
    enforce_single_parent: bool = False  # If True, requirements can only have one parent
    prevent_orphans_at_lower_levels: bool = False  # If True, non-top-level requirements must have parents

class ProjectConfig(BaseModel):
    name: str
    levels: List[Union[str, RequirementLevel]] = Field(default_factory=lambda: [
        RequirementLevel(name="User", description="User-facing requirements"),
        RequirementLevel(name="System", description="System-level requirements")
    ])
    risk_matrix: Dict[str, Any] = {}
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    
    def get_level_names(self) -> List[str]:
        """Get list of level names, handling both old (str) and new (RequirementLevel) formats."""
        return [level.name if isinstance(level, RequirementLevel) else level for level in self.levels]
    
    def get_top_level_name(self) -> Optional[str]:
        """Get the name of the top-level requirement level."""
        if self.levels:
            first_level = self.levels[0]
            return first_level.name if isinstance(first_level, RequirementLevel) else first_level
        return None

class ProjectState(BaseModel):
    config: ProjectConfig
    artifacts: Dict[str, Union[Requirement, RiskHazard, RiskCause, VerificationActivity, BaseArtifact]]
    traces: List[Trace]
