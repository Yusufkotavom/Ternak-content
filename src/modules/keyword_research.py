"""
Keyword Research Module
Riset keyword menggunakan Google Suggest dan SERP analysis
Windows compatible without Selenium
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional
import json
import re
from urllib.parse import quote_plus
import random
import time

from src.utils.config import Settings

class KeywordResearch:
    def __init__(self):
        self.settings = Settings()
        
        # User agents untuk rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Free keyword research APIs
        self.free_apis = {
            'google_suggest': 'https://suggestqueries.google.com/complete/search',
            'bing_suggest': 'https://api.bing.com/qson',
            'youtube_suggest': 'https://suggestqueries.google.com/complete/search'
        }
    
    async def research_keyword(self, keyword: str) -> Dict:
        """Riset keyword dan dapatkan data lengkap"""
        
        try:
            # 1. Get related keywords
            related_keywords = await self._get_related_keywords(keyword)
            
            # 2. Get common questions
            questions = await self._get_common_questions(keyword)
            
            # 3. Get top SERP results
            top_results = await self._get_top_serp_results(keyword)
            
            # 4. Analyze competition
            competition = await self._analyze_competition(keyword, top_results)
            
            # 5. Get search volume estimate
            search_volume = await self._estimate_search_volume(keyword)
            
            return {
                'keyword': keyword,
                'related_keywords': related_keywords,
                'questions': questions,
                'top_results': top_results,
                'competition': competition,
                'search_volume': search_volume,
                'research_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error researching keyword '{keyword}': {str(e)}")
            return self._create_fallback_research(keyword)
    
    async def _get_related_keywords(self, keyword: str) -> List[str]:
        """Get related keywords dari Google Suggest"""
        related_keywords = []
        
        try:
            # Try Google Suggest
            google_keywords = await self._get_google_suggestions(keyword)
            related_keywords.extend(google_keywords)
            
            # Try Bing Suggestions
            bing_keywords = await self._get_bing_suggestions(keyword)
            related_keywords.extend(bing_keywords)
            
            # Add keyword variations
            variations = self._generate_keyword_variations(keyword)
            related_keywords.extend(variations)
            
            # Remove duplicates and limit
            unique_keywords = list(set(related_keywords))
            return unique_keywords[:20]  # Limit to 20 keywords
            
        except Exception as e:
            print(f"Error getting related keywords: {str(e)}")
            return self._generate_keyword_variations(keyword)
    
    async def _get_google_suggestions(self, keyword: str) -> List[str]:
        """Get suggestions dari Google Suggest API"""
        suggestions = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'client': 'firefox',
                    'q': keyword,
                    'hl': 'id'
                }
                
                headers = {
                    'User-Agent': random.choice(self.user_agents)
                }
                
                async with session.get(
                    self.free_apis['google_suggest'],
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if len(data) > 1:
                            suggestions = data[1][:10]  # Get first 10 suggestions
                        
        except Exception as e:
            print(f"Error getting Google suggestions: {str(e)}")
        
        return suggestions
    
    async def _get_bing_suggestions(self, keyword: str) -> List[str]:
        """Get suggestions dari Bing API"""
        suggestions = []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'type': 'cb',
                    'q': keyword,
                    'mkt': 'id-ID'
                }
                
                headers = {
                    'User-Agent': random.choice(self.user_agents)
                }
                
                async with session.get(
                    self.free_apis['bing_suggest'],
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'AS' in data and 'Results' in data['AS']:
                            for result in data['AS']['Results']:
                                if 'Suggests' in result:
                                    for suggest in result['Suggests']:
                                        if 'Txt' in suggest:
                                            suggestions.append(suggest['Txt'])
                        
        except Exception as e:
            print(f"Error getting Bing suggestions: {str(e)}")
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate keyword variations manually"""
        variations = []
        
        # Add common prefixes/suffixes
        prefixes = ['cara', 'tips', 'panduan', 'tutorial', 'belajar', 'mengenal']
        suffixes = ['untuk pemula', 'lengkap', 'terbaik', '2024', 'indonesia']
        
        for prefix in prefixes:
            variations.append(f"{prefix} {keyword}")
        
        for suffix in suffixes:
            variations.append(f"{keyword} {suffix}")
        
        # Add question variations
        question_words = ['apa', 'bagaimana', 'kapan', 'di mana', 'mengapa']
        for word in question_words:
            variations.append(f"{word} {keyword}")
        
        return variations
    
    async def _get_common_questions(self, keyword: str) -> List[str]:
        """Get common questions tentang keyword"""
        questions = []
        
        try:
            # Generate common question patterns
            question_patterns = [
                f"Apa itu {keyword}?",
                f"Bagaimana cara {keyword}?",
                f"Tips {keyword} untuk pemula",
                f"Berapa biaya {keyword}?",
                f"Di mana bisa {keyword}?",
                f"Kapan waktu terbaik untuk {keyword}?",
                f"Mengapa perlu {keyword}?",
                f"Apa manfaat {keyword}?",
                f"Berapa lama waktu {keyword}?",
                f"Apa yang diperlukan untuk {keyword}?"
            ]
            
            questions.extend(question_patterns)
            
            # Try to get real questions from search
            real_questions = await self._get_real_questions(keyword)
            questions.extend(real_questions)
            
            return questions[:15]  # Limit to 15 questions
            
        except Exception as e:
            print(f"Error getting questions: {str(e)}")
            return question_patterns[:10]
    
    async def _get_real_questions(self, keyword: str) -> List[str]:
        """Get real questions dari search results"""
        questions = []
        
        try:
            # Search for questions containing the keyword
            search_terms = [
                f'"{keyword}" "apa"',
                f'"{keyword}" "bagaimana"',
                f'"{keyword}" "tips"',
                f'"{keyword}" "panduan"'
            ]
            
            for search_term in search_terms:
                try:
                    # Simple web scraping (without Selenium)
                    results = await self._simple_web_search(search_term)
                    
                    # Extract questions from results
                    for result in results:
                        question = self._extract_question_from_text(result.get('title', ''))
                        if question:
                            questions.append(question)
                    
                    # Add delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error getting real questions: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in real questions search: {str(e)}")
        
        return questions[:5]  # Limit to 5 real questions
    
    async def _simple_web_search(self, query: str) -> List[Dict]:
        """Simple web search without Selenium"""
        results = []
        
        try:
            # Use a simple search API or fallback
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': random.choice(self.user_agents)
                }
                
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Simple HTML parsing
                        results = self._parse_search_results(html)
                        
        except Exception as e:
            print(f"Error in simple web search: {str(e)}")
        
        return results
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results from HTML"""
        results = []
        
        try:
            # Simple regex parsing
            title_pattern = r'<h3[^>]*>(.*?)</h3>'
            link_pattern = r'href="([^"]*)"'
            
            titles = re.findall(title_pattern, html)
            links = re.findall(link_pattern, html)
            
            for i, title in enumerate(titles[:5]):  # Get first 5 results
                if i < len(links):
                    results.append({
                        'title': title.strip(),
                        'url': links[i]
                    })
                    
        except Exception as e:
            print(f"Error parsing search results: {str(e)}")
        
        return results
    
    def _extract_question_from_text(self, text: str) -> Optional[str]:
        """Extract question from text"""
        question_words = ['apa', 'bagaimana', 'kapan', 'di mana', 'mengapa', 'berapa']
        
        for word in question_words:
            if word in text.lower():
                # Clean the text
                cleaned = re.sub(r'<[^>]+>', '', text)
                cleaned = cleaned.strip()
                if len(cleaned) > 10:  # Minimum length
                    return cleaned
        
        return None
    
    async def _get_top_serp_results(self, keyword: str) -> List[Dict]:
        """Get top SERP results"""
        results = []
        
        try:
            # Simple search without Selenium
            search_results = await self._simple_web_search(keyword)
            
            for result in search_results[:5]:  # Top 5 results
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'domain': self._extract_domain(result.get('url', ''))
                })
                
        except Exception as e:
            print(f"Error getting SERP results: {str(e)}")
            # Return fallback results
            results = [
                {'title': f'Hasil pencarian untuk {keyword}', 'url': '#', 'domain': 'example.com'},
                {'title': f'Informasi tentang {keyword}', 'url': '#', 'domain': 'example.com'},
                {'title': f'Panduan {keyword}', 'url': '#', 'domain': 'example.com'}
            ]
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return 'unknown'
    
    async def _analyze_competition(self, keyword: str, top_results: List[Dict]) -> Dict:
        """Analyze competition level"""
        try:
            # Simple competition analysis
            domains = [result.get('domain', '') for result in top_results]
            unique_domains = len(set(domains))
            
            # Determine competition level
            if unique_domains >= 4:
                competition_level = "Tinggi"
                difficulty = "Sulit"
            elif unique_domains >= 2:
                competition_level = "Sedang"
                difficulty = "Menengah"
            else:
                competition_level = "Rendah"
                difficulty = "Mudah"
            
            return {
                'level': competition_level,
                'difficulty': difficulty,
                'unique_domains': unique_domains,
                'total_results': len(top_results)
            }
            
        except Exception as e:
            print(f"Error analyzing competition: {str(e)}")
            return {
                'level': 'Sedang',
                'difficulty': 'Menengah',
                'unique_domains': 3,
                'total_results': 5
            }
    
    async def _estimate_search_volume(self, keyword: str) -> str:
        """Estimate search volume"""
        try:
            # Simple estimation based on keyword length and complexity
            word_count = len(keyword.split())
            
            if word_count == 1:
                volume = "Tinggi (10K+ per bulan)"
            elif word_count == 2:
                volume = "Sedang (1K-10K per bulan)"
            else:
                volume = "Rendah (<1K per bulan)"
            
            return volume
            
        except Exception as e:
            print(f"Error estimating search volume: {str(e)}")
            return "Sedang (1K-10K per bulan)"
    
    def _create_fallback_research(self, keyword: str) -> Dict:
        """Create fallback research data"""
        return {
            'keyword': keyword,
            'related_keywords': self._generate_keyword_variations(keyword)[:10],
            'questions': [
                f"Apa itu {keyword}?",
                f"Bagaimana cara {keyword}?",
                f"Tips {keyword} untuk pemula",
                f"Berapa biaya {keyword}?",
                f"Di mana bisa {keyword}?"
            ],
            'top_results': [
                {'title': f'Hasil pencarian untuk {keyword}', 'url': '#', 'domain': 'example.com'},
                {'title': f'Informasi tentang {keyword}', 'url': '#', 'domain': 'example.com'},
                {'title': f'Panduan {keyword}', 'url': '#', 'domain': 'example.com'}
            ],
            'competition': {
                'level': 'Sedang',
                'difficulty': 'Menengah',
                'unique_domains': 3,
                'total_results': 5
            },
            'search_volume': 'Sedang (1K-10K per bulan)',
            'research_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }