from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from repository.knowledge_repository import KnowledgeRepository
from typing import List, Optional
from pydantic import BaseModel
from utils.redactor import Redactor
from utils.differ import DiffEngine

router = APIRouter(
    prefix="/sections",
    tags=["sections"]
)

# Pydantic schema validation structures
class StatusUpdateRequest(BaseModel):
    version: int
    status: str

class CommentCreateRequest(BaseModel):
    version: int
    author: str
    text: str
    suggested_text: Optional[str] = None

@router.get("/{workspace_id}/{section_slug}")
def get_latest_section(workspace_id: str, section_slug: str, db: Session = Depends(get_db)):
    """
    Retrieves the latest drafted version of a specific DRHP section.
    """
    repo = KnowledgeRepository()
    section = repo.get_latest_section(db, workspace_id, section_slug)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found.")
    return section

@router.get("/{workspace_id}/{section_slug}/history")
def get_section_history(workspace_id: str, section_slug: str, db: Session = Depends(get_db)):
    """
    Retrieves the complete version history of a DRHP section.
    """
    repo = KnowledgeRepository()
    return repo.get_section_history(db, workspace_id, section_slug)

@router.post("/{workspace_id}/{section_slug}/status")
def update_section_status(workspace_id: str, section_slug: str, body: StatusUpdateRequest, db: Session = Depends(get_db)):
    """
    Updates the workflow status of a specific drafted version of a section.
    """
    repo = KnowledgeRepository()
    updated = repo.update_section_status(db, workspace_id, section_slug, body.version, body.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Section version not found.")
    return updated

@router.post("/{workspace_id}/{section_slug}/comments")
def add_comment(workspace_id: str, section_slug: str, body: CommentCreateRequest, db: Session = Depends(get_db)):
    """
    Adds a comment or inline edit suggestion to a specific version of a section.
    """
    repo = KnowledgeRepository()
    # Verify section version exists first
    section_history = repo.get_section_history(db, workspace_id, section_slug)
    valid_versions = [s.version for s in section_history]
    if body.version not in valid_versions:
        raise HTTPException(status_code=400, detail=f"Invalid section version. Valid versions: {valid_versions}")
        
    comment = repo.add_section_comment(
        db=db,
        workspace_id=workspace_id,
        section_slug=section_slug,
        version=body.version,
        author=body.author,
        text=body.text,
        suggested_text=body.suggested_text
    )
    return comment

@router.get("/{workspace_id}/{section_slug}/comments")
def get_comments(workspace_id: str, section_slug: str, version: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Retrieves all comments/suggestions for a section. Can filter by version.
    """
    repo = KnowledgeRepository()
    return repo.get_section_comments(db, workspace_id, section_slug, version)

@router.post("/comments/{comment_id}/resolve")
def resolve_comment(comment_id: str, db: Session = Depends(get_db)):
    """
    Resolves a comment by ID, marking its status as RESOLVED.
    """
    repo = KnowledgeRepository()
    resolved = repo.resolve_section_comment(db, comment_id)
    if not resolved:
        raise HTTPException(status_code=404, detail="Comment not found.")
    return resolved


class RedactRequest(BaseModel):
    rules: Optional[List[str]] = None


@router.post("/{workspace_id}/{section_slug}/redact")
def redact_section_content(workspace_id: str, section_slug: str, body: Optional[RedactRequest] = None, db: Session = Depends(get_db)):
    """
    Applies privacy redaction filters to the latest version of a section.
    Saves a new incremented version in the database containing the masked content.
    """
    repo = KnowledgeRepository()
    
    # 1. Fetch latest draft version
    latest = repo.get_latest_section(db, workspace_id, section_slug)
    if not latest:
        raise HTTPException(status_code=404, detail=f"Section '{section_slug}' not found.")
        
    # 2. Run Redactor matching active rules
    redactor = Redactor()
    active_rules = body.rules if body else None
    redacted_text = redactor.redact(latest.content, active_rules)
    
    # 3. Save as a new version
    new_version = repo.save_section(
        db=db,
        workspace_id=workspace_id,
        section_slug=section_slug,
        title=latest.title,
        content=redacted_text,
        status="DRAFT",
        metadata_json=f"{{'action': 'redact', 'previous_version': {latest.version}, 'rules': {active_rules}}}"
    )
    
    return new_version


@router.get("/{workspace_id}/{section_slug}/diff")
def compare_section_versions(workspace_id: str, section_slug: str, v_from: Optional[int] = Query(None), v_to: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """
    Compares text differences between two historical draft versions of a section.
    If versions are not specified, defaults v_to to latest version, and v_from to v_to - 1.
    """
    repo = KnowledgeRepository()
    
    # 1. Determine target version (v_to)
    if v_to is None:
        latest = repo.get_latest_section(db, workspace_id, section_slug)
        if not latest:
            raise HTTPException(status_code=404, detail=f"Section '{section_slug}' not found.")
        v_to = latest.version
        
    # 2. Determine base version (v_from)
    if v_from is None:
        v_from = max(1, v_to - 1)
        
    # 3. Retrieve both versions
    sec_from = repo.get_section_by_version(db, workspace_id, section_slug, v_from)
    sec_to = repo.get_section_by_version(db, workspace_id, section_slug, v_to)
    
    text_from = sec_from.content if sec_from else ""
    text_to = sec_to.content if sec_to else ""
    
    # 4. Generate diff
    diff_engine = DiffEngine()
    diff_report = diff_engine.generate_diff(text_from, text_to)
    
    return {
        "workspace_id": workspace_id,
        "section_slug": section_slug,
        "v_from": v_from,
        "v_to": v_to,
        "raw_diff": diff_report["raw_diff"],
        "html_diff": diff_report["html_diff"]
    }
