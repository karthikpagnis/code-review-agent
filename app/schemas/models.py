from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional
from datetime import datetime


class ReviewRequest(BaseModel):
    github_url: Optional[str] = None   # public GitHub file or repo URL
    code_snippet: Optional[str] = None  # direct code paste
    language: str = "python"

    model_config = {"json_schema_extra": {
        "example": {
            "github_url": "https://github.com/karthikpagnis/PolicyPilot/blob/main/main.py",
            "language": "python"
        }
    }}


class Finding(BaseModel):
    severity: Literal["high", "medium", "low"]
    category: Literal["security", "logic", "quality"]
    type: str
    line_hint: str
    description: str
    suggestion: str


class ReviewReport(BaseModel):
    review_id: str
    repo_url: Optional[str]
    language: str
    files_analysed: int
    chunks_analysed: int
    total_issues: int
    high_count: int
    medium_count: int
    low_count: int
    findings: list[Finding]
    blob_url: Optional[str]   # Azure Blob link to persisted JSON
    reviewed_at: datetime


class ReviewResponse(BaseModel):
    status: str
    report: ReviewReport
