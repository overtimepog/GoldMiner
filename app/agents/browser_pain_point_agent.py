"""Browser-based agent for active pain point discovery using Playwright"""
import logging
import asyncio
import re
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Page, Browser
import random
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class BrowserPainPointAgent:
    """Agent that actively browses communities to discover pain points"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context = None
        self.stealth_enabled = True
        
        # User agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'
        ]
        
        # Platform-specific selectors
        self.platform_selectors = {
            'reddit': {
                'post_container': 'div[data-testid="post-container"], article',
                'title': 'h3, h1',
                'content': 'div[data-click-id="text"]',
                'author': 'a[href*="/user/"]',
                'upvotes': 'span[style*="color: var(--newCommunityTheme-voteText)"]',
                'comments': 'a[href*="/comments/"] span',
                'awards': 'div[id*="PostAwardBadges"]',
                'load_more': 'button:has-text("Load more"), button:has-text("View more")',
                'sort_options': 'button[id*="sort"], select[name="sort"]'
            },
            'hackernews': {
                'post_container': 'tr.athing',
                'title': 'span.titleline > a',
                'content': '.comment',
                'author': 'a.hnuser',
                'points': 'span.score',
                'comments': 'a:has-text("comments")',
                'load_more': 'a.morelink'
            },
            'stackoverflow': {
                'post_container': 'div.question-summary',
                'title': 'h3 > a',
                'content': 'div.excerpt',
                'author': 'div.user-info a',
                'score': 'span.vote-count-post',
                'answers': 'div.status strong',
                'views': 'div.views'
            },
            'discourse': {  # Many forums use Discourse
                'post_container': 'tr.topic-list-item',
                'title': 'a.title',
                'content': 'div.cooked',
                'author': 'a.username',
                'replies': 'span.posts-map',
                'views': 'span.views',
                'load_more': 'button.load-more'
            }
        }
        
        # Pain point detection patterns
        self.pain_patterns = {
            'strong_pain': [
                r'hate\s+(?:when|that|how)',
                r'drives?\s+me\s+(?:crazy|nuts|insane)',
                r'waste\s+of\s+(?:time|money)',
                r'(?:really|so)\s+frustrat(?:ing|ed)',
                r'(?:absolutely|completely)\s+(?:terrible|awful)',
                r'nightmare\s+to\s+(?:deal|work)\s+with',
                r'(?:never|doesn\'t)\s+work(?:s|ing)?',
                r'(?:lost|losing)\s+(?:hours|days|customers|money)',
                r'(?:sick|tired)\s+of\s+(?:dealing|having)',
                r'why\s+is\s+(?:it|this)\s+so\s+(?:hard|difficult|complicated)'
            ],
            'medium_pain': [
                r'struggle\s+(?:with|to)',
                r'pain\s+(?:point|in\s+the)',
                r'wish\s+(?:there|I\s+could)',
                r'anyone\s+(?:else|know)',
                r'looking\s+for\s+(?:a\s+)?(?:solution|alternative)',
                r'(?:need|want)\s+(?:help|advice)',
                r'(?:annoying|annoyed)\s+(?:that|when)',
                r'(?:difficult|hard)\s+to',
                r'problem\s+(?:is|with)',
                r'issue\s+(?:is|with)'
            ],
            'feature_request': [
                r'would\s+be\s+(?:great|nice|cool)\s+if',
                r'(?:should|could)\s+(?:add|have|implement)',
                r'feature\s+request',
                r'(?:need|want)\s+(?:a\s+)?way\s+to',
                r'(?:missing|lacks?)\s+(?:a\s+)?(?:feature|functionality)',
                r'why\s+(?:can\'t|doesn\'t)\s+(?:it|this)',
                r'(?:please|desperately)\s+(?:add|need)',
                r'game\s+changer\s+(?:if|would\s+be)'
            ]
        }
    
    async def initialize(self):
        """Initialize the browser with stealth settings"""
        playwright = await async_playwright().start()
        
        # Launch with stealth settings
        self.browser = await playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--enable-features=NetworkService,NetworkServiceInProcess'
            ]
        )
        
        # Create context with random user agent
        self.context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # NYC
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            // Override the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Chrome specific
            window.chrome = {
                runtime: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    async def close(self):
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def scrape_reddit_pain_points(self, subreddit: str, pain_keywords: List[str], 
                                      max_posts: int = 20) -> List[Dict]:
        """Scrape pain points from a specific subreddit"""
        
        url = f"https://www.reddit.com/r/{subreddit}/top/?t=week"
        page = await self.context.new_page()
        
        try:
            # Random delay before navigation
            await asyncio.sleep(random.uniform(2, 5))
            
            # Navigate to subreddit
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for posts to load
            await page.wait_for_selector(self.platform_selectors['reddit']['post_container'], 
                                       timeout=10000)
            
            # Random scrolling to appear human-like
            await self._human_like_scroll(page)
            
            # Extract posts
            posts = await self._extract_reddit_posts(page, pain_keywords, max_posts)
            
            # Visit top pain point posts for more details
            detailed_posts = []
            for post in posts[:5]:  # Limit to top 5 to avoid rate limiting
                if post.get('url'):
                    detailed = await self._get_reddit_post_details(page, post['url'])
                    if detailed:
                        post.update(detailed)
                detailed_posts.append(post)
                
                # Random delay between posts
                await asyncio.sleep(random.uniform(3, 7))
            
            return detailed_posts
            
        except Exception as e:
            logger.error(f"Error scraping subreddit {subreddit}: {e}")
            return []
        finally:
            await page.close()
    
    async def scrape_forum_pain_points(self, forum_url: str, search_terms: List[str],
                                     max_threads: int = 20) -> List[Dict]:
        """Scrape pain points from generic forums"""
        
        page = await self.context.new_page()
        
        try:
            # Navigate to forum
            await page.goto(forum_url, wait_until='domcontentloaded', timeout=30000)
            
            # Detect forum type
            forum_type = await self._detect_forum_type(page)
            
            # Search for pain points
            if forum_type == 'discourse':
                return await self._scrape_discourse_forum(page, search_terms, max_threads)
            elif forum_type == 'phpbb':
                return await self._scrape_phpbb_forum(page, search_terms, max_threads)
            elif forum_type == 'xenforo':
                return await self._scrape_xenforo_forum(page, search_terms, max_threads)
            else:
                # Generic forum scraping
                return await self._scrape_generic_forum(page, search_terms, max_threads)
                
        except Exception as e:
            logger.error(f"Error scraping forum {forum_url}: {e}")
            return []
        finally:
            await page.close()
    
    async def search_google_dorks(self, dork_queries: List[str], max_results: int = 10) -> List[Dict]:
        """Execute Google dork searches and extract pain points"""
        
        page = await self.context.new_page()
        all_results = []
        
        try:
            for dork in dork_queries[:5]:  # Limit to prevent detection
                # Random delay
                await asyncio.sleep(random.uniform(5, 10))
                
                # Search Google
                search_url = f"https://www.google.com/search?q={dork}"
                await page.goto(search_url, wait_until='domcontentloaded')
                
                # Extract search results
                results = await self._extract_google_results(page)
                
                # Visit promising results
                for result in results[:3]:
                    if result.get('url'):
                        pain_points = await self._extract_pain_points_from_url(
                            page, result['url']
                        )
                        all_results.extend(pain_points)
                        
                        if len(all_results) >= max_results:
                            break
                
                if len(all_results) >= max_results:
                    break
                    
        except Exception as e:
            logger.error(f"Error with Google dork search: {e}")
        finally:
            await page.close()
            
        return all_results[:max_results]
    
    async def _extract_reddit_posts(self, page: Page, pain_keywords: List[str], 
                                  max_posts: int) -> List[Dict]:
        """Extract posts from Reddit page"""
        
        posts = []
        selectors = self.platform_selectors['reddit']
        
        # Get all post containers
        post_elements = await page.query_selector_all(selectors['post_container'])
        
        for element in post_elements[:max_posts * 2]:  # Check more posts than needed
            try:
                # Extract basic info
                title_el = await element.query_selector(selectors['title'])
                title = await title_el.inner_text() if title_el else ''
                
                content_el = await element.query_selector(selectors['content'])
                content = await content_el.inner_text() if content_el else ''
                
                # Check if post contains pain indicators
                full_text = f"{title} {content}".lower()
                if not self._contains_pain_indicators(full_text, pain_keywords):
                    continue
                
                # Extract metadata
                author_el = await element.query_selector(selectors['author'])
                author = await author_el.inner_text() if author_el else None
                
                upvotes_el = await element.query_selector(selectors['upvotes'])
                upvotes_text = await upvotes_el.inner_text() if upvotes_el else '0'
                upvotes = self._parse_vote_count(upvotes_text)
                
                # Get post URL
                link_el = await element.query_selector('a[href*="/comments/"]')
                post_url = await link_el.get_attribute('href') if link_el else None
                if post_url and not post_url.startswith('http'):
                    post_url = f"https://www.reddit.com{post_url}"
                
                # Calculate pain score
                pain_score = self._calculate_pain_score(full_text)
                
                posts.append({
                    'platform': 'Reddit',
                    'title': title,
                    'content': content,
                    'author': author,
                    'upvotes': upvotes,
                    'url': post_url,
                    'pain_score': pain_score,
                    'extracted_at': datetime.now().isoformat()
                })
                
                if len(posts) >= max_posts:
                    break
                    
            except Exception as e:
                logger.warning(f"Error extracting Reddit post: {e}")
                continue
        
        return sorted(posts, key=lambda x: x['pain_score'], reverse=True)
    
    async def _get_reddit_post_details(self, page: Page, post_url: str) -> Optional[Dict]:
        """Get detailed information from a Reddit post"""
        
        try:
            # Create new page for post
            post_page = await self.context.new_page()
            await post_page.goto(post_url, wait_until='domcontentloaded')
            
            # Wait for comments to load
            await post_page.wait_for_selector('.Comment', timeout=5000)
            
            # Extract top comments that indicate pain
            comments = []
            comment_elements = await post_page.query_selector_all('.Comment')
            
            for comment_el in comment_elements[:10]:
                try:
                    comment_text_el = await comment_el.query_selector('div[data-testid="comment"]')
                    if comment_text_el:
                        comment_text = await comment_text_el.inner_text()
                        
                        # Check if comment expresses pain
                        if self._contains_pain_indicators(comment_text.lower(), []):
                            comment_score_el = await comment_el.query_selector('span[style*="color"]')
                            comment_score = self._parse_vote_count(
                                await comment_score_el.inner_text() if comment_score_el else '0'
                            )
                            
                            comments.append({
                                'text': comment_text[:500],
                                'score': comment_score,
                                'pain_score': self._calculate_pain_score(comment_text)
                            })
                            
                except Exception as e:
                    continue
            
            await post_page.close()
            
            # Sort comments by pain score
            comments.sort(key=lambda x: x['pain_score'], reverse=True)
            
            return {
                'top_pain_comments': comments[:5],
                'comment_pain_indicators': self._extract_pain_indicators(
                    ' '.join(c['text'] for c in comments)
                )
            }
            
        except Exception as e:
            logger.warning(f"Error getting Reddit post details: {e}")
            return None
    
    async def _scrape_discourse_forum(self, page: Page, search_terms: List[str], 
                                    max_threads: int) -> List[Dict]:
        """Scrape Discourse-based forums"""
        
        results = []
        
        try:
            # Search for each term
            for term in search_terms:
                # Use Discourse search
                search_url = f"{page.url}/search?q={term}"
                await page.goto(search_url, wait_until='domcontentloaded')
                
                # Wait for results
                await page.wait_for_selector('.search-results', timeout=5000)
                
                # Extract results
                result_elements = await page.query_selector_all('.search-result')
                
                for element in result_elements[:max_threads // len(search_terms)]:
                    try:
                        title_el = await element.query_selector('.topic-title')
                        title = await title_el.inner_text() if title_el else ''
                        
                        excerpt_el = await element.query_selector('.blurb')
                        excerpt = await excerpt_el.inner_text() if excerpt_el else ''
                        
                        # Check for pain indicators
                        if not self._contains_pain_indicators(f"{title} {excerpt}".lower(), []):
                            continue
                        
                        link_el = await element.query_selector('a.search-link')
                        thread_url = await link_el.get_attribute('href') if link_el else None
                        
                        if thread_url:
                            if not thread_url.startswith('http'):
                                thread_url = urljoin(page.url, thread_url)
                            
                            results.append({
                                'platform': 'Discourse Forum',
                                'title': title,
                                'content': excerpt,
                                'url': thread_url,
                                'pain_score': self._calculate_pain_score(f"{title} {excerpt}"),
                                'forum_type': 'discourse'
                            })
                            
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping Discourse forum: {e}")
            
        return results
    
    async def _extract_pain_points_from_url(self, page: Page, url: str) -> List[Dict]:
        """Extract pain points from any URL"""
        
        try:
            # Navigate to URL
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            
            # Get page content
            content = await page.content()
            text_content = await page.evaluate('() => document.body.innerText')
            
            # Extract pain points from text
            pain_points = []
            
            # Split into paragraphs
            paragraphs = text_content.split('\n\n')
            
            for para in paragraphs:
                if len(para) < 50:  # Skip short paragraphs
                    continue
                    
                # Check for pain indicators
                pain_score = self._calculate_pain_score(para)
                
                if pain_score > 0.3:  # Threshold for pain content
                    # Extract context
                    pain_indicators = self._extract_pain_indicators(para)
                    
                    pain_points.append({
                        'platform': self._get_platform_from_url(url),
                        'content': para[:1000],
                        'url': url,
                        'pain_score': pain_score,
                        'pain_indicators': pain_indicators,
                        'extracted_at': datetime.now().isoformat()
                    })
            
            return sorted(pain_points, key=lambda x: x['pain_score'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error extracting from URL {url}: {e}")
            return []
    
    def _contains_pain_indicators(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains pain indicators"""
        
        # Check keywords first
        if keywords:
            if not any(keyword.lower() in text for keyword in keywords):
                return False
        
        # Check pain patterns
        for category in self.pain_patterns.values():
            for pattern in category:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
                    
        return False
    
    def _calculate_pain_score(self, text: str) -> float:
        """Calculate pain intensity score"""
        
        score = 0.0
        text_lower = text.lower()
        
        # Check pain patterns
        for pattern in self.pain_patterns['strong_pain']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            score += matches * 0.3
            
        for pattern in self.pain_patterns['medium_pain']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            score += matches * 0.2
            
        for pattern in self.pain_patterns['feature_request']:
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            score += matches * 0.1
        
        # Normalize score
        return min(score / max(len(text.split()), 1) * 100, 1.0)
    
    def _extract_pain_indicators(self, text: str) -> List[str]:
        """Extract specific pain indicators from text"""
        
        indicators = []
        text_lower = text.lower()
        
        for category, patterns in self.pain_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                indicators.extend(matches)
        
        return list(set(indicators))[:10]  # Return top 10 unique indicators
    
    async def _human_like_scroll(self, page: Page):
        """Perform human-like scrolling"""
        
        # Random scroll pattern
        scroll_attempts = random.randint(3, 7)
        
        for _ in range(scroll_attempts):
            # Scroll distance
            distance = random.randint(300, 800)
            
            # Smooth scroll
            await page.evaluate(f"""
                window.scrollBy({{
                    top: {distance},
                    behavior: 'smooth'
                }});
            """)
            
            # Random pause
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Sometimes scroll up a bit
            if random.random() < 0.3:
                await page.evaluate(f"""
                    window.scrollBy({{
                        top: -{random.randint(100, 300)},
                        behavior: 'smooth'
                    }});
                """)
                await asyncio.sleep(random.uniform(0.3, 1.0))
    
    async def _detect_forum_type(self, page: Page) -> str:
        """Detect the type of forum software"""
        
        # Check for common forum indicators
        content = await page.content()
        
        if 'discourse' in content.lower() or await page.query_selector('.discourse-tags'):
            return 'discourse'
        elif 'phpbb' in content.lower() or await page.query_selector('#phpbb'):
            return 'phpbb'
        elif 'xenforo' in content.lower() or await page.query_selector('.xenforo'):
            return 'xenforo'
        elif 'vbulletin' in content.lower():
            return 'vbulletin'
        else:
            return 'generic'
    
    def _parse_vote_count(self, text: str) -> int:
        """Parse vote count from various formats"""
        
        # Remove non-numeric characters except k/m
        clean = re.sub(r'[^\d.km]', '', text.lower())
        
        if not clean:
            return 0
            
        try:
            if 'k' in clean:
                return int(float(clean.replace('k', '')) * 1000)
            elif 'm' in clean:
                return int(float(clean.replace('m', '')) * 1000000)
            else:
                return int(float(clean))
        except:
            return 0
    
    def _get_platform_from_url(self, url: str) -> str:
        """Determine platform from URL"""
        
        domain = urlparse(url).netloc.lower()
        
        if 'reddit.com' in domain:
            return 'Reddit'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'Twitter'
        elif 'stackoverflow.com' in domain:
            return 'StackOverflow'
        elif 'news.ycombinator.com' in domain:
            return 'HackerNews'
        elif 'facebook.com' in domain:
            return 'Facebook'
        elif 'linkedin.com' in domain:
            return 'LinkedIn'
        elif 'quora.com' in domain:
            return 'Quora'
        elif 'github.com' in domain:
            return 'GitHub'
        else:
            return 'Web'
    
    async def _extract_google_results(self, page: Page) -> List[Dict]:
        """Extract search results from Google"""
        
        results = []
        
        try:
            # Wait for results
            await page.wait_for_selector('div#search', timeout=5000)
            
            # Get result containers
            result_elements = await page.query_selector_all('div.g')
            
            for element in result_elements[:10]:
                try:
                    # Extract title and URL
                    title_el = await element.query_selector('h3')
                    title = await title_el.inner_text() if title_el else ''
                    
                    link_el = await element.query_selector('a')
                    url = await link_el.get_attribute('href') if link_el else None
                    
                    # Extract snippet
                    snippet_el = await element.query_selector('span.aCOpRe, div.VwiC3b')
                    snippet = await snippet_el.inner_text() if snippet_el else ''
                    
                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting Google results: {e}")
            
        return results
    
    async def _scrape_phpbb_forum(self, page: Page, search_terms: List[str], 
                                 max_threads: int) -> List[Dict]:
        """Scrape phpBB forums"""
        # Implementation would follow similar pattern to Discourse
        return []
    
    async def _scrape_xenforo_forum(self, page: Page, search_terms: List[str],
                                   max_threads: int) -> List[Dict]:
        """Scrape XenForo forums"""
        # Implementation would follow similar pattern to Discourse
        return []
    
    async def _scrape_generic_forum(self, page: Page, search_terms: List[str],
                                   max_threads: int) -> List[Dict]:
        """Generic forum scraping fallback"""
        
        results = []
        
        try:
            # Look for common forum patterns
            thread_selectors = [
                'a[href*="thread"]',
                'a[href*="topic"]',
                'a[href*="/t/"]',
                '.topic-title',
                '.thread-title'
            ]
            
            for selector in thread_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements[:max_threads]:
                        try:
                            title = await element.inner_text()
                            url = await element.get_attribute('href')
                            
                            if url and title:
                                if not url.startswith('http'):
                                    url = urljoin(page.url, url)
                                    
                                # Check for pain indicators in title
                                if self._contains_pain_indicators(title.lower(), search_terms):
                                    results.append({
                                        'platform': 'Forum',
                                        'title': title,
                                        'url': url,
                                        'pain_score': self._calculate_pain_score(title),
                                        'forum_type': 'generic'
                                    })
                                    
                        except Exception as e:
                            continue
                            
                    break
                    
        except Exception as e:
            logger.error(f"Error in generic forum scraping: {e}")
            
        return results