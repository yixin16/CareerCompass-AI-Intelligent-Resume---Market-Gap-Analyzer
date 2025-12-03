"""
Intelligent Job Matcher
Uses Vector Similarity to match skills regardless of exact naming.
Updated for Batch Processing (High Performance).
"""

import re
from typing import Dict, List, Any
from core.semantic_matcher import SemanticMatcher
from utils.logger import logger

class IntelligentJobMatcher:
    def __init__(self):
        self.ai = SemanticMatcher()
        # Weights for the final score
        self.weights = {'skills': 0.8, 'experience': 0.2}

    def extract_job_requirements(self, job_desc: str, job_title: str) -> Dict:
        """
        Extracts requirements dynamically using AI validation.
        UPDATED: Uses Batch Processing for speed.
        """
        # 1. Extract potential technical nouns (Heuristic Regex)
        # We look for Capitalized words or special tech terms like C++, .NET
        candidates = set(re.findall(
            r'\b[A-Z][a-zA-Z0-9+#]*\b|\b\.NET\b|\bNode\.js\b', 
            job_desc
        ))
        
        # Define stopwords to filter noise
        stopwords = {
            "The", "A", "To", "For", "Of", "In", "And", "With", "We", "You", "Our", "Are", "Is",
            "Job", "Role", "Team", "Work", "Experience", "Skills", "Requirements", "Degree",
            "Bachelor", "Master", "PhD", "Computer", "Science", "Engineering", "Apply",
            "Responsibility", "Duties", "Qualifications", "Preferred", "Plus", "Strong",
            "Knowledge", "Understanding", "Proficiency", "Years", "Location", "Remote",
            "Global", "Local", "Business", "Client", "Service", "Solution"
        }
        
        filtered_candidates = [
            c for c in candidates 
            if len(c) > 1 and c not in stopwords and not c.isdigit()
        ]
        
        # 2. AI VALIDATION (The Fix: Using Batch Processing)
        # Instead of calling .is_technical_skill() in a loop, we filter all at once.
        if filtered_candidates:
            required_skills = self.ai.batch_filter_skills(
                filtered_candidates, 
                threshold=0.45
            )
        else:
            required_skills = []
                
        return {
            'required_skills': required_skills,
            'job_title_features': job_title.lower().split()
        }

    def _calculate_gap_severity(self, missing_count: int, total_count: int) -> str:
        """Determine how severe the skill gap is."""
        if total_count == 0:
            return "None"
        
        ratio = missing_count / total_count
        
        if ratio == 0:
            return "None - Perfect Match"
        elif ratio <= 0.2:
            return "Minor"
        elif ratio <= 0.4:
            return "Moderate"
        elif ratio <= 0.6:
            return "Significant"
        else:
            return "Critical"

    def calculate_skill_match(self, resume_profile: Dict, job_req: Dict) -> Dict:
        """
        Matches Resume Skills (Flattened) vs Job Requirements using Semantic AI.
        """
        # Flatten resume skills into a single list
        resume_skill_list = []
        for cat, skills in resume_profile.get('skills_by_category', {}).items():
            for s in skills:
                # Handle both dict format and string format
                if isinstance(s, dict):
                    resume_skill_list.append(s.get('skill', ''))
                else:
                    resume_skill_list.append(str(s))
        
        matched = []
        missing = []
        ai_insights = []
        
        required = job_req.get('required_skills', [])
        
        if not required:
            return {
                'score': 0, 
                'required_coverage': 0.0,
                'gap_severity': "Unknown",
                'matched_required': [], 
                'missing_required': [], 
                'ai_insights': [],
                'details': 'No clear requirements found'
            }

        for req in required:
            # 1. Try Exact Match (Fastest)
            # Case-insensitive check
            if any(req.lower() == r.lower() for r in resume_skill_list):
                matched.append({'skill': req, 'method': 'Exact'})
                continue
                
            # 2. Try AI Semantic Match (Slower but Smarter)
            # Note: Since find_best_match is a semantic operation, we keep it here.
            # (It's 1-to-N comparison, which is fast enough for ~50 resume skills)
            best_match, score = self.ai.find_best_match(req, resume_skill_list, threshold=0.70)
            
            if best_match:
                matched.append({'skill': req, 'method': 'AI', 'matched_with': best_match})
                ai_insights.append(f"🧠 AI Inference: Job asked for '{req}', matched with your '{best_match}'")
            else:
                missing.append(req)
        
        # Calculate scores
        score = len(matched) / max(len(required), 1)
        severity = self._calculate_gap_severity(len(missing), len(required))
        
        return {
            'score': round(score, 3),
            'required_coverage': round(score * 100, 1),
            'gap_severity': severity,
            'matched_required': matched,
            'missing_required': missing,
            'ai_insights': ai_insights,
            'match_count': len(matched),
            'total_reqs': len(required)
        }

    def calculate_experience_match(self, resume_years: int, job_desc: str) -> Dict:
        """
        Simple heuristic to determine experience match based on job description text.
        """
        req_years_match = re.search(r'(\d+)\+?\s*years?', job_desc.lower())
        req_years = int(req_years_match.group(1)) if req_years_match else 0
        
        if req_years == 0:
            return {'score': 1.0, 'years_analysis': "Not specified"}
        
        diff = resume_years - req_years
        
        if diff >= 0:
            return {'score': 1.0, 'years_analysis': f"Meets requirement ({req_years}+ years)"}
        elif diff >= -1:
            return {'score': 0.8, 'years_analysis': f"Slightly below ({req_years} years required)"}
        elif diff >= -3:
            return {'score': 0.5, 'years_analysis': f"Below requirement ({req_years} years required)"}
        else:
            return {'score': 0.2, 'years_analysis': f"Significant gap ({req_years} years required)"}

    def _generate_insights(self, skill_res: Dict) -> Dict:
        """Generate human-readable insights for the report."""
        strengths = []
        talking_points = []
        
        # Generate strengths based on matches
        if skill_res['matched_required']:
            top_skills = [m['skill'] for m in skill_res['matched_required'][:3]]
            strengths.append(f"Strong technical match for: {', '.join(top_skills)}")
        else:
            strengths.append("General profile alignment")
            
        if skill_res['ai_insights']:
            strengths.append(f"AI identified {len(skill_res['ai_insights'])} transferable skills")

        # Generate talking points
        if skill_res['matched_required']:
            skill = skill_res['matched_required'][0]['skill']
            talking_points.append(f"Highlight your practical experience with {skill}")
            
        if skill_res['missing_required']:
            missing = skill_res['missing_required'][0]
            talking_points.append(f"Address how you plan to learn {missing} quickly")

        return {
            'strengths_to_highlight': strengths,
            'talking_points': talking_points,
            'gaps_to_address': skill_res['missing_required'],
            'ai_matches': skill_res['ai_insights']
        }

    def _generate_action_items(self, skill_res: Dict) -> List[str]:
        """Generate actionable advice."""
        actions = []
        
        if skill_res['missing_required']:
            top_missing = skill_res['missing_required'][:2]
            actions.append(f"Prioritize learning: {', '.join(top_missing)}")
        
        if skill_res['score'] > 0.7:
            actions.append("Tailor resume summary to match job keywords")
        else:
            actions.append("Focus on bridging critical skill gaps before applying")
            
        return actions

    def match_with_intelligent_insights(self, resume_profile: Dict, job: Dict) -> Dict:
        """Main matching function called by main.py"""
        
        # 1. Extract Requirements
        job_desc = job.get('description', '')
        job_title = job.get('title', '')
        
        # The key fix is inside this method call
        job_reqs = self.extract_job_requirements(job_desc, job_title)
        
        # 2. Calculate Skill Match
        skill_res = self.calculate_skill_match(resume_profile, job_reqs)
        
        # 3. Calculate Experience Match
        # Safe get for nested dicts
        exp_data = resume_profile.get('experience', {})
        if isinstance(exp_data, dict):
            resume_years = exp_data.get('total_years', 0)
        else:
            resume_years = 0 # Fallback
            
        exp_res = self.calculate_experience_match(resume_years, job_desc)
        
        # 4. Semantic Title Match 
        career_level = resume_profile.get('career_level', 'Mid-Level')
        candidate_title_proxy = f"{career_level} Developer"
        title_sim = self.ai.get_similarity(job_title, candidate_title_proxy)
        
        # 5. Final Weighted Score
        final_score = (skill_res['score'] * 0.6) + (title_sim * 0.2) + (exp_res['score'] * 0.2)
        
        # 6. Determine Match Quality & Priority
        if final_score >= 0.8:
            match_quality = "Excellent"
            priority = "🔥 URGENT"
            recommendation = "Apply immediately"
        elif final_score >= 0.65:
            match_quality = "Strong"
            priority = "✅ HIGH"
            recommendation = "Highly recommended"
        elif final_score >= 0.5:
            match_quality = "Good"
            priority = "📝 MEDIUM"
            recommendation = "Good opportunity"
        else:
            match_quality = "Weak"
            priority = "⚠️ LOW"
            recommendation = "Focus on skills"
            
        # 7. Generate Insights
        insights = self._generate_insights(skill_res)
        action_items = self._generate_action_items(skill_res)

        return {
            'job_title': job_title,
            'company': job.get('company', 'Unknown'),
            'location': job.get('location', 'N/A'),
            'url': job.get('url', '#'),
            'source': job.get('source', 'Unknown'),
            'overall_score': round(final_score, 2),
            'match_quality': match_quality,
            'priority': priority,
            'recommendation': recommendation,
            'skill_match': skill_res,
            'experience_match': exp_res,
            'insights': insights,
            'action_items': action_items,
            # IMPORTANT: Pass raw data for the Resume Tailor feature
            'raw_text': job_desc 
        }