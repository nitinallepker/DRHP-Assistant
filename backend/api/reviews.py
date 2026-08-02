from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from repository.knowledge_repository import KnowledgeRepository
from review.review_engine import ReviewEngine
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

class SuggestionStatusRequest(BaseModel):
    status: str  # OPEN, ACCEPTED, REJECTED

@router.post("/{workspace_id}/run")
def run_workspace_review(workspace_id: str, db: Session = Depends(get_db)):
    """
    Executes all independent reviewer agents across the workspace's drafted sections
    using relevant facts context packs. Stores findings in SQLite.
    """
    # Verify workspace exists
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    try:
        engine = ReviewEngine()
        suggestions = engine.run_workspace_review(db, workspace_id)
        
        return {
            "status": "success",
            "workspace_id": workspace_id,
            "suggestions_count": len(suggestions),
            "suggestions": [
                {
                    "suggestion_id": s.suggestion_id,
                    "section_slug": s.section_slug,
                    "reviewer": s.reviewer,
                    "severity": s.severity,
                    "recommendation": s.recommendation[:100] + "..." if len(s.recommendation) > 100 else s.recommendation
                }
                for s in suggestions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review Engine audit failed: {str(e)}")

@router.get("/{workspace_id}/suggestions")
def get_workspace_suggestions(
    workspace_id: str,
    section_slug: Optional[str] = Query(None),
    reviewer: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieves review suggestions flagged for this workspace.
    Supports query parameters to filter by section slug, reviewer, severity, and status.
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    suggestions = repo.get_review_suggestions(
        db=db,
        workspace_id=workspace_id,
        section_slug=section_slug,
        reviewer=reviewer,
        severity=severity,
        status=status
    )
    
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "results_count": len(suggestions),
        "suggestions": [
            {
                "suggestion_id": s.suggestion_id,
                "workspace_id": s.workspace_id,
                "section_slug": s.section_slug,
                "section_version": s.section_version,
                "reviewer": s.reviewer,
                "severity": s.severity,
                "confidence": s.confidence,
                "reason": s.reason,
                "evidence": s.evidence,
                "recommendation": s.recommendation,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in suggestions
        ]
    }

@router.post("/suggestions/{suggestion_id}/status")
def update_suggestion_status(
    suggestion_id: str,
    body: SuggestionStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts or rejects an AI reviewer suggestion, updating its status state.
    """
    repo = KnowledgeRepository()
    status_upper = body.status.upper()
    if status_upper not in ["OPEN", "ACCEPTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid suggestion status. Must be OPEN, ACCEPTED, or REJECTED.")
        
    updated = repo.update_review_suggestion_status(db, suggestion_id, status_upper)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Suggestion ID '{suggestion_id}' not found.")
        
    return {
        "status": "success",
        "suggestion_id": suggestion_id,
        "new_status": updated.status
    }
