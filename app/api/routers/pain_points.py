"""Pain Points Discovery API Router"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.db.database import get_db
from app.db import crud, schemas
from app.agents.pain_point_researcher import PainPointResearcherAgent
from app.agents.browser_pain_point_agent import BrowserPainPointAgent
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/pain-points",
    tags=["pain-points"]
)

# Create agent instances
pain_point_researcher = PainPointResearcherAgent()
browser_agent = None  # Will be initialized on demand

@router.post("/discover", response_model=Dict)
async def discover_pain_points(
    request: schemas.PainPointDiscoveryRequest,
    db: Session = Depends(get_db),
    use_browser: bool = False
):
    """
    Discover pain points using Perplexity and optionally browser scraping
    
    - **use_browser**: Enable browser-based scraping for deeper discovery (slower but more thorough)
    """
    try:
        results = {
            "communities": {},
            "google_dorks": [],
            "pain_points": [],
            "discovery_method": "perplexity_only"
        }
        
        # Step 1: Discover communities using Perplexity
        logger.info(f"Discovering communities for {request.target_market} in {request.market_focus}")
        communities = await pain_point_researcher.discover_communities(
            target_market=request.target_market,
            market_focus=request.market_focus,
            problem_area=request.problem_area
        )
        results["communities"] = communities
        
        # Step 2: Generate Google dorks
        dorks = await pain_point_researcher.generate_google_dorks(
            problem_statement=request.problem_statement,
            target_market=request.target_market,
            communities=communities
        )
        results["google_dorks"] = dorks[:10]  # Return top 10 for reference
        
        # Step 3: Search for pain points
        if use_browser and request.enable_browser_scraping:
            # Initialize browser agent if needed
            global browser_agent
            if browser_agent is None:
                browser_agent = BrowserPainPointAgent()
                await browser_agent.initialize()
            
            results["discovery_method"] = "perplexity_and_browser"
            
            # Use both methods in parallel
            perplexity_task = pain_point_researcher.search_pain_points_advanced(
                problem_statement=request.problem_statement,
                target_market=request.target_market,
                market_focus=request.market_focus,
                problem_area=request.problem_area,
                max_results=request.max_results // 2
            )
            
            # Browser scraping tasks
            browser_tasks = []
            
            # Scrape top Reddit communities
            for subreddit in communities.get('reddit', [])[:3]:
                browser_tasks.append(
                    browser_agent.scrape_reddit_pain_points(
                        subreddit=subreddit,
                        pain_keywords=request.problem_statement.split()[:5],
                        max_posts=5
                    )
                )
            
            # Execute Google dork searches
            if dorks:
                browser_tasks.append(
                    browser_agent.search_google_dorks(
                        dork_queries=dorks[:3],
                        max_results=5
                    )
                )
            
            # Gather all results
            all_results = await asyncio.gather(
                perplexity_task,
                *browser_tasks,
                return_exceptions=True
            )
            
            # Process results
            pain_points = []
            
            # Add Perplexity results
            if not isinstance(all_results[0], Exception):
                pain_points.extend(all_results[0])
            
            # Add browser results
            for i, result in enumerate(all_results[1:], 1):
                if not isinstance(result, Exception):
                    if isinstance(result, list):
                        for item in result:
                            # Convert browser format to standard format
                            if 'content' in item:
                                item['snippet'] = item.pop('content', '')[:1000]
                            if 'pain_score' in item:
                                item['relevance_score'] = item.pop('pain_score')
                            pain_points.append(item)
                else:
                    logger.error(f"Browser task {i} failed: {result}")
            
        else:
            # Perplexity only
            pain_points = await pain_point_researcher.search_pain_points_advanced(
                problem_statement=request.problem_statement,
                target_market=request.target_market,
                market_focus=request.market_focus,
                problem_area=request.problem_area,
                max_results=request.max_results
            )
        
        # Sort by relevance and deduplicate
        seen_urls = set()
        unique_pain_points = []
        for pp in sorted(pain_points, key=lambda x: x.get('relevance_score', 0), reverse=True):
            url = pp.get('source_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_pain_points.append(pp)
                if len(unique_pain_points) >= request.max_results:
                    break
        
        results["pain_points"] = unique_pain_points
        results["total_discovered"] = len(unique_pain_points)
        
        # Save to database if idea_id is provided
        if request.idea_id:
            evidence_creates = []
            for pp in unique_pain_points:
                evidence_create = schemas.PainPointEvidenceCreate(
                    idea_id=request.idea_id,
                    platform=pp.get('platform', 'Unknown'),
                    source_url=pp.get('source_url', ''),
                    title=pp.get('title'),
                    snippet=pp.get('snippet', ''),
                    author=pp.get('author'),
                    upvotes=pp.get('upvotes'),
                    date_posted=pp.get('date_posted'),
                    relevance_score=pp.get('relevance_score', 0.5),
                    subreddit=pp.get('subreddit') or pp.get('metadata', {}).get('subreddit'),
                    comment_count=pp.get('comment_count') or pp.get('metadata', {}).get('comments')
                )
                evidence_creates.append(evidence_create)
            
            if evidence_creates:
                saved = crud.create_multiple_pain_point_evidence(db, evidence_creates)
                logger.info(f"Saved {len(saved)} pain points to database for idea {request.idea_id}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in pain point discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/communities/{target_market}", response_model=Dict)
async def get_relevant_communities(
    target_market: str,
    market_focus: Optional[str] = None,
    problem_area: Optional[str] = None
):
    """Get relevant communities for a target market"""
    try:
        communities = await pain_point_researcher.discover_communities(
            target_market=target_market,
            market_focus=market_focus or "",
            problem_area=problem_area
        )
        
        return {
            "target_market": target_market,
            "market_focus": market_focus,
            "communities": communities,
            "total_communities": sum(len(v) for v in communities.values())
        }
        
    except Exception as e:
        logger.error(f"Error discovering communities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google-dorks", response_model=List[str])
async def generate_google_dorks(
    request: schemas.GoogleDorkRequest
):
    """Generate Google dork queries for pain point discovery"""
    try:
        # First get communities if not provided
        communities = request.communities or await pain_point_researcher.discover_communities(
            target_market=request.target_market,
            market_focus=request.market_focus or "",
            problem_area=request.problem_area
        )
        
        dorks = await pain_point_researcher.generate_google_dorks(
            problem_statement=request.problem_statement,
            target_market=request.target_market,
            communities=communities
        )
        
        return dorks[:request.max_dorks] if request.max_dorks else dorks
        
    except Exception as e:
        logger.error(f"Error generating Google dorks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evidence/{idea_id}", response_model=List[schemas.PainPointEvidence])
async def get_pain_point_evidence(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """Get all pain point evidence for a specific idea"""
    evidence = crud.get_pain_point_evidence_by_idea(db, idea_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="No evidence found for this idea")
    return evidence

@router.delete("/evidence/{evidence_id}")
async def delete_pain_point_evidence(
    evidence_id: int,
    db: Session = Depends(get_db)
):
    """Delete specific pain point evidence"""
    if not crud.delete_pain_point_evidence(db, evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"message": "Evidence deleted successfully"}

@router.post("/browser/cleanup")
async def cleanup_browser():
    """Clean up browser resources"""
    global browser_agent
    if browser_agent:
        await browser_agent.close()
        browser_agent = None
        return {"message": "Browser agent cleaned up successfully"}
    return {"message": "No browser agent to clean up"}

@router.get("/stats", response_model=Dict)
async def get_pain_point_stats(db: Session = Depends(get_db)):
    """Get statistics about pain point discovery"""
    try:
        from app.db import models
        from sqlalchemy import func
        
        total_evidence = db.query(models.PainPointEvidence).count()
        evidence_by_platform = db.query(
            models.PainPointEvidence.platform,
            func.count(models.PainPointEvidence.id)
        ).group_by(models.PainPointEvidence.platform).all()
        
        avg_relevance = db.query(
            func.avg(models.PainPointEvidence.relevance_score)
        ).scalar() or 0
        
        return {
            "total_evidence_collected": total_evidence,
            "evidence_by_platform": dict(evidence_by_platform),
            "average_relevance_score": float(avg_relevance),
            "last_discovery": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting pain point stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))