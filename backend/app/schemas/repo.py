from pydantic import BaseModel, AnyUrl, validator, Field
from typing import List, Optional, Dict, Any

class RepoRequest(BaseModel):
    url: str = Field(..., description="The GitHub repository URL (HTTPS or SSH)")

    @validator("url")
    def validate_url(cls, v):
        # Basic validation for git url
        if not (v.startswith("http") or v.startswith("git@")):
            raise ValueError("Invalid repository URL")
        return v

class FileNode(BaseModel):
    path: str
    type: str # 'file' or 'directory'
    size: Optional[int] = 0
    children: Optional[List['FileNode']] = None

class RepoAnalysisInput(BaseModel):
    """Data structure extracted from the repo to be sent to Gemini."""
    structure: List[str] # Simplified file list
    key_files_content: Dict[str, str] # e.g. README.md, requirements.txt content
    languages: Dict[str, int] # Extension count

class RepoAnalysisResult(BaseModel):
    overview: str
    tech_stack: List[str]
    architecture: str
    modules: List[dict]
    entry_points: List[str]
    setup_notes: str
    raw_structure: Optional[List[str]] = None # For debugging or display
