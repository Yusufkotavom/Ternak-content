"""
Keyword Research Module
Melakukan riset keyword menggunakan SERP scraping dan API
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.config import Settings

class KeywordResearch:
    def __init__(self):
        self.settings = Settings()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })
    
    async def research_keyword(self, keyword: str) -> Dict:
        """
        Melakukan riset keyword lengkap
        """
        research_data = {
            'keyword': keyword,
            'search_volume': None,
            'competition': None,
            'related_keywords': [],
            'questions': [],
            'top_results': [],
            'suggestions': []
        }
        
        try:
            # 1. Get related keywords
            research_data['related_keywords'] = await self._get_related_keywords(keyword)
            
            # 2. Get questions
            research_data['questions'] = await self._get_questions(keyword)
            
            # 3. Get top search results
            research_data['top_results'] = await self._get_top_results(keyword)
            
            # 4. Get keyword suggestions
            research_data['suggestions'] = await self._get_keyword_suggestions(keyword)
            
            # 5. Analyze competition (basic)
            research_data['competition'] = await self._analyze_competition(keyword)
            
        except Exception as e:
            print(f"Error in keyword research for '{keyword}': {str(e)}")
        
        return research_data
    
    async def _get_related_keywords(self, keyword: str) -> List[str]:
        """Get related keywords dari Google Suggest"""
        related_keywords = []
        
        try:
            # Google Suggest API
            suggest_url = f"http://suggestqueries.google.com/complete/search"
            params = {
                'client': 'firefox',
                'q': keyword
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(suggest_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if len(data) > 1:
                            related_keywords = data[1][:10]  # Ambil 10 suggestions
        except Exception as e:
            print(f"Error getting related keywords: {str(e)}")
        
        return related_keywords
    
    async def _get_questions(self, keyword: str) -> List[str]:
        """Get pertanyaan terkait keyword"""
        questions = []
        
        try:
            # Cari "how to", "what is", "why", etc.
            question_prefixes = [
                f"how to {keyword}",
                f"what is {keyword}",
                f"why {keyword}",
                f"when {keyword}",
                f"where {keyword}",
                f"tips {keyword}",
                f"cara {keyword}",
                f"apa itu {keyword}",
                f"mengapa {keyword}"
            ]
            
            for question in question_prefixes:
                questions.append(question)
                
        except Exception as e:
            print(f"Error getting questions: {str(e)}")
        
        return questions[:5]  # Limit to 5 questions
    
    async def _get_top_results(self, keyword: str) -> List[Dict]:
        """Get top 5 search results dari Google"""
        results = []
        
        try:
            # Gunakan Selenium untuk scraping Google
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
                driver.get(search_url)
                
                # Wait for results
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
                )
                
                # Get top 5 results
                result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")[:5]
                
                for element in result_elements:
                    try:
                        title_element = element.find_element(By.CSS_SELECTOR, "h3")
                        link_element = element.find_element(By.CSS_SELECTOR, "a")
                        snippet_element = element.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                        
                        results.append({
                            'title': title_element.text,
                            'url': link_element.get_attribute('href'),
                            'snippet': snippet_element.text
                        })
                    except:
                        continue
                        
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"Error getting top results: {str(e)}")
        
        return results
    
    async def _get_keyword_suggestions(self, keyword: str) -> List[str]:
        """Get keyword suggestions dari berbagai sumber"""
        suggestions = []
        
        try:
            # Tambahkan keyword dengan modifier
            modifiers = [
                "tips", "cara", "panduan", "tutorial", "review", 
                "harga", "terbaik", "terbaru", "lengkap", "gratis"
            ]
            
            for modifier in modifiers:
                suggestions.append(f"{modifier} {keyword}")
                suggestions.append(f"{keyword} {modifier}")
        
        except Exception as e:
            print(f"Error getting keyword suggestions: {str(e)}")
        
        return suggestions[:10]
    
    async def _analyze_competition(self, keyword: str) -> str:
        """Analisis kompetisi sederhana"""
        try:
            # Hitung jumlah hasil pencarian
            search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers={'User-Agent': self.ua.random}) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Cari statistik hasil pencarian
                        stats_element = soup.find('div', {'id': 'result-stats'})
                        if stats_element:
                            stats_text = stats_element.text
                            # Extract number from "About X results"
                            import re
                            numbers = re.findall(r'[\d,]+', stats_text)
                            if numbers:
                                result_count = int(numbers[0].replace(',', ''))
                                
                                if result_count < 100000:
                                    return "Low"
                                elif result_count < 1000000:
                                    return "Medium"
                                else:
                                    return "High"
        
        except Exception as e:
            print(f"Error analyzing competition: {str(e)}")
        
        return "Unknown"
    
    def get_bulk_keywords_from_csv(self, file_path: str) -> List[str]:
        """Baca keywords dari file CSV"""
        import pandas as pd
        
        try:
            df = pd.read_csv(file_path)
            if 'keyword' in df.columns:
                return df['keyword'].tolist()
            else:
                return df.iloc[:, 0].tolist()
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return []
    
    def get_bulk_keywords_from_text(self, text: str) -> List[str]:
        """Parse keywords dari text input"""
        keywords = []
        
        for line in text.strip().split('\n'):
            keyword = line.strip()
            if keyword:
                keywords.append(keyword)
        
        return keywords