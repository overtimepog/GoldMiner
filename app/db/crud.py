from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from app.db import models
from app.db.schemas import StartupIdeaCreate, StartupIdeaUpdate, ValidationResultCreate, MarketResearchCreate, PainPointEvidenceCreate

# Startup Ideas CRUD
def create_startup_idea(db: Session, idea: StartupIdeaCreate) -> models.StartupIdea:
    """Create a new startup idea"""
    idea_data = idea.dict()
    # Add status field with default value
    if 'status' not in idea_data:
        idea_data['status'] = 'pending'
    db_idea = models.StartupIdea(**idea_data)
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

def get_startup_idea(db: Session, idea_id: int) -> Optional[models.StartupIdea]:
    """Get a startup idea by ID"""
    return db.query(models.StartupIdea).filter(models.StartupIdea.id == idea_id).first()

def get_startup_ideas(db: Session, skip: int = 0, limit: int = 100) -> List[models.StartupIdea]:
    """Get all startup ideas with pagination"""
    return db.query(models.StartupIdea).offset(skip).limit(limit).all()

def update_startup_idea(db: Session, idea_id: int, update_data: Union[StartupIdeaUpdate, Dict]) -> Optional[models.StartupIdea]:
    """Update a startup idea"""
    db_idea = get_startup_idea(db, idea_id)
    if db_idea:
        if isinstance(update_data, dict):
            data = update_data
        else:
            data = update_data.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(db_idea, field, value)
        db_idea.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_idea)
    return db_idea

def delete_startup_idea(db: Session, idea_id: int) -> bool:
    """Delete a startup idea"""
    db_idea = get_startup_idea(db, idea_id)
    if db_idea:
        db.delete(db_idea)
        db.commit()
        return True
    return False

# Validation Results CRUD
def create_validation_result(db: Session, validation: ValidationResultCreate) -> models.ValidationResult:
    """Create a new validation result"""
    db_validation = models.ValidationResult(**validation.dict())
    db.add(db_validation)
    db.commit()
    db.refresh(db_validation)
    return db_validation

def get_validation_results_by_idea(db: Session, idea_id: int) -> List[models.ValidationResult]:
    """Get all validation results for an idea"""
    return db.query(models.ValidationResult).filter(models.ValidationResult.idea_id == idea_id).all()

def get_latest_validation_result(db: Session, idea_id: int) -> Optional[models.ValidationResult]:
    """Get the latest validation result for an idea"""
    return db.query(models.ValidationResult).filter(
        models.ValidationResult.idea_id == idea_id
    ).order_by(models.ValidationResult.validated_at.desc()).first()

# Market Research CRUD
def create_market_research(db: Session, research: MarketResearchCreate) -> models.MarketResearch:
    """Create new market research"""
    db_research = models.MarketResearch(**research.dict())
    db.add(db_research)
    db.commit()
    db.refresh(db_research)
    return db_research

def get_market_research_by_idea(db: Session, idea_id: int) -> List[models.MarketResearch]:
    """Get all market research for an idea"""
    return db.query(models.MarketResearch).filter(models.MarketResearch.idea_id == idea_id).all()

def get_latest_market_research(db: Session, idea_id: int) -> Optional[models.MarketResearch]:
    """Get the latest market research for an idea"""
    return db.query(models.MarketResearch).filter(
        models.MarketResearch.idea_id == idea_id
    ).order_by(models.MarketResearch.research_timestamp.desc()).first()

# Search and Filter Functions
def search_startup_ideas(db: Session, query: str) -> List[models.StartupIdea]:
    """Search startup ideas by title or description"""
    search = f"%{query}%"
    return db.query(models.StartupIdea).filter(
        (models.StartupIdea.title.ilike(search)) |
        (models.StartupIdea.problem_statement.ilike(search)) |
        (models.StartupIdea.solution_outline.ilike(search))
    ).all()

def get_ideas_by_market_focus(db: Session, market_focus: str) -> List[models.StartupIdea]:
    """Get ideas by market focus"""
    return db.query(models.StartupIdea).filter(
        models.StartupIdea.market_focus == market_focus
    ).all()

def get_high_scoring_ideas(db: Session, min_score: float = 70.0) -> List[Dict[str, Any]]:
    """Get ideas with validation score above threshold"""
    results = db.query(
        models.StartupIdea,
        models.ValidationResult
    ).join(
        models.ValidationResult
    ).filter(
        models.ValidationResult.overall_score >= min_score
    ).all()
    
    return [{"idea": idea, "validation": validation} for idea, validation in results]

# Pain Point Evidence CRUD
def create_pain_point_evidence(db: Session, evidence: PainPointEvidenceCreate) -> models.PainPointEvidence:
    """Create new pain point evidence"""
    db_evidence = models.PainPointEvidence(**evidence.dict())
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

def create_multiple_pain_point_evidence(db: Session, evidence_list: List[PainPointEvidenceCreate]) -> List[models.PainPointEvidence]:
    """Create multiple pain point evidence records"""
    db_evidence_list = [models.PainPointEvidence(**evidence.dict()) for evidence in evidence_list]
    db.add_all(db_evidence_list)
    db.commit()
    for evidence in db_evidence_list:
        db.refresh(evidence)
    return db_evidence_list

def get_pain_point_evidence_by_idea(db: Session, idea_id: int) -> List[models.PainPointEvidence]:
    """Get all pain point evidence for an idea"""
    return db.query(models.PainPointEvidence).filter(
        models.PainPointEvidence.idea_id == idea_id
    ).order_by(models.PainPointEvidence.relevance_score.desc()).all()

def get_pain_point_evidence_by_platform(db: Session, platform: str, limit: int = 100) -> List[models.PainPointEvidence]:
    """Get pain point evidence by platform"""
    return db.query(models.PainPointEvidence).filter(
        models.PainPointEvidence.platform == platform
    ).limit(limit).all()

def delete_pain_point_evidence(db: Session, evidence_id: int) -> bool:
    """Delete pain point evidence"""
    db_evidence = db.query(models.PainPointEvidence).filter(
        models.PainPointEvidence.id == evidence_id
    ).first()
    if db_evidence:
        db.delete(db_evidence)
        db.commit()
        return True
    return False