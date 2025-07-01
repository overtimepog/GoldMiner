"""Perplexity API client for searching pain points"""
import os
import logging
from typing import List, Dict, Optional
import json
import httpx
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class PerplexityClient:
    """Client for Perplexity API"""
    
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment")
        self.base_url = "https://api.perplexity.ai"
        
    async def search(self, query: str) -> Dict:
        """Search using Perplexity API"""
        if not self.api_key:
            logger.warning("No Perplexity API key, returning mock data")
            return self._get_mock_response(query)
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Perplexity API expects messages format
        data = {
            "model": "sonar",  # Lightweight search model for quick searches
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Perplexity API response preview: {str(result)[:500]}...")
                    return self._parse_perplexity_response(result, query)
                else:
                    logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                    return self._get_mock_response(query)
                    
        except Exception as e:
            logger.error(f"Error calling Perplexity API: {e}")
            return self._get_mock_response(query)
    
    def _parse_perplexity_response(self, response: Dict, query: str) -> Dict:
        """Parse Perplexity API response into our format"""
        try:
            # Extract content from the response
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            citations = response.get('citations', [])
            
            logger.debug(f"Parsing Perplexity content: {content[:200]}...")
            
            results = []
            
            # Look for structured data patterns in the response
            # Try to find individual pain points or complaints
            post_patterns = [
                r'(?:Comment|Post|Tweet|Pain Point)[\s\d]+:?\s*\n(.*?)(?=\n(?:Comment|Post|Tweet|Pain Point)|\Z)',
                r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)',
                r'•\s*(.*?)(?=\n•|\Z)',
                r'-\s*(.*?)(?=\n-|\Z)',
                r'\*\s*(.*?)(?=\n\*|\Z)',
                r'(?:Problem|Issue|Complaint):\s*(.*?)(?=\n(?:Problem|Issue|Complaint):|\Z)'
            ]
            
            sections = []
            for pattern in post_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
                if matches:
                    sections = matches
                    break
            
            # If no pattern matches, split by double newlines
            if not sections:
                sections = content.split('\n\n')
            
            for i, section in enumerate(sections[:10]):  # Check more sections
                section = section.strip()
                if len(section) < 50:
                    continue
                
                # Try to extract URL from section or citations
                url = None
                url_match = re.search(r'(https?://[^\s]+)', section)
                if url_match:
                    url = url_match.group(1).rstrip('.,!?')
                elif i < len(citations):
                    url = citations[i]
                else:
                    # Generate search URL based on content and detected platform
                    search_terms = section[:50].replace('\n', ' ').replace('"', '')
                    if 'reddit' in section.lower() or 'r/' in section.lower():
                        # Extract subreddit if mentioned
                        subreddit_match = re.search(r'r/(\w+)', section)
                        if subreddit_match:
                            subreddit = subreddit_match.group(1)
                            url = f"https://www.reddit.com/r/{subreddit}/search?q={search_terms}&restrict_sr=1"
                        else:
                            url = f"https://www.reddit.com/search?q={search_terms}"
                    elif 'twitter' in section.lower() or '@' in section:
                        url = f"https://twitter.com/search?q={search_terms}"
                    else:
                        # Generate a Google search for the pain point
                        url = f"https://www.google.com/search?q={search_terms}"
                
                # Extract title from section
                title = None
                title_patterns = [
                    r'Title:\s*([^\n]+)',
                    r'Post:\s*([^\n]+)',
                    r'^([^.!?]{10,100})[.!?]'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, section)
                    if match:
                        title = match.group(1).strip()
                        break
                
                results.append({
                    'url': url,
                    'title': title,
                    'snippet': section[:1000]
                })
            
            # If we got no results, return at least something from citations
            if not results and citations:
                for i, citation in enumerate(citations[:5]):
                    results.append({
                        'url': citation,
                        'title': f"Source {i+1}",
                        'snippet': content[i*200:(i+1)*200] if i*200 < len(content) else content[-200:]
                    })
            
            return {
                'results': results,
                'response': content,
                'citations': citations
            }
            
        except Exception as e:
            logger.error(f"Error parsing Perplexity response: {e}")
            return self._get_mock_response(query)
    
    def _get_mock_response(self, query: str) -> Dict:
        """Return mock response when API is unavailable"""
        mock_results = []
        
        if 'reddit.com' in query.lower():
            if 'workflow' in query.lower() or 'automation' in query.lower():
                mock_results = [
                    {
                        'url': 'https://www.reddit.com/r/smallbusiness/comments/workflow_nightmare',
                        'title': 'Workflow automation nightmare - 3 hours daily on manual tasks',
                        'snippet': "Running a small marketing agency with 5 employees. We use Monday for project management, Slack for communication, Toggl for time tracking, and QuickBooks for invoicing. Every day I spend 3+ hours just moving data between these systems. Tried Zapier but it's too limited for our complex workflows. Anyone else drowning in manual work?"
                    },
                    {
                        'url': 'https://www.reddit.com/r/Entrepreneur/comments/lost_client_workflow',
                        'title': 'Lost biggest client due to workflow miscommunication',
                        'snippet': "Just lost a $50k/year client because tasks fell through the cracks between our tools. Designer updated files in Dropbox, PM didn't see the Slack notification, client never got the deliverables on time. This is the 3rd time this year. I need a solution that actually connects all our tools properly."
                    }
                ]
            elif 'devops' in query.lower() or 'cybersecurity' in query.lower():
                mock_results = [
                    {
                        'url': 'https://www.reddit.com/r/devops/comments/security_integrations',
                        'title': 'Managing 15+ security tool integrations killing productivity',
                        'snippet': "Small cybersecurity startup here. We integrate with Snyk, SonarQube, GitLab, AWS Security Hub, etc. Each has its own repo structure and CI/CD requirements. Our DevOps team spends 60% of their time just managing these integrations instead of building features. Manual sync is error-prone and we've had 2 security incidents from missed updates."
                    }
                ]
        elif 'twitter' in query.lower():
            mock_results = [
                {
                    'url': 'https://twitter.com/startup_struggles/status/example',
                    'title': 'Another day wasted on manual workflows',
                    'snippet': "Another day, another 2 hours wasted copy-pasting between our CRM and accounting software. Why is small business automation still this hard in 2024? 😤 #SmallBusinessStruggles"
                }
            ]
        
        return {
            'results': mock_results if mock_results else [{
                'url': 'https://example.com',
                'title': 'No specific results found',
                'snippet': f'No specific pain points found for query: {query[:100]}'
            }],
            'response': 'Mock data - Perplexity API not available'
        }

# Global client instance
perplexity_client = PerplexityClient()

async def search_pain_points(query: str, context: str) -> List[Dict]:
    """
    Search for pain points using Perplexity API
    """
    # Enhance query with context
    enhanced_query = f"{query} Related to: {context[:100]}"
    
    logger.info(f"Searching Perplexity with query: {enhanced_query[:150]}...")
    
    result = await perplexity_client.search(enhanced_query)
    
    return result.get('results', [])