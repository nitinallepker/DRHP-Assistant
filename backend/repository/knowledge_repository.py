from sqlalchemy.orm import Session
from database.models import Workspace, WorkspaceFile, KnowledgeItem, DRHPSection, SectionDependency, SectionComment, ReviewSuggestion, TransformedContent
from typing import List, Dict, Any, Optional

class KnowledgeRepository:
    """
    KnowledgeRepository manages database CRUD transactions for documents 
    and AI-extracted corporate facts in the SQLite database.
    """

    def add_workspace_files(
        self, 
        db: Session, 
        workspace_id: str, 
        workspace_name: str, 
        files: List[Dict[str, Any]]
    ) -> List[WorkspaceFile]:
        """
        Registers metadata records for scanned workspace files in the database.
        """
        db_files = []
        for file in files:
            db_file = WorkspaceFile(
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                name=file["name"],
                type=file["type"],
                size_bytes=file["size_bytes"],
                size_display=file["size_display"],
                path=file["path"],
                absolute_path=file["absolute_path"],
                extension=file["extension"],
                category=file["category"]
            )
            db.add(db_file)
            db_files.append(db_file)
        
        db.commit()
        for f in db_files:
            db.refresh(f)
        return db_files

    def add_knowledge_items(
        self, 
        db: Session, 
        workspace_id: str, 
        items: List[Dict[str, Any]]
    ) -> List[KnowledgeItem]:
        """
        Persists a list of extracted structured knowledge facts to the database.
        """
        db_items = []
        for item in items:
            db_item = KnowledgeItem(
                workspace_id=workspace_id,
                category=item["category"],
                field=item["field"],
                value=str(item["value"]),
                evidence=item["evidence"],
                source_document=item["source_document"],
                source_page=str(item["source_page"]),
                confidence=float(item["confidence"])
            )
            db.add(db_item)
            db_items.append(db_item)
            
        db.commit()
        for i in db_items:
            db.refresh(i)
        return db_items

    def get_workspace_files(self, db: Session, workspace_id: str) -> List[WorkspaceFile]:
        """
        Retrieves all documents associated with a workspace ID.
        """
        return db.query(WorkspaceFile).filter(WorkspaceFile.workspace_id == workspace_id).all()

    def get_knowledge_items(self, db: Session, workspace_id: str) -> List[KnowledgeItem]:
        """
        Retrieves all facts extracted for a workspace ID.
        """
        return db.query(KnowledgeItem).filter(KnowledgeItem.workspace_id == workspace_id).all()

    def get_knowledge_by_category(self, db: Session, workspace_id: str, category: str) -> List[KnowledgeItem]:
        """
        Retrieves facts for a workspace ID filtered by category (e.g. financials, promoters).
        """
        return db.query(KnowledgeItem).filter(
            KnowledgeItem.workspace_id == workspace_id,
            KnowledgeItem.category == category
        ).all()

    def create_workspace(
        self, 
        db: Session, 
        workspace_id: str, 
        name: str, 
        root_path: str, 
        status: str = "PENDING"
    ) -> Workspace:
        """
        Registers a new workspace in the repository.
        """
        db_workspace = Workspace(
            id=workspace_id,
            name=name,
            status=status,
            root_path=root_path
        )
        db.add(db_workspace)
        db.commit()
        db.refresh(db_workspace)
        return db_workspace

    def update_workspace_status(self, db: Session, workspace_id: str, status: str) -> Optional[Workspace]:
        """
        Updates the execution status of a workspace.
        """
        workspace = self.get_workspace(db, workspace_id)
        if workspace:
            workspace.status = status
            db.commit()
            db.refresh(workspace)
        return workspace

    def get_workspace(self, db: Session, workspace_id: str) -> Optional[Workspace]:
        """
        Queries and returns a workspace metadata record by its ID.
        """
        return db.query(Workspace).filter(Workspace.id == workspace_id).first()

    def save_section(
        self, 
        db: Session, 
        workspace_id: str, 
        section_slug: str, 
        title: str, 
        content: str, 
        status: str = "DRAFT", 
        metadata_json: str = None
    ) -> DRHPSection:
        """
        Creates a new version of the specified DRHP section in the database.
        Ensures previous versions are preserved by incrementing the version index.
        """
        latest = self.get_latest_section(db, workspace_id, section_slug)
        next_version = (latest.version + 1) if latest else 1
        
        db_section = DRHPSection(
            workspace_id=workspace_id,
            section_slug=section_slug,
            title=title,
            content=content,
            version=next_version,
            status=status,
            metadata_json=metadata_json
        )
        db.add(db_section)
        db.commit()
        db.refresh(db_section)
        return db_section

    def get_latest_section(self, db: Session, workspace_id: str, section_slug: str) -> Optional[DRHPSection]:
        """
        Queries and returns the latest version of a specific DRHP section slug.
        """
        return db.query(DRHPSection).filter(
            DRHPSection.workspace_id == workspace_id,
            DRHPSection.section_slug == section_slug
        ).order_by(DRHPSection.version.desc()).first()

    def get_section_history(self, db: Session, workspace_id: str, section_slug: str) -> List[DRHPSection]:
        return db.query(DRHPSection).filter(
            DRHPSection.workspace_id == workspace_id,
            DRHPSection.section_slug == section_slug
        ).order_by(DRHPSection.version.desc()).all()

    def get_section_by_version(self, db: Session, workspace_id: str, section_slug: str, version: int) -> Optional[DRHPSection]:
        """
        Queries and returns a specific version of a DRHP section by its version number.
        """
        return db.query(DRHPSection).filter(
            DRHPSection.workspace_id == workspace_id,
            DRHPSection.section_slug == section_slug,
            DRHPSection.version == version
        ).first()

    def add_section_dependency(self, db: Session, workspace_id: str, section_slug: str, depends_on_slug: str) -> SectionDependency:
        """
        Registers a section-to-section dependency mapping if it does not already exist.
        """
        existing = db.query(SectionDependency).filter(
            SectionDependency.workspace_id == workspace_id,
            SectionDependency.section_slug == section_slug,
            SectionDependency.depends_on_slug == depends_on_slug
        ).first()
        if existing:
            return existing
            
        dep = SectionDependency(
            workspace_id=workspace_id,
            section_slug=section_slug,
            depends_on_slug=depends_on_slug
        )
        db.add(dep)
        db.commit()
        db.refresh(dep)
        return dep

    def get_section_dependencies(self, db: Session, workspace_id: str, section_slug: str) -> List[str]:
        """
        Retrieves the list of slugs that the specified section slug depends on.
        """
        deps = db.query(SectionDependency).filter(
            SectionDependency.workspace_id == workspace_id,
            SectionDependency.section_slug == section_slug
        ).all()
        return [d.depends_on_slug for d in deps]

    def add_section_comment(
        self,
        db: Session,
        workspace_id: str,
        section_slug: str,
        version: int,
        author: str,
        text: str,
        suggested_text: str = None
    ) -> SectionComment:
        """
        Appends a new comment or inline text suggestion to a specific version of a DRHP section.
        """
        db_comment = SectionComment(
            workspace_id=workspace_id,
            section_slug=section_slug,
            version=version,
            author=author,
            text=text,
            suggested_text=suggested_text,
            status="OPEN"
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def resolve_section_comment(self, db: Session, comment_id: str) -> Optional[SectionComment]:
        """
        Resolves (closes) a comment or inline suggestion by setting its status to 'RESOLVED'.
        """
        comment = db.query(SectionComment).filter(SectionComment.id == comment_id).first()
        if comment:
            comment.status = "RESOLVED"
            db.commit()
            db.refresh(comment)
        return comment

    def get_section_comments(
        self, 
        db: Session, 
        workspace_id: str, 
        section_slug: str, 
        version: int = None
    ) -> List[SectionComment]:
        """
        Queries comments/suggestions on a section. Optionally filters by version.
        """
        query = db.query(SectionComment).filter(
            SectionComment.workspace_id == workspace_id,
            SectionComment.section_slug == section_slug
        )
        if version is not None:
            query = query.filter(SectionComment.version == version)
        return query.order_by(SectionComment.created_at.asc()).all()

    def update_section_status(
        self,
        db: Session,
        workspace_id: str,
        section_slug: str,
        version: int,
        status: str
    ) -> Optional[DRHPSection]:
        """
        Updates the workflow status of a specific drafted section version (e.g. APPROVED).
        """
        section = db.query(DRHPSection).filter(
            DRHPSection.workspace_id == workspace_id,
            DRHPSection.section_slug == section_slug,
            DRHPSection.version == version
        ).first()
        if section:
            section.status = status
            db.commit()
            db.refresh(section)
        return section

    def add_review_suggestion(
        self,
        db: Session,
        workspace_id: str,
        section_slug: str,
        section_version: int,
        reviewer: str,
        severity: str,
        confidence: float,
        reason: str,
        evidence: str,
        recommendation: str,
        status: str = "OPEN"
    ) -> ReviewSuggestion:
        """
        Creates and stores a new structured AI reviewer suggestion in SQLite.
        """
        import uuid
        suggestion = ReviewSuggestion(
            suggestion_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            section_slug=section_slug,
            section_version=section_version,
            reviewer=reviewer,
            severity=severity,
            confidence=confidence,
            reason=reason,
            evidence=evidence,
            recommendation=recommendation,
            status=status
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        return suggestion

    def get_review_suggestions(
        self,
        db: Session,
        workspace_id: str,
        section_slug: Optional[str] = None,
        reviewer: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ReviewSuggestion]:
        """
        Retrieves review suggestions matching the specified query filters.
        """
        query = db.query(ReviewSuggestion).filter(ReviewSuggestion.workspace_id == workspace_id)
        
        if section_slug:
            query = query.filter(ReviewSuggestion.section_slug == section_slug)
        if reviewer:
            query = query.filter(ReviewSuggestion.reviewer == reviewer)
        if severity:
            query = query.filter(ReviewSuggestion.severity == severity)
        if status:
            query = query.filter(ReviewSuggestion.status == status)
            
        return query.order_by(ReviewSuggestion.created_at.desc()).all()

    def update_review_suggestion_status(
        self,
        db: Session,
        suggestion_id: str,
        status: str
    ) -> Optional[ReviewSuggestion]:
        """
        Updates the status (e.g. ACCEPTED, REJECTED) of an AI review suggestion.
        """
        suggestion = db.query(ReviewSuggestion).filter(ReviewSuggestion.suggestion_id == suggestion_id).first()
        if suggestion:
            suggestion.status = status
            db.commit()
            db.refresh(suggestion)
        return suggestion

    def save_transformed_content(
        self,
        db: Session,
        workspace_id: str,
        content_type: str,
        title: str,
        content: str
    ) -> TransformedContent:
        """
        Saves or updates downstream transformed media content in SQLite database.
        """
        import uuid
        existing = db.query(TransformedContent).filter(
            TransformedContent.workspace_id == workspace_id,
            TransformedContent.content_type == content_type
        ).first()
        
        if existing:
            existing.title = title
            existing.content = content
            db.commit()
            db.refresh(existing)
            return existing
            
        tc = TransformedContent(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            content_type=content_type,
            title=title,
            content=content
        )
        db.add(tc)
        db.commit()
        db.refresh(tc)
        return tc

    def get_transformed_contents(self, db: Session, workspace_id: str) -> List[TransformedContent]:
        """
        Retrieves all transformed media formats generated for a workspace.
        """
        return db.query(TransformedContent).filter(TransformedContent.workspace_id == workspace_id).all()

    def get_transformed_content_by_type(self, db: Session, workspace_id: str, content_type: str) -> Optional[TransformedContent]:
        """
        Retrieves a specific transformed media content by its type.
        """
        return db.query(TransformedContent).filter(
            TransformedContent.workspace_id == workspace_id,
            TransformedContent.content_type == content_type
        ).first()
