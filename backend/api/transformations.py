from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from repository.knowledge_repository import KnowledgeRepository
from transformation.transformer import ContentTransformer

router = APIRouter(
    prefix="/transformations",
    tags=["transformations"]
)

@router.post("/{workspace_id}/run")
def run_content_transformations(workspace_id: str, db: Session = Depends(get_db)):
    """
    Automatically compiles the approved DRHP prospectus text and generates all 8 downstream
    marketing and media formats (Summaries, brochures, slide decks, FAQs, website pages copy,
    social posts, design prompts, video scripts). Stores deliverables in SQLite.
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    try:
        transformer = ContentTransformer()
        transformed_items = transformer.transform_workspace(db, workspace_id)
        
        return {
            "status": "success",
            "workspace_id": workspace_id,
            "transformed_count": len(transformed_items),
            "transformed_content": [
                {
                    "id": tc.id,
                    "content_type": tc.content_type,
                    "title": tc.title
                }
                for tc in transformed_items
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content transformation pipeline failed: {str(e)}")

@router.get("/{workspace_id}")
def get_transformed_contents(workspace_id: str, db: Session = Depends(get_db)):
    """
    Retrieves a list of all transformed media formats generated for this workspace.
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    items = repo.get_transformed_contents(db, workspace_id)
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "results_count": len(items),
        "transformed_content": [
            {
                "id": tc.id,
                "content_type": tc.content_type,
                "title": tc.title,
                "created_at": tc.created_at.isoformat() if tc.created_at else None
            }
            for tc in items
        ]
    }

@router.get("/{workspace_id}/{content_type}")
def get_transformed_content_by_type(workspace_id: str, content_type: str, db: Session = Depends(get_db)):
    """
    Retrieves the raw content of a specific transformed media type (e.g. EXECUTIVE_SUMMARY or SOCIAL_MEDIA).
    """
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    content_type_upper = content_type.strip().upper()
    item = repo.get_transformed_content_by_type(db, workspace_id, content_type_upper)
    if not item:
        raise HTTPException(
            status_code=404, 
            detail=f"Transformed content for type '{content_type_upper}' not found in workspace."
        )
        
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "content_type": item.content_type,
        "title": item.title,
        "content": item.content
    }

@router.get("/{workspace_id}/{content_type}/download")
def download_transformed_content_file(workspace_id: str, content_type: str, db: Session = Depends(get_db)):
    """
    Downloads the actual compiled professional deliverable file (.pptx, .pdf, .html, .zip)
    directly as a browser attachment file download.
    """
    import os
    from fastapi.responses import FileResponse
    
    repo = KnowledgeRepository()
    workspace = repo.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
        
    content_type_upper = content_type.strip().upper()
    item = repo.get_transformed_content_by_type(db, workspace_id, content_type_upper)
    if not item:
        raise HTTPException(
            status_code=404, 
            detail=f"Transformed content for type '{content_type_upper}' not found in workspace."
        )
        
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "transformations", workspace_id))
    
    # Map content type to expected file extension
    ext_mapping = {
        "PPT_PRESENTATION": ("ppt_presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
        "WEBSITE_CONTENT": ("website_content.html", "text/html"),
        "SOCIAL_MEDIA": ("social_media.zip", "application/zip"),
        "IMAGE_PROMPTS": ("image_prompts.txt", "text/plain"),
        "EXECUTIVE_SUMMARY": ("executive_summary.pdf", "application/pdf"),
        "INVESTOR_BROCHURE": ("investor_brochure.pdf", "application/pdf"),
        "FAQ": ("faq.pdf", "application/pdf"),
        "VIDEO_SCRIPT": ("video_script.pdf", "application/pdf")
    }
    
    mapping = ext_mapping.get(content_type_upper)
    if not mapping:
        raise HTTPException(status_code=400, detail=f"Unsupported download format content type: {content_type_upper}")
        
    filename, media_type = mapping
    file_path = os.path.join(storage_dir, filename)
    
    # Fallback to dynamic compilation on the fly if the file is missing
    if not os.path.exists(file_path):
        try:
            from transformation.transformer import ContentTransformer
            transformer = ContentTransformer()
            transformer.compile_physical_file(workspace.name, content_type_upper, item.title, item.content, storage_dir)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to dynamically compile requested asset file: {str(e)}")
            
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested compiled asset file not found on disk.")
        
    return FileResponse(
        path=file_path,
        filename=f"{workspace.name.replace(' ', '_')}_{filename}",
        media_type=media_type
    )
