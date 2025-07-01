import json
import logging
from typing import Dict, Optional
from app.core.openrouter import openrouter_client
from app.core.prompts import MARKET_RESEARCH_PROMPT, COMPETITOR_ANALYSIS_PROMPT, TREND_ANALYSIS_PROMPT
from app.db.schemas import StartupIdea

logger = logging.getLogger(__name__)

class MarketResearchAgent:
    """Agent for conducting market research on startup ideas"""
    
    def __init__(self):
        self.client = openrouter_client
    
    async def research_idea(
        self,
        idea: StartupIdea,
        research_depth: str = "standard"
    ) -> Dict[str, any]:
        """Conduct comprehensive market research for a startup idea"""
        
        # Build research prompt
        prompt = MARKET_RESEARCH_PROMPT.format(
            title=idea.title,
            problem_statement=idea.problem_statement,
            solution_outline=idea.solution_outline,
            target_market=idea.target_market
        )
        
        try:
            # Get market research from AI
            response = await self.client.complete(
                prompt=prompt,
                task_type="market_research",
                temperature=0.3,  # Lower temperature for factual research
                max_tokens=2500
            )
            
            # Parse response
            research_data = self._parse_research_response(response)
            
            # Add additional research for deeper analysis
            if research_depth in ["deep", "comprehensive"]:
                competitor_data = await self._research_competitors(idea)
                research_data["competitor_analysis"].update(competitor_data)
                
                if research_depth == "comprehensive":
                    trend_data = await self._research_trends(idea)
                    research_data["trend_analysis"].update(trend_data)
            
            return research_data
            
        except Exception as e:
            logger.error(f"Error conducting market research: {str(e)}")
            return self._create_fallback_research()
    
    async def _research_competitors(self, idea: StartupIdea) -> Dict[str, any]:
        """Deep dive into competitor analysis"""
        prompt = COMPETITOR_ANALYSIS_PROMPT.format(
            market_focus=idea.market_focus or "general",
            problem_statement=idea.problem_statement
        )
        
        try:
            response = await self.client.complete(
                prompt=prompt,
                task_type="analysis",
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse competitor analysis
            return self._parse_competitor_response(response)
            
        except Exception as e:
            logger.error(f"Error researching competitors: {str(e)}")
            return {}
    
    async def _research_trends(self, idea: StartupIdea) -> Dict[str, any]:
        """Analyze market trends"""
        prompt = TREND_ANALYSIS_PROMPT.format(
            market_focus=idea.market_focus or "general",
            innovation_type=idea.innovation_type or "technology"
        )
        
        try:
            response = await self.client.complete(
                prompt=prompt,
                task_type="analysis",
                temperature=0.4,
                max_tokens=1200
            )
            
            # Parse trend analysis
            return self._parse_trend_response(response)
            
        except Exception as e:
            logger.error(f"Error researching trends: {str(e)}")
            return {}
    
    def _parse_research_response(self, response: str) -> Dict[str, any]:
        """Parse market research response into structured data"""
        try:
            # Try to extract JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Ensure all required fields exist
                return self._validate_research_data(data)
            else:
                return self._create_fallback_research()
                
        except json.JSONDecodeError:
            return self._create_fallback_research()
    
    def _validate_research_data(self, data: Dict) -> Dict[str, any]:
        """Validate and fill missing research data"""
        default_data = self._create_fallback_research()
        
        # Merge with defaults to ensure all fields exist
        for key, value in default_data.items():
            if key not in data or not data[key]:
                data[key] = value
        
        return data
    
    def _parse_competitor_response(self, response: str) -> Dict[str, any]:
        """Parse competitor analysis response"""
        # Simple parsing logic for competitor data
        competitors = {
            "detailed_analysis": [],
            "market_leaders": [],
            "opportunities": []
        }
        
        # Extract competitor information from response
        lines = response.split("\n")
        for line in lines:
            if "competitor" in line.lower():
                competitors["detailed_analysis"].append(line.strip())
            elif "leader" in line.lower():
                competitors["market_leaders"].append(line.strip())
            elif "opportunity" in line.lower() or "gap" in line.lower():
                competitors["opportunities"].append(line.strip())
        
        return competitors
    
    def _parse_trend_response(self, response: str) -> Dict[str, any]:
        """Parse trend analysis response"""
        trends = {
            "technology_trends": [],
            "market_shifts": [],
            "future_outlook": []
        }
        
        # Extract trend information
        lines = response.split("\n")
        for line in lines:
            if "technology" in line.lower() or "tech" in line.lower():
                trends["technology_trends"].append(line.strip())
            elif "market" in line.lower() or "shift" in line.lower():
                trends["market_shifts"].append(line.strip())
            elif "future" in line.lower() or "outlook" in line.lower():
                trends["future_outlook"].append(line.strip())
        
        return trends
    
    def _create_fallback_research(self) -> Dict[str, any]:
        """Create fallback research data if AI fails"""
        return {
            "market_size_data": {
                "tam": "$10B+",
                "sam": "$2B",
                "som": "$200M"
            },
            "market_size": "$10B+ Total Addressable Market",
            "growth_rate": 15.0,
            "competitor_analysis": {
                "direct_competitors": ["Industry Leader A", "Startup B"],
                "indirect_competitors": ["Traditional Solution C"],
                "competitive_advantages": ["AI-powered", "Cost-effective"]
            },
            "trend_analysis": {
                "growing_trends": ["Digital transformation", "AI adoption"],
                "declining_trends": ["Manual processes"],
                "opportunities": ["Emerging markets", "SMB segment"]
            },
            "target_audience_insights": {
                "demographics": {"age": "25-45", "income": "$50k+"},
                "pain_points": ["Efficiency", "Cost", "Scalability"],
                "buying_behavior": "Technology-forward, ROI-focused"
            }
        }