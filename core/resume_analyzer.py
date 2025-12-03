"""
Ultra-Intelligent Resume Analyzer (Enhanced)
Extracts structured data, calculates true experience timeline, and utilizes vectorized NLP.
"""

import re
from typing import Dict, List, Set
from datetime import datetime
from utils.logger import logger
from core.semantic_matcher import SemanticMatcher

class UltraIntelligentResumeAnalyzer:
    def __init__(self):
        self.ai = SemanticMatcher()
        
    def extract_skills_dynamically(self, text: str) -> Dict:
        """
        Optimized Pipeline:
        1. Heuristic Extraction (Broad net)
        2. Vectorized Batch Validation (Fast filtering)
        3. Vectorized Categorization
        """
        logger.info("  🧠 AI scanning for technical skills...")
        
        # 1. Candidate Extraction (Heuristics)
        # Fix: Better Regex to capture "C++", "C#", "Node.js", "React Native"
        # Captures capitalized phrases or special tech keywords
        pattern = r'\b[A-Z][a-zA-Z0-9]*\+?\+?#?(?:\s[A-Z][a-zA-Z0-9]*\+?)*\b|\b\.NET\b|\bNode\.js\b|\bReact\.js\b|\bVue\.js\b'
        raw_candidates = set(re.findall(pattern, text))
        
        # Expanded Stopwords List (Noise reduction)
        stopwords = {
            "The", "A", "An", "In", "On", "To", "For", "Of", "And", "With", "By", "At", "From",
            "Work", "Experience", "Education", "University", "College", "School", "Institute",
            "Bachelor", "Master", "PhD", "Diploma", "Degree", "Certified", "Certificate",
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
            "Present", "Current", "Date", "Year", "Month", "Project", "Role", "Manager", "Team", "Member",
            "Senior", "Junior", "Lead", "Associate", "Developer", "Engineer", "Analyst", "Consultant"
        }
        
        # Clean candidates
        clean_candidates = []
        for c in raw_candidates:
            c_clean = c.strip().strip(',').strip('.')
            if len(c_clean) > 1 and c_clean not in stopwords and not c_clean.isdigit():
                clean_candidates.append(c_clean)
        
        # Limit to top N unique candidates to keep inference fast
        candidate_list = list(set(clean_candidates))[:200]
        
        # 2. BATCH Validation (The Speedup)
        # Instead of loop, we send all candidates to the GPU/CPU at once
        valid_skill_names = self.ai.batch_filter_skills(candidate_list, threshold=0.40)
        
        # 3. BATCH Categorization
        categorized_skills = self.ai.batch_classify_categories(valid_skill_names)
        
        # 4. Attach Proficiency (Contextual)
        final_skills = {}
        for category, skills in categorized_skills.items():
            final_skills[category] = []
            for skill in skills:
                proficiency = self._estimate_proficiency(text, skill)
                final_skills[category].append({
                    'skill': skill,
                    'proficiency': proficiency
                })
        
        total = sum(len(x) for x in final_skills.values())
        logger.info(f"  ✓ AI identified {total} skills across {len(final_skills)} categories.")
        return final_skills

    def _estimate_proficiency(self, text: str, skill: str) -> float:
        """Check surrounding text for keywords."""
        try:
            # Find all occurrences
            matches = [m.start() for m in re.finditer(re.escape(skill), text, re.IGNORECASE)]
            if not matches: return 0.75
            
            scores = []
            for idx in matches:
                window = text[max(0, idx-50):min(len(text), idx+50)].lower()
                if any(w in window for w in ['expert', 'advanced', 'proficient', 'architect', 'lead', 'master']): 
                    scores.append(1.0)
                elif any(w in window for w in ['basic', 'familiar', 'learning', 'junior', 'exposure']): 
                    scores.append(0.5)
                else:
                    scores.append(0.75)
            
            return max(scores) if scores else 0.75
        except:
            return 0.75

    def _extract_contact_info(self, text: str) -> Dict:
        """Enhanced regex for Email, Phone, and Links."""
        # Email
        email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        
        # Phone (Supports various formats: +1-555..., (555) ..., 123 456 ...)
        phone = re.search(r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        
        # Links
        links = re.findall(r'(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[a-zA-Z0-9_-]+|github\.com/[a-zA-Z0-9_-]+|portfolio\.[a-z]+)', text)
        
        return {
            'email': email.group(0) if email else None,
            'phone': phone.group(0) if phone else None,
            'links': links
        }

    def _calculate_experience_robust(self, text: str) -> Dict:
        """
        Attempts to calculate experience based on dates (2018 - 2023) 
        rather than just looking for '5 years'.
        """
        # Find years like 20xx
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        years = [int(y) for y in years]
        
        current_year = datetime.now().year
        total_years = 0
        
        if years:
            min_year = min(years)
            max_year = max(years)
            
            # If "Present" or "Current" is found, assume they are working until now
            if re.search(r'\b(Present|Current)\b', text, re.IGNORECASE):
                max_year = current_year
                
            span = max_year - min_year
            # Cap realistic span (e.g. if resume lists DOB 1990, don't count it as work exp)
            if 0 < span < 40:
                total_years = span
        
        # Fallback to text search if date calculation fails or seems off
        if total_years == 0:
            text_years = re.findall(r'(\d+)\+?\s*years?', text.lower())
            if text_years:
                valid_years = [int(y) for y in text_years if int(y) < 40]
                if valid_years:
                    total_years = max(valid_years)

        # Seniority Logic
        if total_years >= 7: seniority = "Staff/Principal"
        elif total_years >= 5: seniority = "Senior"
        elif total_years >= 2: seniority = "Mid-Level"
        else: seniority = "Junior"
        
        return {'total_years': total_years, 'seniority_level': seniority}

    def _derive_strengths(self, skills: Dict, exp_data: Dict) -> List[str]:
        strengths = []
        years = exp_data['total_years']
        
        if years >= 5:
            strengths.append(f"Seasoned Professional ({years}+ years experience)")
        elif years >= 2:
            strengths.append(f"Solid track record ({years} years experience)")
            
        # Find dominant skill category
        max_cat = None
        max_count = 0
        for cat, s_list in skills.items():
            if len(s_list) > max_count:
                max_count = len(s_list)
                max_cat = cat
        
        if max_cat:
            strengths.append(f"Specialized in {max_cat}")
            
        return strengths

    def analyze_resume(self, text: str) -> Dict:
        """Main Entry Point"""
        contact = self._extract_contact_info(text)
        skills = self.extract_skills_dynamically(text)
        exp_data = self._calculate_experience_robust(text)
        strengths = self._derive_strengths(skills, exp_data)

        return {
            'contact_info': contact,
            'skills_by_category': skills,
            'total_skills': sum(len(v) for v in skills.values()),
            'experience': exp_data,
            'career_level': exp_data['seniority_level'],
            'strengths': strengths,
            'analysis_timestamp': datetime.now().isoformat()
        }