import os
import logging
import git
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
from models import ProjectState, ProjectConfig, BaseArtifact, Trace, ArtifactType, Requirement, RiskHazard, RiskCause, VerificationActivity, VerificationMethod, RequirementLevel, ProjectSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitStorage:
    def __init__(self, project_path: str):
        """Initialize Git storage for a project."""
        self.project_path = project_path
        self.artifacts_path = os.path.join(project_path, "artifacts")
        try:
            os.makedirs(self.artifacts_path, exist_ok=True)
            self.repo = self._init_repo()
            logger.info(f"Initialized GitStorage for project at {project_path}")
        except Exception as e:
            logger.error(f"Failed to initialize GitStorage at {project_path}: {str(e)}")
            raise

    def _init_repo(self) -> git.Repo:
        """Initialize or open Git repository."""
        try:
            if not os.path.exists(os.path.join(self.project_path, ".git")):
                logger.info(f"Creating new Git repository at {self.project_path}")
                repo = git.Repo.init(self.project_path)
                # Create initial commit
                readme_path = os.path.join(self.project_path, "README.md")
                with open(readme_path, "w") as f:
                    f.write("# Engineering Project")
                repo.index.add([readme_path])
                repo.index.commit("Initial commit")
                logger.info("Created initial Git commit")
                return repo
            else:
                logger.info(f"Opening existing Git repository at {self.project_path}")
                return git.Repo(self.project_path)
        except Exception as e:
            logger.error(f"Failed to initialize Git repository: {str(e)}")
            raise

    def save_draft(self, state: ProjectState):
        """Save project state to XML files without committing."""
        try:
            logger.info(f"Saving draft for project at {self.project_path}")
            
            # Save Project Config
            config_root = ET.Element("ProjectConfig")
            ET.SubElement(config_root, "Name").text = state.config.name
            
            # Save Levels (support both old str and new RequirementLevel format)
            levels_elem = ET.SubElement(config_root, "Levels")
            for level in state.config.levels:
                if isinstance(level, RequirementLevel):
                    level_elem = ET.SubElement(levels_elem, "Level")
                    ET.SubElement(level_elem, "Name").text = level.name
                    ET.SubElement(level_elem, "Description").text = level.description
                else:
                    # Backward compatibility: old string format
                    ET.SubElement(levels_elem, "Level").text = level
            
            # Save Settings
            settings_elem = ET.SubElement(config_root, "Settings")
            ET.SubElement(settings_elem, "EnforceSingleParent").text = str(state.config.settings.enforce_single_parent)
            ET.SubElement(settings_elem, "PreventOrphansAtLowerLevels").text = str(state.config.settings.prevent_orphans_at_lower_levels)
            
            tree = ET.ElementTree(config_root)
            ET.indent(tree, space="  ", level=0)
            tree.write(os.path.join(self.project_path, "project.xml"), encoding="utf-8", xml_declaration=True)

            # Save Traces
            traces_root = ET.Element("Traces")
            for trace in state.traces:
                trace_elem = ET.SubElement(traces_root, "Trace")
                ET.SubElement(trace_elem, "SourceID").text = trace.source_id
                ET.SubElement(trace_elem, "TargetID").text = trace.target_id
                ET.SubElement(trace_elem, "Type").text = trace.type.value
                if trace.description:
                    ET.SubElement(trace_elem, "Description").text = trace.description
            
            tree = ET.ElementTree(traces_root)
            ET.indent(tree, space="  ", level=0)
            tree.write(os.path.join(self.project_path, "traces.xml"), encoding="utf-8", xml_declaration=True)

            # Save Artifacts
            for artifact in state.artifacts.values():
                self._save_artifact(artifact)
            
            logger.info(f"Successfully saved draft with {len(state.artifacts)} artifacts and {len(state.traces)} traces")
        except Exception as e:
            logger.error(f"Failed to save draft: {str(e)}")
            raise

    def _save_artifact(self, artifact: BaseArtifact):
        """Save a single artifact to XML file."""
        try:
            root = ET.Element("Artifact")
            ET.SubElement(root, "ID").text = artifact.id
            ET.SubElement(root, "Type").text = artifact.type.value
            ET.SubElement(root, "Title").text = artifact.title
            if artifact.description:
                ET.SubElement(root, "Description").text = artifact.description
            
            # Type specific fields
            if isinstance(artifact, Requirement):
                ET.SubElement(root, "Level").text = artifact.level
                
                # Save parent IDs (support both old parent_id and new parent_ids)
                if artifact.parent_ids:
                    parent_ids_elem = ET.SubElement(root, "ParentIDs")
                    for parent_id in artifact.parent_ids:
                        ET.SubElement(parent_ids_elem, "ParentID").text = parent_id
                elif artifact.parent_id:
                    # Backward compatibility: save old parent_id format
                    ET.SubElement(root, "ParentID").text = artifact.parent_id
                
                # Save justification if present
                if artifact.justification:
                    ET.SubElement(root, "Justification").text = artifact.justification
            elif isinstance(artifact, RiskHazard):
                if artifact.severity:
                    ET.SubElement(root, "Severity").text = artifact.severity
            elif isinstance(artifact, RiskCause):
                if artifact.probability:
                    ET.SubElement(root, "Probability").text = artifact.probability
            elif isinstance(artifact, VerificationActivity):
                ET.SubElement(root, "Method").text = artifact.method.value
                if artifact.procedure:
                    ET.SubElement(root, "Procedure").text = artifact.procedure
                if artifact.setup:
                    ET.SubElement(root, "Setup").text = artifact.setup
                ET.SubElement(root, "Passed").text = str(artifact.passed)

            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(os.path.join(self.artifacts_path, f"{artifact.id}.xml"), encoding="utf-8", xml_declaration=True)
        except Exception as e:
            logger.error(f"Failed to save artifact {artifact.id}: {str(e)}")
            raise

    def load_project(self) -> ProjectState:
        """Load project state from XML files."""
        try:
            logger.info(f"Loading project from {self.project_path}")
            
            # Load Config
            config_path = os.path.join(self.project_path, "project.xml")
            if not os.path.exists(config_path):
                logger.warning("Project config not found, returning default state")
                return ProjectState(
                    config=ProjectConfig(name="New Project"),
                    artifacts={},
                    traces=[]
                )
            
            tree = ET.parse(config_path)
            root = tree.getroot()
            name = root.find("Name").text
            
            # Load levels (support both old str and new RequirementLevel format)
            levels = []
            levels_elem = root.find("Levels")
            if levels_elem is not None:
                for level_elem in levels_elem.findall("Level"):
                    # Check if it's new format (with Name/Description) or old format (just text)
                    name_elem = level_elem.find("Name")
                    if name_elem is not None:
                        # New format
                        desc_elem = level_elem.find("Description")
                        levels.append(RequirementLevel(
                            name=name_elem.text,
                            description=(desc_elem.text or "") if desc_elem is not None else ""
                        ))
                    else:
                        # Old format - convert to RequirementLevel for consistency
                        levels.append(RequirementLevel(
                            name=level_elem.text,
                            description=""
                        ))
            
            # Load settings (with defaults if not present)
            settings = ProjectSettings()
            settings_elem = root.find("Settings")
            if settings_elem is not None:
                enforce_elem = settings_elem.find("EnforceSingleParent")
                if enforce_elem is not None:
                    settings.enforce_single_parent = enforce_elem.text == "True"
                prevent_elem = settings_elem.find("PreventOrphansAtLowerLevels")
                if prevent_elem is not None:
                    settings.prevent_orphans_at_lower_levels = prevent_elem.text == "True"
            
            config = ProjectConfig(name=name, levels=levels, settings=settings)

            # Load Traces
            traces = []
            traces_path = os.path.join(self.project_path, "traces.xml")
            if os.path.exists(traces_path):
                tree = ET.parse(traces_path)
                root = tree.getroot()
                for trace_elem in root.findall("Trace"):
                    traces.append(Trace(
                        source_id=trace_elem.find("SourceID").text,
                        target_id=trace_elem.find("TargetID").text,
                        type=trace_elem.find("Type").text,
                        description=trace_elem.find("Description").text if trace_elem.find("Description") is not None else None
                    ))

            # Load Artifacts
            artifacts = {}
            if os.path.exists(self.artifacts_path):
                for filename in os.listdir(self.artifacts_path):
                    if filename.endswith(".xml"):
                        tree = ET.parse(os.path.join(self.artifacts_path, filename))
                        root = tree.getroot()
                        art_type = ArtifactType(root.find("Type").text)
                        art_id = root.find("ID").text
                        title = root.find("Title").text
                        desc = root.find("Description").text if root.find("Description") is not None else None
                        
                        if art_type == ArtifactType.REQUIREMENT:
                            # Load parent IDs (support both old parent_id and new parent_ids)
                            parent_ids = []
                            parent_id = None
                            
                            # Check for new format (ParentIDs)
                            parent_ids_elem = root.find("ParentIDs")
                            if parent_ids_elem is not None:
                                parent_ids = [p.text for p in parent_ids_elem.findall("ParentID")]
                            else:
                                # Check for old format (ParentID)
                                parent_id_elem = root.find("ParentID")
                                if parent_id_elem is not None:
                                    parent_id = parent_id_elem.text
                                    parent_ids = [parent_id] if parent_id else []
                            
                            # Load justification
                            justification = None
                            justification_elem = root.find("Justification")
                            if justification_elem is not None:
                                justification = justification_elem.text
                            
                            artifacts[art_id] = Requirement(
                                id=art_id, title=title, description=desc,
                                level=root.find("Level").text,
                                parent_id=parent_id,
                                parent_ids=parent_ids,
                                justification=justification
                            )
                        elif art_type == ArtifactType.RISK_HAZARD:
                            artifacts[art_id] = RiskHazard(
                                id=art_id, title=title, description=desc,
                                severity=root.find("Severity").text if root.find("Severity") is not None else None
                            )
                        elif art_type == ArtifactType.RISK_CAUSE:
                            artifacts[art_id] = RiskCause(
                                id=art_id, title=title, description=desc,
                                probability=root.find("Probability").text if root.find("Probability") is not None else None
                            )
                        elif art_type == ArtifactType.VERIFICATION_ACTIVITY:
                            artifacts[art_id] = VerificationActivity(
                                id=art_id, title=title, description=desc,
                                method=VerificationMethod(root.find("Method").text),
                                procedure=root.find("Procedure").text if root.find("Procedure") is not None else None,
                                setup=root.find("Setup").text if root.find("Setup") is not None else None,
                                passed=root.find("Passed").text == "True"
                            )

            logger.info(f"Successfully loaded project with {len(artifacts)} artifacts and {len(traces)} traces")
            return ProjectState(config=config, artifacts=artifacts, traces=traces)
        except Exception as e:
            logger.error(f"Failed to load project: {str(e)}")
            raise

    def commit(self, message: str):
        """Commit all changes to Git repository."""
        try:
            logger.info(f"Committing changes: {message}")
            self.repo.git.add(A=True)
            self.repo.index.commit(message)
            logger.info("Successfully committed changes")
        except Exception as e:
            logger.error(f"Failed to commit changes: {str(e)}")
            raise

    def get_history(self):
        return list(self.repo.iter_commits())

    def checkout(self, commit_hash: str):
        self.repo.git.checkout(commit_hash)
