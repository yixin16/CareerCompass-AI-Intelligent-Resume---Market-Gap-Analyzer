"""
Ultra-Intelligent Resume Analyzer
Dynamically extracts and validates skills using AI, no hardcoded lists.
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
        AI Pipeline:
        1. Extract Candidates (Heuristics)
        2. Validate Candidates (Semantic AI)
        3. Categorize Valid Skills (Semantic AI)
        4. Determine Proficiency (Context Analysis)
        """
        logger.info("  🧠 AI scanning for technical skills...")
        
        # 1. Candidate Extraction (Find things that LOOK like skills)
        candidates = set()
        candidates.update(re.findall(r'\b[A-Z][a-zA-Z0-9]*(?:\s[A-Z][a-zA-Z0-9]*)*\b', text))
        candidates.update(re.findall(r'\b[a-zA-Z0-9]+\+\+|\b[a-zA-Z0-9]+#|\.net\b|\bnode\.js\b', text, re.IGNORECASE))
        
        stopwords = {"The", "A", "An", "In", "On", "To", "For", "Of", "And", "Work", "Experience", "Education", "University", "Bachelor", "Master", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Present", "Current"}
        clean_candidates = {c.strip() for c in candidates if len(c) > 1 and c not in stopwords and not c.isdigit()}
        
        candidate_list = sorted(list(clean_candidates), key=len, reverse=True)[:150]
        
        valid_skills = {}
        
        # 2. AI Validation Loop
        for cand in candidate_list:
            if self.ai.is_technical_skill(cand, threshold=0.4):
                category = self.ai.classify_category(cand)
                proficiency = self._estimate_proficiency(text, cand)
                
                if category not in valid_skills:
                    valid_skills[category] = []
                    
                valid_skills[category].append({
                    'skill': cand,
                    'proficiency': proficiency
                })
        
        total = sum(len(x) for x in valid_skills.values())
        logger.info(f"  ✓ AI identified {total} skills across {len(valid_skills)} categories.")
        return valid_skills

    def _estimate_proficiency(self, text: str, skill: str) -> float:
        """Check surrounding text for 'expert', 'senior', 'basic'."""
        try:
            idx = text.lower().find(skill.lower())
            if idx == -1: return 0.75
            window = text[max(0, idx-60):min(len(text), idx+60)].lower()
            if any(w in window for w in ['expert', 'advanced', 'lead', 'senior', 'comprehensive']): return 1.0
            if any(w in window for w in ['basic', 'familiar', 'exposure', 'learning']): return 0.5
            return 0.75
        except:
            return 0.75

    def _extract_contact(self, text):
        """Helper for basic contact extraction."""
        email = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return {'email': email.group(0) if email else None}

    def _derive_strengths(self, skills: Dict, years: int) -> List[str]:
        """Generate strength highlights based on data."""
        strengths = []
        if years > 5:
            strengths.append(f"Experienced Professional ({years} years)")
        
        # Find dominant skill category
        max_cat = None
        max_count = 0
        for cat, s_list in skills.items():
            if len(s_list) > max_count:
                max_count = len(s_list)
                max_cat = cat
        
        if max_cat:
            strengths.append(f"Strong background in {max_cat}")
            
        if sum(len(x) for x in skills.values()) > 20:
            strengths.append("Diverse Technical Skillset")
            
        return strengths

    def analyze_resume(self, text: str) -> Dict:
        contact = self._extract_contact(text)
        skills = self.extract_skills_dynamically(text)
        
        # Extract Experience
        years_exp = 0
        years_match = re.findall(r'(\d+)\+?\s*years?', text.lower())
        if years_match:
            years_exp = max([int(y) for y in years_match if int(y) < 40])
            
        # Determine Seniority
        seniority = 'Senior' if years_exp >= 5 else 'Mid-Level' if years_exp >= 2 else 'Junior'
        
        # Generate Strengths
        strengths = self._derive_strengths(skills, years_exp)

        return {
            'contact_info': contact,
            'skills_by_category': skills,
            'total_skills': sum(len(v) for v in skills.values()),
            'experience': {
                'total_years': years_exp,
                'seniority_level': seniority  # <--- FIXED: Added this missing key
            },
            'career_level': seniority,
            'strengths': strengths,
            'achievements': [], # Placeholder for NLP extraction if needed later
            'analysis_timestamp': datetime.now().isoformat()
        }