from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Startup Idea Schemas
class StartupIdeaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    problem_statement: str = Field(..., min_length=10)
    solution_outline: str = Field(..., min_length=10)
    target_market: str = Field(..., min_length=1, max_length=255)
    unique_value_proposition: Optional[str] = None
    market_focus: Optional[str] = None
    innovation_type: Optional[str] = None

class StartupIdeaCreate(StartupIdeaBase):
    pass

class StartupIdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    problem_statement: Optional[str] = Field(None, min_length=10)
    solution_outline: Optional[str] = Field(None, min_length=10)
    target_market: Optional[str] = Field(None, min_length=1, max_length=255)
    unique_value_proposition: Optional[str] = None
    market_focus: Optional[str] = None
    innovation_type: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|validated|rejected)$")

class StartupIdea(StartupIdeaBase):
    id: int
    status: Optional[str] = "pending"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Validation Result Schemas
class ValidationResultBase(BaseModel):
    idea_id: int
    problem_score: float = Field(..., ge=0, le=100)
    solution_score: float = Field(..., ge=0, le=100)
    market_score: float = Field(..., ge=0, le=100)
    execution_score: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)
    validation_details: Optional[Dict[str, Any]] = None
    validation_notes: Optional[str] = None
    
    @field_validator('overall_score', mode='before')
    def calculate_overall_score(cls, v, values):
        if v is None and all(k in values.data for k in ['problem_score', 'solution_score', 'market_score', 'execution_score']):
            # Calculate weighted average
            problem = values.data['problem_score'] * 0.25
            solution = values.data['solution_score'] * 0.25
            market = values.data['market_score'] * 0.30
            execution = values.data['execution_score'] * 0.20
            return problem + solution + market + execution
        return v

class ValidationResultCreate(ValidationResultBase):
    pass

class ValidationResult(ValidationResultBase):
    id: int
    validated_at: datetime
    
    class Config:
        from_attributes = True

# Market Research Schemas
class MarketResearchBase(BaseModel):
    idea_id: int
    competitor_analysis: Optional[Dict[str, Any]] = None
    market_size_data: Optional[Dict[str, Any]] = None
    market_size: Optional[str] = None
    growth_rate: Optional[float] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    target_audience_insights: Optional[Dict[str, Any]] = None

class MarketResearchCreate(MarketResearchBase):
    pass

class MarketResearch(MarketResearchBase):
    id: int
    research_timestamp: datetime
    
    class Config:
        from_attributes = True

# Pain Point Evidence Schemas
class PainPointEvidenceBase(BaseModel):
    idea_id: int
    platform: str = Field(..., min_length=1, max_length=50)
    source_url: str = Field(..., min_length=10)
    title: Optional[str] = Field(None, max_length=500)
    snippet: str = Field(..., min_length=10)
    author: Optional[str] = Field(None, max_length=255)
    upvotes: Optional[int] = None
    date_posted: Optional[datetime] = None
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    subreddit: Optional[str] = Field(None, max_length=100)
    comment_count: Optional[int] = None

class PainPointEvidenceCreate(PainPointEvidenceBase):
    pass

class PainPointEvidence(PainPointEvidenceBase):
    id: int
    date_found: datetime
    
    class Config:
        from_attributes = True

# Response Models
class StartupIdeaWithValidation(StartupIdea):
    validation: Optional[ValidationResult] = None
    latest_validation: Optional[ValidationResult] = None
    latest_research: Optional[MarketResearch] = None
    pain_point_evidence: Optional[List[PainPointEvidence]] = None

class IdeaGenerationRequest(BaseModel):
    market_focus: str
    innovation_type: str
    target_demographic: Optional[str] = None
    problem_area: Optional[str] = None
    
class ValidationRequest(BaseModel):
    idea_id: int
    validation_depth: str = Field(default="standard", pattern="^(standard|deep|comprehensive)$")

class MarketResearchRequest(BaseModel):
    idea_id: int
    research_depth: str = Field(default="standard", pattern="^(standard|deep|comprehensive)$")

# Pain Point Discovery Schemas
class PainPointDiscoveryRequest(BaseModel):
    problem_statement: str = Field(..., min_length=10)
    target_market: str = Field(..., min_length=1)
    market_focus: str = Field(..., min_length=1)
    problem_area: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=50)
    enable_browser_scraping: bool = Field(default=False)
    idea_id: Optional[int] = None

class GoogleDorkRequest(BaseModel):
    problem_statement: str = Field(..., min_length=10)
    target_market: str = Field(..., min_length=1)
    market_focus: Optional[str] = None
    problem_area: Optional[str] = None
    communities: Optional[Dict[str, List[str]]] = None
    max_dorks: Optional[int] = Field(None, ge=1, le=50)