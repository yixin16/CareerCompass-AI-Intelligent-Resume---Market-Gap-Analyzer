"""
Multi-Source Job Scraper
Scrapes jobs from Indeed RSS, Google Jobs, LinkedIn (without login required)
Includes synthetic job generation for comprehensive analysis
"""

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote_plus
from utils.logger import logger
from config import USER_AGENT, INCLUDE_SYNTHETIC_JOBS
import re


class MultiSourceJobScraper:
    """Scrapes jobs from multiple sources without requiring login."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.results_cache = []
    
    def search_indeed_rss(self, keywords: List[str], location: str = "Malaysia",
                          max_per_keyword: int = 5) -> List[Dict]:
        """Search Indeed using RSS feed (no login required)."""
        logger.info("Searching Indeed via RSS...")
        jobs = []
        
        for keyword in keywords:
            try:
                query = keyword.replace(' ', '+')
                loc = location.replace(' ', '+')
                url = f"https://www.indeed.com/rss?q={query}&l={loc}"
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')[:max_per_keyword]
                    
                    for item in items:
                        title = item.find('title').text if item.find('title') else 'N/A'
                        link = item.find('link').text if item.find('link') else '#'
                        description = item.find('description').text if item.find('description') else ''
                        pub_date = item.find('pubDate').text if item.find('pubDate') else 'N/A'
                        
                        # Extract company
                        company_match = re.search(r'<b>(.+?)</b>', description)
                        company = company_match.group(1) if company_match else "Company via Indeed"
                        
                        # Clean description
                        desc_clean = BeautifulSoup(description, 'html.parser').get_text()
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': location,
                            'description': desc_clean[:500],
                            'url': link,
                            'source': 'Indeed',
                            'posted_date': pub_date,
                            'job_type': 'Full Time'
                        })
                    
                    logger.info(f"  ✓ Indeed: {len(items)} jobs for '{keyword}'")
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.warning(f"  Indeed RSS error for '{keyword}': {e}")
                continue
        
        return jobs
    
    def search_google_jobs(self, keywords: List[str], location: str = "Malaysia",
                          max_per_keyword: int = 3) -> List[Dict]:
        """Create Google Jobs search links."""
        logger.info("Generating Google Jobs search links...")
        jobs = []
        
        for keyword in keywords:
            try:
                query = f"{keyword} jobs in {location}"
                url = f"https://www.google.com/search?q={quote_plus(query)}&ibp=htl;jobs"
                
                jobs.append({
                    'title': f"{keyword.title()} - Google Jobs",
                    'company': "Various Companies (via Google)",
                    'location': location,
                    'description': f"Search {keyword} positions on Google Jobs. "
                                 f"Click to view current openings from multiple employers.",
                    'url': url,
                    'source': 'Google Jobs',
                    'posted_date': 'Current',
                    'job_type': 'Various'
                })
                
                logger.info(f"  ✓ Google Jobs link for '{keyword}'")
                
            except Exception as e:
                logger.warning(f"  Google Jobs error for '{keyword}': {e}")
        
        return jobs
    
    def search_linkedin_public(self, keywords: List[str], location: str = "Malaysia",
                               max_per_keyword: int = 3) -> List[Dict]:
        """Create LinkedIn public job search links."""
        logger.info("Generating LinkedIn job search links...")
        jobs = []
        
        for keyword in keywords:
            try:
                query = quote_plus(keyword)
                loc = quote_plus(location)
                url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}"
                
                jobs.append({
                    'title': f"{keyword.title()} - LinkedIn Jobs",
                    'company': "Various Companies (via LinkedIn)",
                    'location': location,
                    'description': f"Browse {keyword} positions on LinkedIn. "
                                 f"Professional network with extensive job listings.",
                    'url': url,
                    'source': 'LinkedIn',
                    'posted_date': 'Current',
                    'job_type': 'Various'
                })
                
                logger.info(f"  ✓ LinkedIn link for '{keyword}'")
                
            except Exception as e:
                logger.warning(f"  LinkedIn error for '{keyword}': {e}")
        
        return jobs
    
    def generate_synthetic_jobs(self, keywords: List[str], location: str = "Malaysia",
                                count_per_keyword: int = 4) -> List[Dict]:
        """Generate realistic synthetic jobs for analysis."""
        logger.info("Generating realistic job postings for analysis...")
        
        from data.job_templates import get_job_templates
        
        jobs = []
        templates = get_job_templates()
        companies = [
            "Tech Innovations Malaysia", "Digital Solutions Sdn Bhd", "Global Tech Corp",
            "Smart Systems MY", "Future Labs", "Cloud Nine Tech", "Data Insights Corp"
        ]
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            template = None
            
            # Find matching template
            for key, tmpl in templates.items():
                if key in keyword_lower or any(word in keyword_lower for word in key.split()):
                    template = tmpl
                    break
            
            if not template:
                template = list(templates.values())[0]
            
            # Generate jobs
            for i in range(count_per_keyword):
                title = random.choice(template['titles'])
                company = random.choice(companies)
                
                requirements = random.sample(template['requirements'],
                                           min(4, len(template['requirements'])))
                responsibilities = random.sample(template['responsibilities'],
                                               min(3, len(template['responsibilities'])))
                
                description = f"{title} position at {company}.\n\n"
                description += "Requirements:\n" + "\n".join(f"• {req}" for req in requirements)
                description += "\n\nResponsibilities:\n" + "\n".join(f"• {resp}" for resp in responsibilities)
                description += "\n\nBenefits: Competitive salary, health insurance, flexible work."
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': random.choice([location, 'Kuala Lumpur', 'Selangor', 'Remote']),
                    'description': description,
                    'url': f'https://jobs.example.com/{keyword.replace(" ", "-")}-{i+1}',
                    'source': 'Synthetic (for analysis)',
                    'posted_date': random.choice(['1 day ago', '3 days ago', '1 week ago']),
                    'job_type': random.choice(['Full Time', 'Contract', 'Permanent']),
                    'keyword': keyword
                })
        
        logger.info(f"  ✓ Generated {len(jobs)} realistic jobs")
        return jobs
    
    def search_all_sources(self, keywords: List[str], location: str = "Malaysia",
                           max_jobs: int = 30) -> List[Dict]:
        """Search all available sources."""
        all_jobs = []
        
        # Try Indeed RSS
        try:
            indeed_jobs = self.search_indeed_rss(keywords, location, max_per_keyword=3)
            all_jobs.extend(indeed_jobs)
        except Exception as e:
            logger.warning(f"Indeed search failed: {e}")
        
        # Add Google Jobs links
        try:
            google_jobs = self.search_google_jobs(keywords, location, max_per_keyword=2)
            all_jobs.extend(google_jobs)
        except Exception as e:
            logger.warning(f"Google Jobs failed: {e}")
        
        # Add LinkedIn links
        try:
            linkedin_jobs = self.search_linkedin_public(keywords, location, max_per_keyword=2)
            all_jobs.extend(linkedin_jobs)
        except Exception as e:
            logger.warning(f"LinkedIn failed: {e}")
        
        # Supplement with synthetic jobs if needed
        if INCLUDE_SYNTHETIC_JOBS and len(all_jobs) < 10:
            logger.info("Supplementing with synthetic jobs for comprehensive analysis...")
            synthetic_jobs = self.generate_synthetic_jobs(keywords, location, count_per_keyword=4)
            all_jobs.extend(synthetic_jobs)
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        logger.info(f"✓ Total unique jobs: {len(unique_jobs)}")
        return unique_jobs[:max_jobs]