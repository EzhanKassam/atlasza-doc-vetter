from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class DocResult(BaseModel):
    filename: str
    doc_type: str
    fields: Dict[str, Any] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    decision: str = "NEEDS_REVIEW"

class BatchResult(BaseModel):
    decision: str
    summary: str
    findings: List[str]
    documents: List[DocResult]
    report_path: str
