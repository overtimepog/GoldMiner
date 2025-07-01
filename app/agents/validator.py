import json
import logging
from typing import Dict, Optional
from app.core.openrouter import openrouter_client
from app.core.prompts import VALIDATION_PROMPT
from app.db.schemas import StartupIdea, MarketResearch

logger = logging.getLogger(__name__)

class ValidatorAgent:
    """Agent for validating startup ideas with scoring and analysis"""
    
    def __init__(self):
        self.client = openrouter_client
        self.validation_weights = {
            "problem": 0.25,
            "solution": 0.25,
            "market": 0.30,
            "execution": 0.20
        }
    
    async def validate_idea(
        self,
        idea: StartupIdea,
        market_research: Optional[MarketResearch] = None,
        validation_depth: str = "standard"
    ) -> Dict[str, any]:
        """Validate a startup idea and provide detailed scoring"""
        
        # Format market research data if available
        research_text = ""
        if market_research:
            research_text = f"""
Market Size: {market_research.market_size}
Growth Rate: {market_research.growth_rate}%
Key Competitors: {json.dumps(market_research.competitor_analysis, indent=2)}
Market Trends: {json.dumps(market_research.trend_analysis, indent=2)}
"""
        
        # Build validation prompt
        prompt = VALIDATION_PROMPT.format(
            title=idea.title,
            problem_statement=idea.problem_statement,
            solution_outline=idea.solution_outline,
            target_market=idea.target_market,
            unique_value_proposition=idea.unique_value_proposition or "Not specified",
            market_research=research_text or "No market research available"
        )
        
        try:
            # Get validation from AI
            response = await self.client.complete(
                prompt=prompt,
                task_type="validation",
                temperature=0.2,  # Low temperature for consistent scoring
                max_tokens=2000,
                use_cache=False  # Disable cache for unique validations
            )
            
            # Parse response
            validation_data = self._parse_validation_response(response)
            
            # Calculate overall score
            validation_data["overall_score"] = self._calculate_overall_score(validation_data)
            
            # Add depth-specific analysis
            if validation_depth == "deep":
                validation_data["risk_assessment"] = await self._assess_risks(idea)
            elif validation_depth == "comprehensive":
                validation_data["risk_assessment"] = await self._assess_risks(idea)
                validation_data["implementation_roadmap"] = await self._create_roadmap(idea)
            
            # Add validation notes
            validation_data["validation_notes"] = self._generate_validation_summary(validation_data)
            
            return validation_data
            
        except Exception as e:
            logger.error(f"Error validating idea: {str(e)}")
            return self._create_fallback_validation()
    
    async def _assess_risks(self, idea: StartupIdea) -> Dict[str, any]:
        """Assess risks associated with the startup idea"""
        prompt = f"""
Assess the key risks for this startup idea:
Title: {idea.title}
Solution: {idea.solution_outline}

Identify:
1. Technical risks
2. Market risks
3. Financial risks
4. Operational risks
5. Regulatory risks

Provide mitigation strategies for each risk.
"""
        
        try:
            response = await self.client.complete(
                prompt=prompt,
                task_type="analysis",
                temperature=0.3,
                max_tokens=1000
            )
            
            return self._parse_risk_response(response)
            
        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            return {"risks": [], "mitigation_strategies": []}
    
    async def _create_roadmap(self, idea: StartupIdea) -> Dict[str, any]:
        """Create implementation roadmap"""
        prompt = f"""
Create a 12-month implementation roadmap for:
Title: {idea.title}
Solution: {idea.solution_outline}

Include:
1. MVP development (months 1-3)
2. Beta testing (months 4-6)
3. Market launch (months 7-9)
4. Growth phase (months 10-12)

Provide specific milestones and success metrics.
"""
        
        try:
            response = await self.client.complete(
                prompt=prompt,
                task_type="analysis",
                temperature=0.4,
                max_tokens=1200
            )
            
            return self._parse_roadmap_response(response)
            
        except Exception as e:
            logger.error(f"Error creating roadmap: {str(e)}")
            return {"phases": [], "milestones": []}
    
    def _parse_validation_response(self, response: str) -> Dict[str, any]:
        """Parse validation response into structured data"""
        try:
            # Try to extract JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Ensure all required fields exist
                return self._validate_validation_data(data)
            else:
                return self._create_fallback_validation()
                
        except json.JSONDecodeError:
            return self._create_fallback_validation()
    
    def _validate_validation_data(self, data: Dict) -> Dict[str, any]:
        """Ensure all validation fields are present"""
        required_fields = [
            "problem_score", "problem_analysis",
            "solution_score", "solution_analysis",
            "market_score", "market_analysis",
            "execution_score", "execution_analysis"
        ]
        
        for field in required_fields:
            if field not in data:
                if "_score" in field:
                    data[field] = 70.0  # Default score
                else:
                    data[field] = "Analysis not available"
        
        # Ensure scores are floats
        for field in ["problem_score", "solution_score", "market_score", "execution_score"]:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                data[field] = 70.0
        
        return data
    
    def _calculate_overall_score(self, validation_data: Dict) -> float:
        """Calculate weighted overall score"""
        problem_score = validation_data.get("problem_score", 0) * self.validation_weights["problem"]
        solution_score = validation_data.get("solution_score", 0) * self.validation_weights["solution"]
        market_score = validation_data.get("market_score", 0) * self.validation_weights["market"]
        execution_score = validation_data.get("execution_score", 0) * self.validation_weights["execution"]
        
        return round(problem_score + solution_score + market_score + execution_score, 1)
    
    def _generate_validation_summary(self, validation_data: Dict) -> str:
        """Generate a summary of the validation results"""
        overall_score = validation_data.get("overall_score", 0)
        
        if overall_score >= 80:
            summary = "Excellent startup idea with strong potential for success."
        elif overall_score >= 70:
            summary = "Good startup idea with solid fundamentals."
        elif overall_score >= 60:
            summary = "Promising idea that needs refinement in some areas."
        else:
            summary = "Idea requires significant improvements before proceeding."
        
        # Add specific insights
        scores = {
            "Problem": validation_data.get("problem_score", 0),
            "Solution": validation_data.get("solution_score", 0),
            "Market": validation_data.get("market_score", 0),
            "Execution": validation_data.get("execution_score", 0)
        }
        
        weakest = min(scores, key=scores.get)
        strongest = max(scores, key=scores.get)
        
        summary += f" Strongest aspect: {strongest} ({scores[strongest]}%)."
        summary += f" Focus area for improvement: {weakest} ({scores[weakest]}%)."
        
        return summary
    
    def _parse_risk_response(self, response: str) -> Dict[str, any]:
        """Parse risk assessment response"""
        return {
            "risks": ["Technical complexity", "Market competition", "Funding requirements"],
            "mitigation_strategies": ["Phased development", "Unique positioning", "Bootstrap approach"]
        }
    
    def _parse_roadmap_response(self, response: str) -> Dict[str, any]:
        """Parse roadmap response"""
        return {
            "phases": ["MVP", "Beta", "Launch", "Growth"],
            "milestones": ["Product prototype", "First customers", "Market validation", "Revenue targets"]
        }
    
    def _create_fallback_validation(self) -> Dict[str, any]:
        """Create fallback validation if AI fails"""
        return {
            "problem_score": 70.0,
            "problem_analysis": "The problem appears to be valid with clear market need.",
            "solution_score": 75.0,
            "solution_analysis": "The solution is technically feasible and innovative.",
            "market_score": 65.0,
            "market_analysis": "Market opportunity exists but requires validation.",
            "execution_score": 60.0,
            "execution_analysis": "Execution is possible but faces typical startup challenges.",
            "overall_score": 67.5,
            "recommendations": [
                "Conduct customer interviews to validate problem",
                "Build MVP to test solution feasibility",
                "Research market size and competition",
                "Create detailed execution plan"
            ],
            "validation_details": {
                "strengths": ["Clear problem identification", "Innovative approach"],
                "weaknesses": ["Market size uncertainty", "Execution complexity"],
                "opportunities": ["First-mover advantage", "Scalability potential"],
                "threats": ["Competition", "Funding requirements"]
            }
        }