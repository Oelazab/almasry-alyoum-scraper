import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import json
from typing import List, Dict, Optional

class AlmasryalyoumScraper:
    """
    A library for scraping news articles from Almasryalyoum website.
    
    Features:
    - Cloudflare bypass using cloudscraper
    - Randomized delays to avoid detection
    - Retry mechanism for failed requests
    - Realistic browser headers
    """
    
    def __init__(self, max_retries: int = 3, delay_range: tuple = (5, 15)):
        """
        Initialize the scraper.
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests
            delay_range: Tuple of (min, max) delay between requests in seconds
        """
        self.BASE_URL = "https://www.almasryalyoum.com"
        self.max_retries = max_retries
        self.delay_range = delay_range
        
    def _setup_scraper(self):
        """Configure the cloudscraper with realistic browser headers"""
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=random.randint(*self.delay_range)
        )
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }
        
        scraper.headers.update(headers)
        return scraper
    
    def _scrape_with_retry(self, url: str):
        """Attempt scraping with retries and random delays"""
        scraper = self._setup_scraper()
        
        for attempt in range(self.max_retries):
            try:
                print(f"Attempt {attempt + 1} of {self.max_retries}")
                response = scraper.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response
                
                time.sleep(random.randint(*self.delay_range))
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(random.randint(*self.delay_range))
        
        return None
    
    def scrape_articles(self, keyword: str = "سد النهضة", limit: int = 10) -> List[Dict]:
        """
        Scrape articles from Almasryalyoum based on a search keyword.
        
        Args:
            keyword: Search term to look for
            limit: Maximum number of articles to return
            
        Returns:
            List of dictionaries containing article information
        """
        SEARCH_URL = f"{self.BASE_URL}/news/search?keyword={keyword}"
        
        print("Starting scraping with enhanced bypass techniques...")
        response = self._scrape_with_retry(SEARCH_URL)
        
        if not response:
            print("All scraping attempts failed. The website is blocking aggressively.")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        news_items = soup.select('.last_news ul li')[:limit]  # Safety limit
        
        for item in news_items:
            try:
                link = urljoin(self.BASE_URL, item.find('a')['href'])
                title = item.select_one('.wrap p:not(.time)').get_text(strip=True)
                time_text = item.select_one('.time').get_text(strip=True)
                
                img = item.find('img')
                img_src = img['src'] if img else None
                
                articles.append({
                    'title': title,
                    'url': link,
                    'time': time_text,
                    'image': img_src
                })
            except Exception as e:
                print(f"Error parsing article: {str(e)}")
                continue
        
        return articles
    
    def save_to_json(self, data: List[Dict], filename: str = "response/results.json") -> None:
        """
        Save scraped data to a JSON file.
        
        Args:
            data: List of article dictionaries
            filename: Output filename
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {filename}")