import json
import logging
import re
import random
from typing import Dict, List, Optional
from app.core.openrouter import openrouter_client
from app.core.prompts import IDEA_GENERATION_PROMPT, IDEA_GENERATION_PROMPT_V2, get_diverse_problem_context

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    'title',
    'problem_statement',
    'solution_outline',
    'target_market',
    'unique_value_proposition'
]

class IdeaGeneratorAgent:
    """Agent for generating startup ideas using AI"""
    
    def __init__(self):
        self.client = openrouter_client
        self.generated_ideas_cache = set()  # Track generated ideas to avoid duplicates
        self.used_niches = set()  # Track used niches to ensure diversity
    
    async def generate_idea(
        self,
        market_focus: str,
        innovation_type: str,
        target_demographic: Optional[str] = None,
        problem_area: Optional[str] = None,
        retry_count: int = 0
    ) -> Dict[str, str]:
        """Generate a single startup idea based on parameters"""
        
        # Use improved prompt v2 for more diverse and specific ideas
        # Get a diverse problem context to avoid repetition
        diverse_context = get_diverse_problem_context(
            market_focus, 
            target_demographic or "General consumers",
            problem_area or "Efficiency and automation",
            self.used_niches
        )
        
        # Add to used niches
        self.used_niches.add(diverse_context)
        
        # Build prompt with diverse context
        prompt = IDEA_GENERATION_PROMPT_V2.format(
            market_focus=market_focus,
            innovation_type=innovation_type,
            target_demographic=diverse_context,  # Use diverse context instead
            problem_area=problem_area or "Efficiency and automation"
        )
        
        try:
            # Generate idea using creative model
            # Add randomness to prompt to avoid cache hits
            prompt += f"\n\nGeneration ID: {random.randint(1000, 9999)}"
            
            response = await self.client.complete(
                prompt=prompt,
                task_type="idea_generation",
                temperature=0.8 + (retry_count * 0.1),  # Increase temperature on retries
                max_tokens=1500,
                use_cache=False  # Disable cache for unique ideas
            )
            
            # Parse JSON response
            idea_data = self._parse_idea_response(response)
            
            # Validate required fields
            missing_fields = [field for field in REQUIRED_FIELDS if field not in idea_data or not idea_data[field]]
            
            if missing_fields:
                logger.warning(f"Missing fields in AI response: {missing_fields}")
                logger.warning(f"Parsed data: {idea_data}")
                logger.warning(f"Raw response first 1000 chars: {response[:1000]}")
                # Use fallback if parsing failed
                return self._create_fallback_idea(
                    market_focus, innovation_type, 
                    target_demographic, problem_area
                )
            
            # Check for duplicates
            idea_hash = hash(idea_data.get("title", ""))
            if idea_hash in self.generated_ideas_cache and retry_count < 3:
                # Regenerate if duplicate, but limit retries
                return await self.generate_idea(
                    market_focus, innovation_type, 
                    target_demographic, problem_area,
                    retry_count + 1
                )
            
            self.generated_ideas_cache.add(idea_hash)
            
            # Don't add metadata - it's not part of the schema
            # idea_data["market_focus"] = market_focus
            # idea_data["innovation_type"] = innovation_type
            
            return idea_data
            
        except Exception as e:
            logger.error(f"Error generating idea: {str(e)}")
            # Return fallback idea
            return self._create_fallback_idea(
                market_focus, innovation_type, 
                target_demographic, problem_area
            )
    
    def _parse_idea_response(self, response: str) -> Dict[str, str]:
        """Parse AI response into structured idea data with robust JSON extraction"""
        try:
            # First, try direct JSON parsing in case the response is pure JSON
            try:
                data = json.loads(response.strip())
                if all(field in data and data[field] for field in REQUIRED_FIELDS):
                    logger.info("Successfully parsed pure JSON response")
                    return data
            except json.JSONDecodeError:
                pass
            
            # Try to find JSON object with proper nesting
            # This regex looks for balanced braces
            json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if all(field in data and data[field] for field in REQUIRED_FIELDS):
                        logger.info("Successfully parsed JSON from response")
                        return data
                except json.JSONDecodeError:
                    continue
            
            # Try the old method of finding first { and last }
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start != -1 and json_end > json_start:
                try:
                    json_str = response[json_start:json_end + 1]
                    data = json.loads(json_str)
                    if all(field in data and data[field] for field in REQUIRED_FIELDS):
                        logger.info("Successfully parsed JSON using bracket matching")
                        return data
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error: {str(e)}")
                    
            # If still no valid JSON, try text parsing
            logger.warning(f"No valid JSON found in response, trying text parsing")
            return self._parse_text_response(response)
                
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict[str, str]:
        """Parse non-JSON response into structured data"""
        # Simple text parsing logic
        lines = response.strip().split("\n")
        idea_data = {}
        
        for line in lines:
            if "Title:" in line or "title:" in line:
                idea_data["title"] = line.split(":", 1)[1].strip()
            elif "Problem" in line and ":" in line:
                idea_data["problem_statement"] = line.split(":", 1)[1].strip()
            elif "Solution" in line and ":" in line:
                idea_data["solution_outline"] = line.split(":", 1)[1].strip()
            elif "Target" in line and ":" in line:
                idea_data["target_market"] = line.split(":", 1)[1].strip()
            elif "Value" in line and ":" in line:
                idea_data["unique_value_proposition"] = line.split(":", 1)[1].strip()
        
        return idea_data
    
    def _create_fallback_idea(
        self,
        market_focus: str,
        innovation_type: str,
        target_demographic: Optional[str],
        problem_area: Optional[str]
    ) -> Dict[str, str]:
        """Create a fallback idea if AI generation fails"""
        return {
            "title": f"Smart{market_focus[:15]}Hub",  # Ensure max 50 chars
            "problem_statement": f"In 2025, {target_demographic or 'businesses'} in {market_focus} face increasing challenges with {problem_area or 'efficiency'}, leading to lost productivity and higher costs.",
            "solution_outline": f"An {innovation_type} platform that uses advanced AI to automate workflows, predict issues, and optimize resource allocation specifically for {market_focus} needs.",
            "target_market": target_demographic or f"{market_focus} businesses and professionals",
            "unique_value_proposition": f"First {innovation_type} solution designed specifically for {market_focus} that reduces operational costs by 40% while improving outcomes."
        }
    
    async def generate_multiple_ideas(
        self,
        count: int,
        market_focus: str,
        innovation_type: str,
        target_demographic: Optional[str] = None,
        problem_area: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Generate multiple unique startup ideas"""
        ideas = []
        
        for _ in range(count):
            idea = await self.generate_idea(
                market_focus, innovation_type,
                target_demographic, problem_area
            )
            ideas.append(idea)
        
        return ideas
    
    def clear_cache(self):
        """Clear the generated ideas cache"""
        self.generated_ideas_cache.clear()
        self.used_niches.clear()