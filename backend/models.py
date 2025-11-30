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
    parent_id: Optional[str] = None

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

class ProjectConfig(BaseModel):
    name: str
    levels: List[str] = ["User", "System"]
    risk_matrix: Dict[str, Any] = {}

class ProjectState(BaseModel):
    config: ProjectConfig
    artifacts: Dict[str, Union[Requirement, RiskHazard, RiskCause, VerificationActivity, BaseArtifact]]
    traces: List[Trace]
