"""
Multi-Source Job Scraper (Unified Dorking Edition)
Strategy: Uses DuckDuckGo to find public job pages on Indeed, JobStreet, and LinkedIn.
Why? Direct scraping is blocked. RSS is dead. Search Engines are the only open door.
"""

import time
import random
import requests
import warnings
from typing import List, Dict
from utils.logger import logger
from config import USER_AGENT, INCLUDE_SYNTHETIC_JOBS

# Suppress warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

# Import DDGS
try:
    from ddgs import DDGS
    DDG_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDG_AVAILABLE = True
    except ImportError:
        DDG_AVAILABLE = False

class MultiSourceJobScraper:
    def __init__(self):
        self.session = requests.Session()

    def _dork_search(self, site_domain: str, source_name: str, keywords: List[str], location: str) -> List[Dict]:
        """
        Generic function to scrape any job site via DuckDuckGo.
        """
        if not DDG_AVAILABLE:
            logger.warning("DuckDuckGo library missing. Please run: pip install ddgs")
            return []

        logger.info(f"  🔎 Dorking {source_name} via DuckDuckGo...")
        jobs = []
        
        for keyword in keywords:
            try:
                # Broad search query: site:jobstreet.com.my "data scientist" malaysia
                query = f'site:{site_domain} "{keyword}" {location}'
                
                with DDGS() as ddgs:
                    # Get top results
                    results = list(ddgs.text(query, max_results=6))
                
                for res in results:
                    title = res.get('title', 'Unknown Job')
                    link = res.get('href', '')
                    body = res.get('body', '')
                    
                    # Skip non-job pages (e.g., login pages, category listings)
                    if "login" in link or "signup" in link or "category" in link:
                        continue
                        
                    # Basic Cleanup
                    clean_title = title.split(" | ")[0].split(" - ")[0].strip()
                    
                    jobs.append({
                        'title': clean_title,
                        'company': f"{source_name} Employer", # Hard to extract without visiting
                        'location': location,
                        'description': body, # Search snippet often contains requirements
                        'url': link,
                        'source': f"{source_name} (Dork)",
                        'posted_date': 'Recent'
                    })
                
                # Sleep to prevent DDG rate limiting
                time.sleep(random.uniform(2.0, 4.0))
                
            except Exception:
                continue
        
        logger.info(f"    -> Found {len(jobs)} potential jobs on {source_name}")
        return jobs

    def search_jobstreet_via_dork(self, keywords: List[str], location: str) -> List[Dict]:
        # Relaxed query: Just looking for the domain, not specific subfolders
        return self._dork_search("jobstreet.com.my", "JobStreet", keywords, location)

    def search_indeed_via_dork(self, keywords: List[str], location: str) -> List[Dict]:
        # Indeed Malaysia domain
        return self._dork_search("malaysia.indeed.com", "Indeed", keywords, location)

    def search_linkedin_via_dork(self, keywords: List[str], location: str) -> List[Dict]:
        # Targeted view pages
        return self._dork_search("linkedin.com/jobs/view", "LinkedIn", keywords, location)

    def search_glassdoor_via_dork(self, keywords: List[str], location: str) -> List[Dict]:
        # Glassdoor Malaysia
        return self._dork_search("glassdoor.com", "Glassdoor", keywords, location)

    def generate_synthetic_jobs(self, keywords: List[str], location: str) -> List[Dict]:
        """Fallback generator."""
        logger.info("  ⚠️ Generating synthetic jobs (Fallback)...")
        from data.job_templates import get_job_templates
        jobs = []
        templates = get_job_templates()
        for k in keywords:
            t = templates.get('data_scientist', {})
            jobs.append({
                'title': f"Senior {k.title()}",
                'company': "Fallback Systems",
                'location': location,
                'description': " ".join(t.get('requirements', [])),
                'url': "https://fallback.com",
                'source': 'Synthetic',
                'posted_date': 'Today'
            })
        return jobs

    def search_all_sources(self, keywords: List[str], location: str = "Malaysia", max_jobs: int = 30) -> List[Dict]:
        """Master Search Aggregator"""
        all_jobs = []
        
        # Run Dorking on all major platforms
        all_jobs.extend(self.search_linkedin_via_dork(keywords, location))
        all_jobs.extend(self.search_jobstreet_via_dork(keywords, location))
        all_jobs.extend(self.search_indeed_via_dork(keywords, location))
        all_jobs.extend(self.search_glassdoor_via_dork(keywords, location))
        
        # Deduplicate
        unique = {j['url']: j for j in all_jobs}.values()
        final_list = list(unique)
        
        logger.info(f"✓ Found {len(final_list)} jobs from real-world sources.")
        
        if not final_list and INCLUDE_SYNTHETIC_JOBS:
            return self.generate_synthetic_jobs(keywords, location)
            
        return final_list[:max_jobs]