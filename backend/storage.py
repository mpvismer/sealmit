import os
import logging
import git
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
from models import ProjectState, ProjectConfig, BaseArtifact, Trace, ArtifactType, Requirement, RiskHazard, RiskCause, VerificationActivity, VerificationMethod

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
            levels_elem = ET.SubElement(config_root, "Levels")
            for level in state.config.levels:
                ET.SubElement(levels_elem, "Level").text = level
            
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
                if artifact.parent_id:
                    ET.SubElement(root, "ParentID").text = artifact.parent_id
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
            levels = [l.text for l in root.find("Levels").findall("Level")]
            config = ProjectConfig(name=name, levels=levels)

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
                            artifacts[art_id] = Requirement(
                                id=art_id, title=title, description=desc,
                                level=root.find("Level").text,
                                parent_id=root.find("ParentID").text if root.find("ParentID") is not None else None
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
