from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import crud, schemas
from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.validator import ValidatorAgent
from app.agents.pain_point_researcher import PainPointResearcherAgent
from app.api.websocket import manager
import logging
import asyncio
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ideas",
    tags=["ideas"]
)

# Create agent instances
idea_generator = IdeaGeneratorAgent()
validator = ValidatorAgent()
pain_point_researcher = PainPointResearcherAgent()

@router.post("/generate", response_model=schemas.StartupIdea)
async def generate_idea(
    request: schemas.IdeaGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate a single startup idea using AI"""
    try:
        # Generate idea using AI agent
        idea_data = await idea_generator.generate_idea(
            market_focus=request.market_focus,
            innovation_type=request.innovation_type,
            target_demographic=request.target_demographic,
            problem_area=request.problem_area
        )
        
        # Log the generated data for debugging
        logger.info(f"Generated idea data: {idea_data}")
        
        idea_create = schemas.StartupIdeaCreate(**idea_data)
        return crud.create_startup_idea(db, idea_create)
    except Exception as e:
        logger.error(f"Error in generate_idea endpoint: {str(e)}")
        logger.error(f"Generated data was: {locals().get('idea_data', 'Not generated')}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/goldmine", response_model=List[schemas.StartupIdeaWithValidation])
async def goldmine_ideas(
    request: schemas.IdeaGenerationRequest,
    db: Session = Depends(get_db),
    num_ideas: int = Query(5, ge=1, le=10, description="Number of ideas to generate and validate")
):
    """Gold Mining Method: Generate multiple ideas, validate all, return only validated ones"""
    session_id = str(uuid.uuid4())
    
    try:
        validated_ideas = []
        ideas_generated = 0
        ideas_validated = 0
        
        logger.info(f"Starting Gold Mining process for {num_ideas} ideas")
        
        # Send start notification
        await manager.send_goldmine_update(
            session_id,
            "started",
            {"target": num_ideas, "message": "Starting goldmine process"}
        )
        
        # Generate and validate ideas until we have enough validated ones
        max_attempts = max(num_ideas * 2, 5)  # Generate up to 2x (minimum 5) to ensure we get some valid ones
        target_validated = max(1, min(num_ideas // 2, 3))  # At least 1, up to half of requested or 3
        rate_limit_errors = 0
        max_rate_limit_errors = 3  # Stop after 3 rate limit errors
        
        while len(validated_ideas) < target_validated and ideas_generated < max_attempts:
            # Generate a batch of ideas
            remaining_attempts = max_attempts - ideas_generated
            batch_size = min(5, remaining_attempts)
            
            if batch_size <= 0:
                break
                
            for _ in range(batch_size):
                try:
                    # Generate idea
                    idea_data = await idea_generator.generate_idea(
                        market_focus=request.market_focus,
                        innovation_type=request.innovation_type,
                        target_demographic=request.target_demographic,
                        problem_area=request.problem_area
                    )
                    ideas_generated += 1
                    
                    # Send progress update
                    await manager.send_goldmine_update(
                        session_id,
                        "idea_generated", 
                        {
                            "current_idea": idea_data.get('title', 'Untitled'),
                            "generated": ideas_generated,
                            "validated": ideas_validated
                        }
                    )
                    
                    # Save idea to database with market_focus and innovation_type
                    idea_data['market_focus'] = request.market_focus
                    idea_data['innovation_type'] = request.innovation_type
                    idea_create = schemas.StartupIdeaCreate(**idea_data)
                    idea = crud.create_startup_idea(db, idea_create)
                    
                    # Validate the idea
                    validation_data = await validator.validate_idea(
                        idea=idea,
                        market_research=None,
                        validation_depth="standard"
                    )
                    
                    # Check if idea passes validation (score > 70)
                    total_score = (
                        validation_data["problem_score"] * 0.25 +
                        validation_data["solution_score"] * 0.25 +
                        validation_data["market_score"] * 0.30 +
                        validation_data["execution_score"] * 0.20
                    )
                    
                    if total_score >= 70:  # Validation threshold
                        ideas_validated += 1
                        # Add idea_id to validation data
                        validation_data["idea_id"] = idea.id
                        
                        # Send validation success update
                        await manager.send_goldmine_update(
                            session_id,
                            "idea_validated",
                            {
                                "idea_title": idea.title,
                                "score": total_score,
                                "validated": ideas_validated
                            }
                        )
                        
                        # Save validation result
                        validation_create = schemas.ValidationResultCreate(**validation_data)
                        validation = crud.create_validation_result(db, validation_create)
                        
                        # Update idea status to validated
                        crud.update_startup_idea(db, idea.id, {"status": "validated"})
                        
                        # Research pain point evidence for validated ideas
                        try:
                            evidence_list = await pain_point_researcher.find_pain_point_evidence(
                                problem_statement=idea.problem_statement,
                                target_market=idea.target_market,
                                market_focus=idea.market_focus,
                                problem_area=request.problem_area
                            )
                            
                            # Save evidence to database
                            logger.info(f"Found {len(evidence_list)} pain point evidence for idea {idea.id}")
                            if evidence_list:
                                evidence_creates = []
                                for evidence in evidence_list:
                                    evidence_create = schemas.PainPointEvidenceCreate(
                                        idea_id=idea.id,
                                        platform=evidence.get('platform', 'Unknown'),
                                        source_url=evidence.get('source_url', ''),
                                        title=evidence.get('title'),
                                        snippet=evidence.get('snippet', ''),
                                        author=evidence.get('author'),
                                        upvotes=evidence.get('upvotes'),
                                        date_posted=evidence.get('date_posted'),
                                        relevance_score=evidence.get('relevance_score', 0.5)
                                    )
                                    evidence_creates.append(evidence_create)
                                
                                saved_evidence = crud.create_multiple_pain_point_evidence(db, evidence_creates)
                                logger.info(f"Found and saved {len(saved_evidence)} pain point evidence for idea {idea.id}")
                        except Exception as e:
                            logger.error(f"Error researching pain points for idea {idea.id}: {e}")
                            # Don't fail the whole process if evidence research fails
                            saved_evidence = []
                        
                        # Create combined response
                        idea_dict = idea.__dict__.copy()
                        validation_dict = validation.__dict__.copy()
                        
                        # Create the response using the schemas
                        idea_with_validation = schemas.StartupIdeaWithValidation(
                            id=idea.id,
                            title=idea.title,
                            problem_statement=idea.problem_statement,
                            solution_outline=idea.solution_outline,
                            target_market=idea.target_market,
                            unique_value_proposition=idea.unique_value_proposition,
                            market_focus=idea.market_focus,
                            innovation_type=idea.innovation_type,
                            status="validated",
                            created_at=idea.created_at,
                            updated_at=idea.updated_at,
                            validation=schemas.ValidationResult(
                                id=validation.id,
                                idea_id=validation.idea_id,
                                problem_score=validation.problem_score,
                                solution_score=validation.solution_score,
                                market_score=validation.market_score,
                                execution_score=validation.execution_score,
                                overall_score=validation.overall_score,
                                validation_details=validation.validation_details,
                                validation_notes=validation.validation_notes,
                                validated_at=validation.validated_at
                            ),
                            pain_point_evidence=[
                                schemas.PainPointEvidence(
                                    id=ev.id,
                                    idea_id=ev.idea_id,
                                    platform=ev.platform,
                                    source_url=ev.source_url,
                                    title=ev.title,
                                    snippet=ev.snippet,
                                    author=ev.author,
                                    upvotes=ev.upvotes,
                                    date_posted=ev.date_posted,
                                    date_found=ev.date_found,
                                    relevance_score=ev.relevance_score
                                ) for ev in saved_evidence
                            ] if 'saved_evidence' in locals() else None
                        )
                        validated_ideas.append(idea_with_validation)
                        logger.info(f"✅ Idea '{idea.title}' passed validation with score {total_score:.1f}")
                    else:
                        logger.info(f"❌ Idea '{idea.title}' failed validation with score {total_score:.1f}")
                        # Mark idea as rejected by updating its status
                        crud.update_startup_idea(db, idea.id, {"status": "rejected"})
                        
                except Exception as e:
                    logger.error(f"Error processing idea: {str(e)}")
                    # Check if it's a rate limit error
                    if "429" in str(e) or "rate" in str(e).lower():
                        rate_limit_errors += 1
                        logger.warning(f"Rate limit error #{rate_limit_errors}")
                        if rate_limit_errors >= max_rate_limit_errors:
                            logger.warning("Too many rate limit errors, returning partial results")
                            break
                        # Wait before retrying
                        await asyncio.sleep(10)
                    continue
            
            # Log progress after each batch
            logger.info(f"Progress: Generated {ideas_generated}/{max_attempts}, Validated {len(validated_ideas)}/{target_validated}")
        
        logger.info(f"🏁 Gold Mining complete: Generated {ideas_generated} ideas, validated {ideas_validated}")
        
        # If we have some results, return them even if incomplete
        if validated_ideas:
            return validated_ideas
        elif rate_limit_errors >= max_rate_limit_errors:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please try again later or use your own API key."
            )
        else:
            # No ideas passed validation
            return []
        
    except Exception as e:
        logger.error(f"Error in goldmine_ideas endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.StartupIdea])
async def get_ideas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    market_focus: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all startup ideas with optional filtering"""
    if market_focus:
        ideas = crud.get_ideas_by_market_focus(db, market_focus)
        return ideas[skip:skip+limit]
    return crud.get_startup_ideas(db, skip=skip, limit=limit)

@router.get("/{idea_id}", response_model=schemas.StartupIdeaWithValidation)
async def get_idea(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific startup idea with its latest validation and research"""
    idea = crud.get_startup_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Get latest validation and research
    latest_validation = crud.get_latest_validation_result(db, idea_id)
    latest_research = crud.get_latest_market_research(db, idea_id)
    
    # Convert to response model
    idea_dict = idea.__dict__.copy()
    idea_dict['latest_validation'] = latest_validation
    idea_dict['latest_research'] = latest_research
    
    return schemas.StartupIdeaWithValidation(**idea_dict)

@router.put("/{idea_id}", response_model=schemas.StartupIdea)
async def update_idea(
    idea_id: int,
    idea_update: schemas.StartupIdeaUpdate,
    db: Session = Depends(get_db)
):
    """Update a startup idea"""
    idea = crud.update_startup_idea(db, idea_id, idea_update)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.delete("/{idea_id}")
async def delete_idea(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Delete a startup idea"""
    if not crud.delete_startup_idea(db, idea_id):
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea deleted successfully"}

@router.get("/search/{query}", response_model=List[schemas.StartupIdea])
async def search_ideas(
    query: str,
    db: Session = Depends(get_db)
):
    """Search ideas by title, problem statement, or solution"""
    return crud.search_startup_ideas(db, query)