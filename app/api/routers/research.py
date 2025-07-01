from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, schemas
from app.agents.market_researcher import MarketResearchAgent

router = APIRouter(
    prefix="/api/research",
    tags=["market-research"]
)

# Create agent instance
market_researcher = MarketResearchAgent()

@router.post("/{idea_id}", response_model=schemas.MarketResearch)
async def conduct_market_research(
    idea_id: int,
    request: schemas.MarketResearchRequest,
    db: Session = Depends(get_db)
):
    """Conduct market research for a startup idea"""
    # Check if idea exists
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    try:
        # Run AI market research
        research_data = await market_researcher.research_idea(
            idea=idea,
            research_depth=request.research_depth
        )
        
        # Add idea_id to research data
        research_data["idea_id"] = idea_id
        
        research_create = schemas.MarketResearchCreate(**research_data)
        return crud.create_market_research(db, research_create)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{idea_id}", response_model=List[schemas.MarketResearch])
async def get_research(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Get all market research for an idea"""
    # Check if idea exists
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return crud.get_market_research_by_idea(db, idea_id)

@router.get("/{idea_id}/latest", response_model=schemas.MarketResearch)
async def get_latest_research(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Get the latest market research for an idea"""
    # Check if idea exists
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    research = crud.get_latest_market_research(db, idea_id)
    if not research:
        raise HTTPException(status_code=404, detail="No research found for this idea")
    
    return research