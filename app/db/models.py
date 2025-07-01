from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class StartupIdea(Base):
    __tablename__ = "startup_ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    problem_statement = Column(Text, nullable=False)
    solution_outline = Column(Text, nullable=False)
    target_market = Column(String(255), nullable=False)
    unique_value_proposition = Column(Text)
    market_focus = Column(String(100))
    innovation_type = Column(String(50))
    status = Column(String(20), default="pending")  # pending, validated, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    validation_results = relationship("ValidationResult", back_populates="idea", cascade="all, delete-orphan")
    market_research = relationship("MarketResearch", back_populates="idea", cascade="all, delete-orphan")
    pain_point_evidence = relationship("PainPointEvidence", back_populates="idea", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
        Index('idx_market_focus', 'market_focus'),
    )

class ValidationResult(Base):
    __tablename__ = "validation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("startup_ideas.id"), nullable=False)
    problem_score = Column(Float, nullable=False)
    solution_score = Column(Float, nullable=False)
    market_score = Column(Float, nullable=False)
    execution_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    validation_details = Column(JSON)
    validation_notes = Column(Text)
    validated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    idea = relationship("StartupIdea", back_populates="validation_results")
    
    # Indexes
    __table_args__ = (
        Index('idx_idea_id', 'idea_id'),
        Index('idx_overall_score', 'overall_score'),
        Index('idx_validated_at', 'validated_at'),
    )

class MarketResearch(Base):
    __tablename__ = "market_research"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("startup_ideas.id"), nullable=False)
    competitor_analysis = Column(JSON)
    market_size_data = Column(JSON)
    market_size = Column(String(100))
    growth_rate = Column(Float)
    trend_analysis = Column(JSON)
    target_audience_insights = Column(JSON)
    research_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    idea = relationship("StartupIdea", back_populates="market_research")
    
    # Indexes
    __table_args__ = (
        Index('idx_research_idea_id', 'idea_id'),
        Index('idx_research_timestamp', 'research_timestamp'),
    )

class PainPointEvidence(Base):
    __tablename__ = "pain_point_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("startup_ideas.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # Reddit, Twitter, Facebook, HackerNews, etc.
    source_url = Column(Text, nullable=False)
    title = Column(String(500))  # Post/thread title
    snippet = Column(Text, nullable=False)  # The actual complaint/pain point text
    author = Column(String(255))  # Username/author if available
    upvotes = Column(Integer)  # Engagement metric
    date_posted = Column(DateTime(timezone=True))  # When the original was posted
    date_found = Column(DateTime(timezone=True), server_default=func.now())
    relevance_score = Column(Float)  # How relevant this evidence is (0-1)
    
    # Additional fields for better tracking
    subreddit = Column(String(100))  # For Reddit posts
    comment_count = Column(Integer)  # Number of comments/replies
    
    # Relationships
    idea = relationship("StartupIdea", back_populates="pain_point_evidence")
    
    # Indexes
    __table_args__ = (
        Index('idx_evidence_idea_id', 'idea_id'),
        Index('idx_evidence_platform', 'platform'),
        Index('idx_evidence_relevance', 'relevance_score'),
    )