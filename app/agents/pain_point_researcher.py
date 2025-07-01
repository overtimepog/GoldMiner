"""Enhanced Pain Point Researcher using advanced Perplexity integration and Google dorks"""
import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class PainPointResearcherAgent:
    """Advanced agent for discovering pain points using Perplexity + Google dorks"""
    
    def __init__(self):
        self.platform_patterns = {
            'reddit': {
                'author': r'(?:u/|user:|username:|by\s+)(\w+)',
                'subreddit': r'(?:r/|subreddit:|in\s+)(\w+)',
                'upvotes': r'(\d+)\s*(?:upvotes?|points?|karma)',
                'comments': r'(\d+)\s*comments?',
                'awards': r'(\d+)\s*awards?'
            },
            'twitter': {
                'author': r'@(\w+)',
                'likes': r'(\d+)\s*(?:likes?|hearts?)',
                'retweets': r'(\d+)\s*(?:retweets?|RTs?)',
                'replies': r'(\d+)\s*(?:replies|comments)'
            },
            'hackernews': {
                'author': r'by\s+(\w+)',
                'points': r'(\d+)\s*points?',
                'comments': r'(\d+)\s*comments?'
            },
            'stackoverflow': {
                'author': r'asked by\s+(\w+)',
                'score': r'score:\s*(\d+)',
                'views': r'(\d+)\s*views?',
                'answers': r'(\d+)\s*answers?'
            }
        }
        
        # Pain point indicators for scoring
        self.pain_indicators = {
            'strong': ['hate', 'frustrated', 'annoying', 'terrible', 'nightmare', 'awful', 
                      'waste of time', 'kills me', 'drives me crazy', 'ridiculous', 'impossible'],
            'medium': ['difficult', 'struggle', 'problem', 'issue', 'challenge', 'pain',
                      'wish', 'need', 'looking for', 'anyone else', 'help'],
            'weak': ['wondering', 'curious', 'thinking about', 'considering', 'maybe']
        }
        
    async def discover_communities(self, target_market: str, market_focus: str, 
                                 problem_area: Optional[str] = None) -> Dict[str, List[str]]:
        """Use Perplexity to discover relevant communities across platforms"""
        
        communities = {
            'reddit': [],
            'discord': [],
            'slack': [],
            'forums': [],
            'facebook_groups': [],
            'linkedin_groups': []
        }
        
        try:
            from app.core.perplexity_client import perplexity_client
            
            # Query 1: Find Reddit communities
            reddit_query = f"""Find the most active Reddit subreddits where {target_market} discuss pain points and problems related to {market_focus}.
            
            Include subreddits that:
            1. Have daily/weekly complaint threads
            2. Allow rant/vent posts
            3. Focus on {problem_area if problem_area else 'professional challenges'}
            4. Have >10k members and active daily posts
            
            Also find niche subreddits specific to {target_market} subgroups.
            
            Format: List subreddit names without r/ prefix"""
            
            # Query 2: Find other communities
            other_communities_query = f"""Find active online communities beyond Reddit where {target_market} discuss problems with {market_focus}.
            
            Include:
            1. Discord servers (with invite links if public)
            2. Slack communities
            3. Specialized forums (include URLs)
            4. Facebook groups
            5. LinkedIn groups
            6. Industry-specific platforms
            
            Focus on communities known for:
            - Problem-solving discussions
            - Tool recommendations
            - Workflow complaints
            - Feature requests
            
            Provide community names and how to find them."""
            
            # Execute queries
            results = await asyncio.gather(
                perplexity_client.search(reddit_query),
                perplexity_client.search(other_communities_query),
                return_exceptions=True
            )
            
            # Parse Reddit results
            if not isinstance(results[0], Exception) and results[0].get('response'):
                reddit_subs = self._extract_subreddit_names(results[0]['response'])
                communities['reddit'].extend(reddit_subs)
            
            # Parse other community results
            if not isinstance(results[1], Exception) and results[1].get('response'):
                other_comms = self._extract_other_communities(results[1]['response'])
                for platform, comms in other_comms.items():
                    communities[platform].extend(comms)
            
        except Exception as e:
            logger.error(f"Failed to discover communities: {e}")
        
        # Add fallback communities from our knowledge base
        fallback_communities = self._get_fallback_communities(target_market, market_focus)
        for platform, comms in fallback_communities.items():
            communities[platform].extend(comms)
            
        # Deduplicate
        for platform in communities:
            communities[platform] = list(dict.fromkeys(communities[platform]))
            
        return communities
    
    async def generate_google_dorks(self, problem_statement: str, target_market: str,
                                  communities: Dict[str, List[str]], market_focus: str) -> List[str]:
        """Generate advanced Google dork queries for pain point discovery"""
        
        dorks = []
        
        # Extract key pain terms from problem statement
        pain_terms = self._extract_pain_terms(problem_statement)
        
        # Reddit-specific dorks
        for subreddit in communities.get('reddit', [])[:5]:  # Top 5 subreddits
            dorks.extend([
                f'site:reddit.com/r/{subreddit} intitle:"rant" OR intitle:"frustrated" {target_market}',
                f'site:reddit.com/r/{subreddit} "hate when" OR "drives me crazy" {pain_terms}',
                f'site:reddit.com/r/{subreddit} "looking for solution" OR "need help with" {problem_statement[:30]}',
                f'site:reddit.com/r/{subreddit} "waste of time" OR "inefficient" {pain_terms}'
            ])
        
        # General Reddit search
        dorks.extend([
            f'site:reddit.com "{problem_statement[:40]}" "anyone else" OR "am I the only one"',
            f'site:reddit.com intext:"{target_market}" intext:"problem" OR intext:"issue" {market_focus}',
            f'site:reddit.com "PSA:" OR "Warning:" {target_market} {pain_terms}'
        ])
        
        # Forum searches
        forum_domains = ['forum', 'community', 'discuss', 'talk']
        for domain in forum_domains:
            dorks.append(
                f'inurl:{domain} "{target_market}" intitle:"problem" OR intitle:"issue" {problem_statement[:30]}'
            )
        
        # Stack Overflow / technical forums
        if any(tech in target_market.lower() for tech in ['developer', 'engineer', 'tech', 'software']):
            dorks.extend([
                f'site:stackoverflow.com "{problem_statement[:40]}" is:question score:5',
                f'site:dev.to "{target_market}" "frustrating" OR "annoying" {market_focus}',
                f'site:news.ycombinator.com "{problem_statement[:30]}" complaints'
            ])
        
        # Industry-specific sites
        dorks.extend([
            f'"{target_market}" "pain points" OR "challenges" filetype:pdf',
            f'intitle:"survey results" "{target_market}" problems {pain_terms}',
            f'"case study" "{target_market}" "struggled with" OR "challenges faced"'
        ])
        
        # Time-based searches for recent pain points
        dorks.extend([
            f'"{problem_statement[:30]}" "{target_market}" after:2024',
            f'"still no solution for" "{pain_terms}" {target_market}'
        ])
        
        return dorks
    
    async def search_pain_points_advanced(self, problem_statement: str, target_market: str,
                                        market_focus: str, problem_area: Optional[str] = None,
                                        max_results: int = 10) -> List[Dict]:
        """Advanced pain point search using multiple strategies"""
        
        # Step 1: Discover communities
        communities = await self.discover_communities(target_market, market_focus, problem_area)
        
        # Step 2: Generate Google dorks
        dorks = await self.generate_google_dorks(problem_statement, target_market, communities, market_focus)
        
        # Step 3: Execute searches in parallel
        search_tasks = []
        
        # Use Perplexity with Google dorks
        for dork in dorks[:10]:  # Limit to prevent rate limiting
            query = f"Search using this exact Google query and return the actual user posts/complaints found: {dork}"
            search_tasks.append(self._search_with_dork(query, dork))
        
        # Direct community searches
        for subreddit in communities['reddit'][:5]:
            query = f"""Find the most recent posts in r/{subreddit} where users complain about {problem_statement[:60]}.
            Include:
            - The exact post title and content
            - Username, upvotes, awards, comment count
            - Most upvoted comments that agree or add to the complaint
            - Date posted
            
            Return actual posts, not summaries."""
            search_tasks.append(self._search_community(query, f'reddit.com/r/{subreddit}'))
        
        # Execute all searches
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Process results
        all_evidence = []
        for result in all_results:
            if not isinstance(result, Exception):
                all_evidence.extend(result)
        
        # Advanced scoring and filtering
        scored_evidence = self._advanced_scoring(all_evidence, problem_statement, target_market)
        
        # Cluster similar pain points
        clustered = self._cluster_pain_points(scored_evidence)
        
        # Return top results with cluster information
        return sorted(clustered, key=lambda x: x['relevance_score'], reverse=True)[:max_results]
    
    async def _search_with_dork(self, query: str, dork: str) -> List[Dict]:
        """Execute a search using a Google dork via Perplexity"""
        try:
            from app.core.perplexity_client import perplexity_client
            
            result = await perplexity_client.search(query)
            
            if result and 'response' in result:
                # Parse the response to extract actual posts
                posts = self._extract_posts_from_response(result['response'], dork)
                return posts
            
        except Exception as e:
            logger.error(f"Dork search failed for '{dork}': {e}")
            
        return []
    
    async def _search_community(self, query: str, community: str) -> List[Dict]:
        """Search a specific community for pain points"""
        try:
            from app.core.perplexity_client import perplexity_client
            
            result = await perplexity_client.search(query)
            
            if result and 'response' in result:
                posts = self._extract_posts_from_response(result['response'], community)
                return posts
                
        except Exception as e:
            logger.error(f"Community search failed for '{community}': {e}")
            
        return []
    
    def _extract_posts_from_response(self, response: str, source: str) -> List[Dict]:
        """Extract individual posts from Perplexity response"""
        posts = []
        
        # Split response into potential posts
        post_blocks = re.split(r'\n\n+|\n---+\n|\n\*\*\*+\n', response)
        
        for block in post_blocks:
            if len(block) < 50:  # Too short to be a real post
                continue
                
            post_data = self._parse_post_block(block, source)
            if post_data and self._validate_post_quality(post_data):
                posts.append(post_data)
        
        return posts
    
    def _parse_post_block(self, block: str, source: str) -> Optional[Dict]:
        """Parse a text block into structured post data"""
        
        # Determine platform
        platform = self._infer_platform_from_source(source)
        
        # Extract metadata using platform-specific patterns
        metadata = {}
        if platform in self.platform_patterns:
            for field, pattern in self.platform_patterns[platform].items():
                match = re.search(pattern, block, re.IGNORECASE)
                if match:
                    metadata[field] = match.group(1)
        
        # Extract title (usually first line or after "Title:")
        title_match = re.search(r'^(?:Title:\s*)?(.+?)(?:\n|$)', block, re.MULTILINE)
        title = title_match.group(1) if title_match else None
        
        # Extract main content
        content = self._extract_post_content(block)
        
        if not content:
            return None
            
        # Extract URL if present
        url_match = re.search(r'https?://\S+', block)
        url = url_match.group(0) if url_match else f"https://{source}"
        
        # Extract date
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|'
                              r'\d+ (?:hours?|days?|weeks?|months?) ago)', block, re.IGNORECASE)
        date_str = date_match.group(0) if date_match else None
        
        return {
            'platform': platform,
            'source_url': url,
            'title': title,
            'content': content,
            'author': metadata.get('author'),
            'upvotes': int(metadata.get('upvotes', 0)) if metadata.get('upvotes') else None,
            'engagement_score': self._calculate_engagement_score(metadata, platform),
            'date_posted': date_str,
            'metadata': metadata,
            'source_query': source
        }
    
    def _extract_post_content(self, block: str) -> Optional[str]:
        """Extract the main content from a post block"""
        
        # Remove metadata lines
        lines = block.split('\n')
        content_lines = []
        
        skip_patterns = [
            r'^(Title|Author|Posted|Upvotes|Comments|Score|Date|Link|URL|Source):',
            r'^\[.*?\]$',  # [deleted], [removed], etc.
            r'^https?://',  # URLs
            r'^\d+\s+(upvotes?|comments?|points?)',  # Engagement metrics
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip metadata lines
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
                continue
                
            content_lines.append(line)
        
        content = ' '.join(content_lines)
        
        # Clean up the content
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = content.strip()
        
        return content if len(content) > 30 else None
    
    def _validate_post_quality(self, post_data: Dict) -> bool:
        """Validate that a post contains real user content"""
        
        content = post_data.get('content', '')
        
        # Check minimum length
        if len(content) < 50:
            return False
            
        # Check for summary indicators
        summary_patterns = [
            r'users? (?:often|frequently|commonly|typically) (?:complain|mention|report)',
            r'common (?:complaints?|issues?|problems?)',
            r'based on (?:user|community) feedback',
            r'analysis (?:shows|reveals|indicates)',
            r'survey results?',
            r'aggregate[ds]? (?:from|data)',
        ]
        
        for pattern in summary_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
                
        # Check for personal indicators (good sign)
        personal_patterns = [
            r'\b(I|my|me|we|our|us)\b',
            r"(?:I'm|we're|I've|we've)",
            r'personally',
            r'in my experience',
        ]
        
        has_personal = any(re.search(pattern, content, re.IGNORECASE) for pattern in personal_patterns)
        
        # Check for pain indicators
        has_pain = any(indicator in content.lower() for category in self.pain_indicators.values() 
                      for indicator in category)
        
        return has_personal or has_pain
    
    def _advanced_scoring(self, evidence_list: List[Dict], problem_statement: str, 
                         target_market: str) -> List[Dict]:
        """Advanced relevance scoring with multiple factors"""
        
        problem_keywords = set(problem_statement.lower().split())
        target_keywords = set(target_market.lower().split())
        
        for evidence in evidence_list:
            content = (evidence.get('content') or '').lower()
            title = (evidence.get('title') or '').lower()
            full_text = f"{title} {content}"
            
            score = 0.0
            
            # 1. Keyword relevance (30%)
            problem_matches = sum(1 for kw in problem_keywords if kw in full_text)
            target_matches = sum(1 for kw in target_keywords if kw in full_text)
            
            score += (problem_matches / max(len(problem_keywords), 1)) * 0.15
            score += (target_matches / max(len(target_keywords), 1)) * 0.15
            
            # 2. Pain intensity (25%)
            pain_score = 0
            for level, indicators in self.pain_indicators.items():
                matches = sum(1 for ind in indicators if ind in content)
                if level == 'strong':
                    pain_score += matches * 3
                elif level == 'medium':
                    pain_score += matches * 2
                else:
                    pain_score += matches
            
            score += min(pain_score / 10, 0.25)
            
            # 3. Engagement score (20%)
            engagement = evidence.get('engagement_score', 0)
            score += min(engagement / 100, 0.20)
            
            # 4. Recency (15%)
            date_posted = evidence.get('date_posted')
            if date_posted:
                if 'hour' in str(date_posted) or 'day' in str(date_posted):
                    score += 0.15
                elif 'week' in str(date_posted):
                    score += 0.10
                elif 'month' in str(date_posted):
                    score += 0.05
            
            # 5. Content quality (10%)
            if len(content) > 200:
                score += 0.05
            if evidence.get('author'):
                score += 0.05
                
            evidence['relevance_score'] = min(score, 1.0)
            evidence['scoring_breakdown'] = {
                'keyword_relevance': (problem_matches + target_matches) / 
                                   max(len(problem_keywords) + len(target_keywords), 1),
                'pain_intensity': min(pain_score / 10, 1.0),
                'engagement': min(engagement / 100, 1.0),
                'recency': 0.15 if 'day' in str(date_posted) else 0.0,
                'quality': 0.1 if len(content) > 200 else 0.0
            }
        
        return evidence_list
    
    def _calculate_engagement_score(self, metadata: Dict, platform: str) -> float:
        """Calculate engagement score based on platform-specific metrics"""
        
        score = 0.0
        
        if platform == 'Reddit':
            upvotes = int(metadata.get('upvotes', 0))
            comments = int(metadata.get('comments', 0))
            awards = int(metadata.get('awards', 0))
            
            # Weighted scoring
            score = (upvotes * 0.5) + (comments * 2) + (awards * 10)
            
        elif platform == 'Twitter':
            likes = int(metadata.get('likes', 0))
            retweets = int(metadata.get('retweets', 0))
            replies = int(metadata.get('replies', 0))
            
            score = (likes * 0.3) + (retweets * 2) + (replies * 1)
            
        elif platform == 'HackerNews':
            points = int(metadata.get('points', 0))
            comments = int(metadata.get('comments', 0))
            
            score = (points * 1) + (comments * 3)
            
        elif platform == 'StackOverflow':
            score_val = int(metadata.get('score', 0))
            answers = int(metadata.get('answers', 0))
            views = int(metadata.get('views', 0))
            
            score = (score_val * 2) + (answers * 5) + (views * 0.01)
        
        return score
    
    def _cluster_pain_points(self, evidence_list: List[Dict]) -> List[Dict]:
        """Cluster similar pain points together"""
        
        # Simple clustering based on keyword overlap
        clusters = defaultdict(list)
        
        for evidence in evidence_list:
            content = (evidence.get('content') or '').lower()
            
            # Extract key pain phrases
            pain_phrases = []
            for category in self.pain_indicators.values():
                for indicator in category:
                    if indicator in content:
                        pain_phrases.append(indicator)
            
            # Create cluster key
            cluster_key = tuple(sorted(pain_phrases[:3]))  # Top 3 pain indicators
            
            if cluster_key:
                clusters[cluster_key].append(evidence)
            else:
                clusters[('uncategorized',)].append(evidence)
        
        # Add cluster information to evidence
        for cluster_key, cluster_items in clusters.items():
            cluster_size = len(cluster_items)
            cluster_name = ' + '.join(cluster_key)
            
            for item in cluster_items:
                item['cluster_info'] = {
                    'name': cluster_name,
                    'size': cluster_size,
                    'related_count': cluster_size - 1
                }
        
        return evidence_list
    
    def _extract_pain_terms(self, problem_statement: str) -> str:
        """Extract key pain-related terms from problem statement"""
        
        # Common pain-related verbs and nouns
        pain_verbs = ['struggle', 'waste', 'lose', 'miss', 'fail', 'break', 'crash']
        pain_nouns = ['problem', 'issue', 'error', 'delay', 'confusion', 'frustration']
        
        words = problem_statement.lower().split()
        pain_terms = []
        
        for word in words:
            if any(verb in word for verb in pain_verbs):
                pain_terms.append(word)
            elif any(noun in word for noun in pain_nouns):
                pain_terms.append(word)
        
        return ' '.join(pain_terms) if pain_terms else problem_statement[:30]
    
    def _infer_platform_from_source(self, source: str) -> str:
        """Infer platform from source string"""
        
        source_lower = source.lower()
        
        if 'reddit' in source_lower:
            return 'Reddit'
        elif 'twitter' in source_lower or 'x.com' in source_lower:
            return 'Twitter'
        elif 'hackernews' in source_lower or 'ycombinator' in source_lower:
            return 'HackerNews'
        elif 'stackoverflow' in source_lower:
            return 'StackOverflow'
        elif 'facebook' in source_lower:
            return 'Facebook'
        elif 'linkedin' in source_lower:
            return 'LinkedIn'
        elif 'discord' in source_lower:
            return 'Discord'
        elif 'slack' in source_lower:
            return 'Slack'
        elif 'quora' in source_lower:
            return 'Quora'
        else:
            return 'Forum'
    
    def _extract_subreddit_names(self, response: str) -> List[str]:
        """Extract subreddit names from Perplexity response"""
        
        subreddits = []
        
        # Pattern matching for subreddit names
        patterns = [
            r'r/(\w+)',
            r'/r/(\w+)',
            r'^(\w+)$',  # Just the name on its own line
            r'(?:^|\s)(\w+)(?:\s|$)',  # Word boundaries
        ]
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line or len(line) > 50:  # Skip empty or too long
                continue
                
            # Remove common prefixes
            for prefix in ['- ', '* ', '• ', '1. ', '2. ', '3. ']:
                if line.startswith(prefix):
                    line = line[len(prefix):]
            
            # Try patterns
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    sub_name = match.group(1)
                    # Validate subreddit name
                    if sub_name.replace('_', '').isalnum() and len(sub_name) > 2:
                        subreddits.append(sub_name)
                        break
        
        return subreddits
    
    def _extract_other_communities(self, response: str) -> Dict[str, List[str]]:
        """Extract non-Reddit communities from response"""
        
        communities = defaultdict(list)
        
        # Platform indicators
        platform_keywords = {
            'discord': ['discord', 'server', 'invite'],
            'slack': ['slack', 'workspace'],
            'forums': ['forum', 'community', 'board'],
            'facebook_groups': ['facebook', 'fb', 'group'],
            'linkedin_groups': ['linkedin', 'professional']
        }
        
        lines = response.split('\n')
        current_platform = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line indicates a platform section
            line_lower = line.lower()
            for platform, keywords in platform_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    current_platform = platform
                    break
            
            # Extract community name
            if current_platform:
                # Remove common formatting
                clean_line = re.sub(r'^[-*•]\s*', '', line)
                clean_line = re.sub(r'\s*\(.*?\)\s*$', '', clean_line)  # Remove parenthetical
                
                # Extract URL if present
                url_match = re.search(r'https?://\S+', clean_line)
                if url_match:
                    communities[current_platform].append(url_match.group(0))
                elif len(clean_line) > 3 and len(clean_line) < 100:
                    communities[current_platform].append(clean_line)
        
        return dict(communities)
    
    def _get_fallback_communities(self, target_market: str, market_focus: str) -> Dict[str, List[str]]:
        """Get fallback communities from knowledge base"""
        
        # This would be expanded with a comprehensive database
        fallback = {
            'reddit': [],
            'discord': [],
            'forums': []
        }
        
        # Add some common subreddits based on target market
        market_lower = target_market.lower()
        
        if 'developer' in market_lower or 'engineer' in market_lower:
            fallback['reddit'].extend(['programming', 'webdev', 'cscareerquestions'])
            fallback['discord'].append('https://discord.gg/programming')
            
        elif 'business' in market_lower or 'entrepreneur' in market_lower:
            fallback['reddit'].extend(['Entrepreneur', 'smallbusiness', 'startups'])
            
        elif 'designer' in market_lower:
            fallback['reddit'].extend(['web_design', 'graphic_design', 'userexperience'])
            
        return fallback
    
    async def find_pain_point_evidence(
        self,
        problem_statement: str,
        target_market: str,
        market_focus: str,
        problem_area: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict]:
        """Main entry point for finding pain point evidence - backwards compatible"""
        
        # Use the advanced search method
        results = await self.search_pain_points_advanced(
            problem_statement=problem_statement,
            target_market=target_market,
            market_focus=market_focus,
            problem_area=problem_area,
            max_results=max_results
        )
        
        # Convert to the expected format
        formatted_results = []
        for result in results:
            # Map the fields to match the expected format
            formatted_result = {
                'platform': result.get('platform', 'Unknown'),
                'source_url': result.get('source_url', ''),
                'title': result.get('title'),
                'snippet': result.get('content', '')[:1000],  # Limit to 1000 chars
                'author': result.get('author'),
                'upvotes': result.get('upvotes'),
                'date_posted': result.get('date_posted'),
                'relevance_score': result.get('relevance_score', 0.5),
                'subreddit': result.get('metadata', {}).get('subreddit'),
                'comment_count': result.get('metadata', {}).get('comments')
            }
            formatted_results.append(formatted_result)
        
        return formatted_results