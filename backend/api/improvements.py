from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from repository.knowledge_repository import KnowledgeRepository
from review.improvement_engine import ImprovementEngine

router = APIRouter(
    prefix="/improvements",
    tags=["improvements"]
)

@router.get("/{workspace_id}/conflicts")
def get_suggestion_conflicts(workspace_id: str, db: Session = Depends(get_db)):
    """
    Scans active suggestions for the workspace to detect conflicting recommendations
    between independent reviewer agents (e.g. Legal redacting vs Finance auditing).
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    try:
        suggestions = repo.get_review_suggestions(db, workspace_id)
        engine = ImprovementEngine()
        conflicts = engine.detect_conflicts(suggestions)
        
        return {
            "status": "success",
            "workspace_id": workspace_id,
            "conflicts_count": len(conflicts),
            "conflicts": conflicts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conflict detection failed: {str(e)}")

@router.post("/{workspace_id}/apply")
def apply_accepted_improvements(workspace_id: str, db: Session = Depends(get_db)):
    """
    Retrieves all ACCEPTED review suggestions, rewrites the corresponding sections,
    and saves them as new incremented draft versions in SQLite.
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    try:
        engine = ImprovementEngine()
        updates = engine.apply_improvements(db, workspace_id)
        
        return {
            "status": "success",
            "workspace_id": workspace_id,
            "applied_sections_count": len(updates),
            "applied_updates": updates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Applying improvements failed: {str(e)}")
