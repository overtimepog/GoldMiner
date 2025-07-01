import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import backoff
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    # Free models configuration with fallbacks
    FREE_MODELS = {
        "reasoning": "google/gemini-2.0-flash-exp:free",
        "creative": "meta-llama/llama-4-maverick:free",
        "processing": "mistralai/mistral-7b-instruct:free",
        "fallback": "nousresearch/hermes-3-llama-3.1-405b:free"
    }
    
    # Rate limit tracking
    RATE_LIMITS = {
        "google/gemini-2.0-flash-exp:free": {"limit": 4, "window": 60, "last_reset": 0, "count": 0},
        "meta-llama/llama-4-maverick:free": {"limit": 10, "window": 60, "last_reset": 0, "count": 0},
        "mistralai/mistral-7b-instruct:free": {"limit": 10, "window": 60, "last_reset": 0, "count": 0}
    }
    
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        self.cache = {}  # Simple in-memory cache
        
    def check_rate_limit(self, model: str) -> bool:
        """Check if we can use a model without hitting rate limits"""
        if model not in self.RATE_LIMITS:
            return True
            
        limit_info = self.RATE_LIMITS[model]
        current_time = time.time()
        
        # Reset counter if window has passed
        if current_time - limit_info["last_reset"] > limit_info["window"]:
            limit_info["count"] = 0
            limit_info["last_reset"] = current_time
            
        # Check if under limit
        return limit_info["count"] < limit_info["limit"]
    
    def increment_rate_limit(self, model: str):
        """Increment the rate limit counter for a model"""
        if model in self.RATE_LIMITS:
            self.RATE_LIMITS[model]["count"] += 1
    
    def get_model_for_task(self, task_type: str) -> str:
        """Select appropriate model based on task type and rate limits"""
        model_mapping = {
            "idea_generation": self.FREE_MODELS["creative"],
            "market_research": self.FREE_MODELS["reasoning"],
            "validation": self.FREE_MODELS["processing"],
            "analysis": self.FREE_MODELS["reasoning"],
            "summary": self.FREE_MODELS["processing"],
            "processing": self.FREE_MODELS["processing"]
        }
        
        preferred_model = model_mapping.get(task_type, self.FREE_MODELS["reasoning"])
        
        # Check if preferred model is available
        if self.check_rate_limit(preferred_model):
            return preferred_model
            
        # Try alternative models
        for model in self.FREE_MODELS.values():
            if model != preferred_model and self.check_rate_limit(model):
                logger.info(f"Using alternative model {model} due to rate limits")
                return model
                
        # If all rate limited, return fallback
        logger.warning("All models rate limited, using fallback")
        return self.FREE_MODELS["fallback"]
    
    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=3,
        max_time=30
    )
    async def complete(
        self,
        prompt: str,
        task_type: str = "reasoning",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        use_cache: bool = True
    ) -> str:
        """Generate completion with automatic retries and caching"""
        
        # Check cache
        cache_key = f"{task_type}:{hash(prompt)}"
        if use_cache and cache_key in self.cache:
            logger.info(f"Cache hit for {task_type}")
            return self.cache[cache_key]
        
        model = self.get_model_for_task(task_type)
        logger.info(f"Using model {model} for {task_type}")
        
        try:
            # Increment rate limit counter
            self.increment_rate_limit(model)
            
            # Add timeout for API calls
            import asyncio
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(task_type)},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers={
                        "HTTP-Referer": "https://goldminer-ai.com",
                        "X-Title": "GoldMiner AI Startup Validator"
                    }
                ),
                timeout=30.0  # 30 second timeout
            )
            
            result = response.choices[0].message.content
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = result
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"OpenRouter API timeout after 30s for {task_type}")
            raise Exception("API request timed out")
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            logger.error(f"Model: {model}, Task: {task_type}")
            # If rate limit error, wait a bit before retrying
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning(f"Rate limit hit for {model}, waiting 5s...")
                await asyncio.sleep(5)
            raise
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Get specialized system prompt for different tasks"""
        prompts = {
            "idea_generation": "You are an innovative startup idea generator. Create unique, viable business concepts. ALWAYS respond with valid JSON containing exactly these keys: title, problem_statement, solution_outline, target_market, unique_value_proposition.",
            "market_research": "You are a market research analyst. Provide comprehensive analysis. ALWAYS respond with valid JSON as requested.",
            "validation": "You are a startup validation expert. Evaluate ideas thoroughly. ALWAYS respond with valid JSON containing scores and analysis.",
            "analysis": "You are a business analyst. Provide detailed insights. Structure your response as valid JSON.",
            "summary": "You are a concise summarizer. Extract key insights clearly.",
            "processing": "You are a helpful assistant. Follow instructions precisely and return structured data as requested."
        }
        return prompts.get(task_type, "You are a helpful AI assistant.")
    
    async def batch_complete(
        self,
        prompts: List[Dict[str, str]],
        task_type: str = "reasoning"
    ) -> List[str]:
        """Process multiple prompts in parallel"""
        tasks = [
            self.complete(p["prompt"], task_type, p.get("temperature", 0.7))
            for p in prompts
        ]
        return await asyncio.gather(*tasks)
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        logger.info("Cache cleared")

# Singleton instance
openrouter_client = OpenRouterClient()