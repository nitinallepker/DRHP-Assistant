import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.sql import func
from database.connection import Base

class Workspace(Base):
    """
    SQLAlchemy model representing an overall project/workspace lifecycle.
    """
    __tablename__ = "workspaces"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSING, READY, FAILED
    root_path = Column(String(1000), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class WorkspaceFile(Base):
    """
    SQLAlchemy model representing an ingested document in a workspace.
    """
    __tablename__ = "workspace_files"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), index=True, nullable=False)
    workspace_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    size_display = Column(String(50), nullable=False)
    path = Column(String(500), nullable=False)
    absolute_path = Column(String(1000), nullable=False)
    extension = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class KnowledgeItem(Base):
    """
    SQLAlchemy model representing a single structured fact extracted from a document.
    """
    __tablename__ = "knowledge_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), index=True, nullable=False)
    category = Column(String(50), index=True, nullable=False)
    field = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    source_document = Column(String(255), nullable=False)
    source_page = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class DRHPSection(Base):
    """
    SQLAlchemy model representing a versioned drafted section of the DRHP.
    Supports historical versioning and status changes.
    """
    __tablename__ = "drhp_sections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), index=True, nullable=False)
    section_slug = Column(String(100), index=True, nullable=False)  # e.g., "cover_page", "risk_factors"
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="DRAFT", nullable=False)  # DRAFT, REVIEW_PENDING, APPROVED
    metadata_json = Column(Text, nullable=True)  # Stores generation parameters or change logs
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class SectionDependency(Base):
    """
    SQLAlchemy model mapping logical dependencies between DRHP sections.
    """
    __tablename__ = "section_dependencies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String(36), index=True, nullable=False)
    section_slug = Column(String(100), nullable=False)       # The dependent section
    depends_on_slug = Column(String(100), nullable=False)    # The section it depends on
    created_at = Column(DateTime, server_default=func.now())

class SectionComment(Base):
    """
    SQLAlchemy model representing a comment or inline suggestion on a DRHP section.
    Binds comments to specific document versions.
    """
    __tablename__ = "section_comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), index=True, nullable=False)
    section_slug = Column(String(100), index=True, nullable=False)
    version = Column(Integer, nullable=False)
    author = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    suggested_text = Column(Text, nullable=True)  # Stores inline text proposals
    status = Column(String(50), default="OPEN", nullable=False)  # OPEN, RESOLVED
    created_at = Column(DateTime, server_default=func.now())


class ReviewSuggestion(Base):
    """
    SQLAlchemy model representing an AI-generated structured review suggestion.
    Used by legal, finance, risk, compliance, business, language, and consistency reviewers.
    """
    __tablename__ = "review_suggestions"
    
    suggestion_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), index=True, nullable=False)
    section_slug = Column(String(100), index=True, nullable=False)
    section_version = Column(Integer, nullable=False)
    reviewer = Column(String(100), nullable=False)  # LEGAL, FINANCE, BUSINESS, RISK, COMPLIANCE, LANGUAGE, CONSISTENCY
    severity = Column(String(50), nullable=False)   # HIGH, MEDIUM, LOW
    confidence = Column(Float, nullable=False)      # Range 0.0 to 1.0
    reason = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)         # Cites source document, page, or Knowledge Item
    recommendation = Column(Text, nullable=False)   # Concrete suggested revision text
    status = Column(String(50), default="OPEN", nullable=False)  # OPEN, ACCEPTED, REJECTED
    created_at = Column(DateTime, server_default=func.now())


class TransformedContent(Base):
    """
    SQLAlchemy model representing downstream media generated from the approved DRHP.
    Used for Executive Summary, Brochures, Presentations, FAQs, Social content, and scripts.
    """
    __tablename__ = "transformed_content"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), index=True, nullable=False)
    content_type = Column(String(100), index=True, nullable=False)  # EXECUTIVE_SUMMARY, SOCIAL_MEDIA, FAQ, etc.
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


