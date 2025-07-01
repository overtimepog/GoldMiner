from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, schemas
from app.agents.validator import ValidatorAgent
from app.agents.market_researcher import MarketResearchAgent

router = APIRouter(
    prefix="/api/validation",
    tags=["validation"]
)

# Create agent instances
validator = ValidatorAgent()
market_researcher = MarketResearchAgent()

@router.post("/{idea_id}", response_model=schemas.ValidationResult)
async def validate_idea(
    idea_id: int,
    request: schemas.ValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate a startup idea using AI-powered analysis"""
    # Check if idea exists
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    try:
        # Get latest market research if available
        market_research = crud.get_latest_market_research(db, idea_id)
        
        # Run AI validation
        validation_data = await validator.validate_idea(
            idea=idea,
            market_research=market_research,
            validation_depth=request.validation_depth
        )
        
        # Prepare validation data for database
        validation_create = schemas.ValidationResultCreate(
            idea_id=idea_id,
            problem_score=validation_data["problem_score"],
            solution_score=validation_data["solution_score"],
            market_score=validation_data["market_score"],
            execution_score=validation_data["execution_score"],
            overall_score=validation_data["overall_score"],
            validation_details=validation_data.get("validation_details", {}),
            validation_notes=validation_data.get("validation_notes", "")
        )
        
        return crud.create_validation_result(db, validation_create)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{idea_id}", response_model=List[schemas.ValidationResult])
async def get_validations(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Get all validation results for an idea"""
    # Check if idea exists
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return crud.get_validation_results_by_idea(db, idea_id)

@router.get("/{idea_id}/latest", response_model=schemas.ValidationResult)
async def get_latest_validation(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Get the latest validation result for an idea"""
    # Check if idea exists
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    validation = crud.get_latest_validation_result(db, idea_id)
    if not validation:
        raise HTTPException(status_code=404, detail="No validation found for this idea")
    
    return validation