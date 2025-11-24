import os
import requests
import wikipediaapi
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class ResearchTools:
    """Tools for gathering company information"""
    
    def __init__(self):
        self.scrapingdog_api_key = os.getenv('SCRAPINGDOG_API_KEY')
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='CompanyResearchAgent/1.0 (educational project)'
        )
    
    def search_wikipedia(self, company_name: str) -> Dict[str, str]:
        """Search Wikipedia for company information"""
        try:
            page = self.wiki.page(company_name)
            
            if page.exists():
                # Get first 500 characters of summary
                summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
                
                return {
                    'source': 'Wikipedia',
                    'success': True,
                    'title': page.title,
                    'summary': summary,
                    'url': page.fullurl,
                    'categories': list(page.categories.keys())[:5]
                }
            else:
                return {
                    'source': 'Wikipedia',
                    'success': False,
                    'error': f'No Wikipedia page found for {company_name}'
                }
        except Exception as e:
            return {
                'source': 'Wikipedia',
                'success': False,
                'error': f'Wikipedia error: {str(e)}'
            }
    
    def scrape_company_website(self, url: str) -> Dict[str, str]:
        """Scrape company website using ScrapingDog API"""
        if not self.scrapingdog_api_key:
            return {
                'source': 'ScrapingDog',
                'success': False,
                'error': 'ScrapingDog API key not configured'
            }
        
        try:
            api_url = "https://api.scrapingdog.com/scrape"
            params = {
                'api_key': self.scrapingdog_api_key,
                'url': url,
                'dynamic': 'false'
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Get first 1000 characters
                content = response.text[:1000]
                return {
                    'source': 'ScrapingDog',
                    'success': True,
                    'url': url,
                    'content': content,
                    'status_code': response.status_code
                }
            else:
                return {
                    'source': 'ScrapingDog',
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text[:200]}'
                }
        except Exception as e:
            return {
                'source': 'ScrapingDog',
                'success': False,
                'error': f'Scraping error: {str(e)}'
            }
    
    def search_company_info(self, company_name: str, website_url: Optional[str] = None) -> Dict:
        """Comprehensive company search using all available tools"""
        results = {
            'company_name': company_name,
            'sources': []
        }
        
        # 1. Wikipedia search
        wiki_result = self.search_wikipedia(company_name)
        results['sources'].append(wiki_result)
        
        # 2. Website scraping (if URL provided)
        if website_url:
            scrape_result = self.scrape_company_website(website_url)
            results['sources'].append(scrape_result)
        
        return results
