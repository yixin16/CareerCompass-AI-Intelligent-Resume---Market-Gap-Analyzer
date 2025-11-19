"""
Intelligent Job Matcher
Advanced matching with detailed gap analysis and recommendations
"""

import re
from typing import Dict, List
from utils.logger import logger
from config import MATCHING_WEIGHTS, MATCH_THRESHOLDS


class IntelligentJobMatcher:
    """Advanced job matching with gap analysis."""
    
    def __init__(self):
        self.weights = MATCHING_WEIGHTS
    
    def extract_job_requirements(self, job_desc: str, job_title: str) -> Dict:
        """Extract comprehensive job requirements."""
        from data.skill_categories import SKILL_CATEGORIES
        
        text = (job_desc + " " + job_title).lower()
        
        requirements = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_years': 0,
            'seniority_level': 'mid',
            'education_level': None,
            'must_have_count': 0,
            'nice_to_have_count': 0
        }
        
        # Extract skills
        must_have_section = re.search(
            r'(?:required|must have|essential)[:|\s](.*?)(?:preferred|nice to have|$)',
            text, re.DOTALL | re.IGNORECASE
        )
        preferred_section = re.search(
            r'(?:preferred|nice to have|bonus)[:|\s](.*?)(?:responsibilities|$)',
            text, re.DOTALL | re.IGNORECASE
        )
        
        must_have_text = must_have_section.group(1) if must_have_section else text
        preferred_text = preferred_section.group(1) if preferred_section else ""
        
        for category, data in SKILL_CATEGORIES.items():
            for skill in data['skills']:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, must_have_text, re.IGNORECASE):
                    requirements['required_skills'].append(skill)
                elif re.search(pattern, preferred_text, re.IGNORECASE):
                    requirements['preferred_skills'].append(skill)
        
        requirements['required_skills'] = list(set(requirements['required_skills']))
        requirements['preferred_skills'] = list(set(requirements['preferred_skills']))
        
        # Experience
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?).*?experience',
            r'minimum.*?(\d+)\s*(?:years?|yrs?)',
            r'at least.*?(\d+)\s*(?:years?|yrs?)'
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text)
            if match:
                requirements['experience_years'] = int(match.group(1))
                break
        
        # Seniority
        if any(w in text for w in ['senior', 'lead', 'principal', 'staff']):
            requirements['seniority_level'] = 'senior'
        elif any(w in text for w in ['junior', 'entry', 'graduate']):
            requirements['seniority_level'] = 'junior'
        
        return requirements
    
    def calculate_skill_match(self, resume_skills: Dict, job_req: Dict) -> Dict:
        """Calculate detailed skill matching."""
        # Flatten resume skills
        resume_skill_dict = {}
        for category, skill_list in resume_skills.items():
            for skill_data in skill_list:
                resume_skill_dict[skill_data['skill'].lower()] = {
                    'proficiency': skill_data.get('proficiency', 0.75),
                    'category': category
                }
        
        required_skills = [s.lower() for s in job_req.get('required_skills', [])]
        preferred_skills = [s.lower() for s in job_req.get('preferred_skills', [])]
        
        # Match required
        matched_required = []
        missing_required = []
        
        for req_skill in required_skills:
            matched = False
            for res_skill, res_data in resume_skill_dict.items():
                if req_skill in res_skill or res_skill in req_skill:
                    matched_required.append({
                        'skill': req_skill,
                        'proficiency': res_data['proficiency']
                    })
                    matched = True
                    break
            if not matched:
                missing_required.append(req_skill)
        
        # Match preferred
        matched_preferred = []
        missing_preferred = []
        
        for pref_skill in preferred_skills:
            matched = False
            for res_skill in resume_skill_dict.keys():
                if pref_skill in res_skill or res_skill in pref_skill:
                    matched_preferred.append(pref_skill)
                    matched = True
                    break
            if not matched:
                missing_preferred.append(pref_skill)
        
        # Calculate scores
        required_coverage = len(matched_required) / max(len(required_skills), 1) if required_skills else 1.0
        preferred_coverage = len(matched_preferred) / max(len(preferred_skills), 1) if preferred_skills else 0.5
        
        overall_score = (required_coverage * 0.8) + (preferred_coverage * 0.2)
        
        return {
            'score': round(overall_score, 3),
            'required_coverage': round(required_coverage * 100, 1),
            'preferred_coverage': round(preferred_coverage * 100, 1),
            'matched_required': matched_required,
            'missing_required': missing_required,
            'matched_preferred': matched_preferred,
            'missing_preferred': missing_preferred,
            'gap_severity': self._calculate_gap_severity(missing_required, required_skills)
        }
    
    def _calculate_gap_severity(self, missing: List[str], total: List[str]) -> str:
        """Determine gap severity."""
        if not total:
            return "None"
        
        gap_ratio = len(missing) / len(total)
        
        if gap_ratio == 0:
            return "None - Perfect match!"
        elif gap_ratio <= 0.2:
            return "Minor - Easily addressable"
        elif gap_ratio <= 0.4:
            return "Moderate - Requires preparation"
        elif gap_ratio <= 0.6:
            return "Significant - Needs work"
        else:
            return "Critical - May not be suitable"
    
    def calculate_experience_match(self, resume_exp: Dict, job_req: Dict) -> Dict:
        """Calculate experience matching."""
        required_years = job_req.get('experience_years', 0)
        candidate_years = resume_exp.get('total_years', 0)
        
        # Years match
        if required_years == 0:
            years_score = 0.9
            analysis = "No specific requirement"
        elif candidate_years >= required_years * 1.5:
            years_score = 1.0
            analysis = f"Significantly exceeds (+{candidate_years - required_years} years)"
        elif candidate_years >= required_years:
            years_score = 0.95
            analysis = f"Meets requirement"
        elif candidate_years >= required_years * 0.8:
            years_score = 0.75
            analysis = f"Slightly below (short by {required_years - candidate_years})"
        else:
            years_score = max(0.3, candidate_years / max(required_years, 1))
            analysis = f"Below requirement"
        
        # Seniority match
        seniority_matrix = {
            ('junior', 'junior'): (1.0, "Perfect match"),
            ('junior', 'mid'): (0.6, "May need growth potential"),
            ('junior', 'senior'): (0.2, "Significant gap"),
            ('mid', 'junior'): (0.95, "Overqualified"),
            ('mid', 'mid'): (1.0, "Perfect match"),
            ('mid', 'senior'): (0.7, "Close to required"),
            ('senior', 'junior'): (0.9, "Highly overqualified"),
            ('senior', 'mid'): (0.95, "Overqualified"),
            ('senior', 'senior'): (1.0, "Perfect match"),
        }
        
        candidate_level = resume_exp.get('seniority_level', 'mid')
        required_level = job_req.get('seniority_level', 'mid')
        seniority_score, seniority_analysis = seniority_matrix.get(
            (candidate_level, required_level), (0.5, "Uncertain")
        )
        
        final_score = min(1.0, (years_score * 0.6) + (seniority_score * 0.4))
        
        return {
            'score': round(final_score, 3),
            'years_analysis': analysis,
            'seniority_analysis': seniority_analysis,
            'candidate_years': candidate_years,
            'required_years': required_years
        }
    
    def match_with_intelligent_insights(self, resume_profile: Dict, job: Dict) -> Dict:
        """Comprehensive matching with insights."""
        job_title = job.get('title', 'Unknown')
        job_desc = job.get('description', '')
        
        # Extract requirements
        job_req = self.extract_job_requirements(job_desc, job_title)
        
        # Perform matching
        skill_result = self.calculate_skill_match(
            resume_profile.get('skills_by_category', {}),
            job_req
        )
        
        exp_result = self.calculate_experience_match(
            resume_profile.get('experience', {}),
            job_req
        )
        
        # Calculate final score
        final_score = (
            skill_result['score'] * self.weights['skills'] +
            exp_result['score'] * self.weights['experience']
        )
        
        # Determine quality
        if final_score >= MATCH_THRESHOLDS['excellent']:
            quality = "Excellent Match"
            priority = "🔥 URGENT"
            recommendation = "Apply immediately - Ideal candidate!"
        elif final_score >= MATCH_THRESHOLDS['strong']:
            quality = "Strong Match"
            priority = "✅ HIGH"
            recommendation = "Highly recommended"
        elif final_score >= MATCH_THRESHOLDS['good']:
            quality = "Good Match"
            priority = "📝 MEDIUM"
            recommendation = "Good opportunity"
        elif final_score >= MATCH_THRESHOLDS['fair']:
            quality = "Fair Match"
            priority = "⚠️ LOW"
            recommendation = "Consider if interested"
        else:
            quality = "Weak Match"
            priority = "❌ SKIP"
            recommendation = "Not recommended"
        
        # Generate insights
        insights = self._generate_insights(skill_result, exp_result, resume_profile)
        
        return {
            'job_title': job_title,
            'company': job.get('company', 'Unknown'),
            'location': job.get('location', 'N/A'),
            'url': job.get('url', '#'),
            'source': job.get('source', 'Unknown'),
            'overall_score': round(final_score, 3),
            'match_quality': quality,
            'priority': priority,
            'recommendation': recommendation,
            'skill_match': skill_result,
            'experience_match': exp_result,
            'job_requirements': job_req,
            'insights': insights,
            'action_items': self._generate_action_items(skill_result, exp_result)
        }
    
    def _generate_insights(self, skill_result: Dict, exp_result: Dict,
                          resume_profile: Dict) -> Dict:
        """Generate application insights."""
        insights = {
            'strengths_to_highlight': [],
            'gaps_to_address': [],
            'talking_points': [],
            'cover_letter_tips': []
        }
        
        # Strengths
        if skill_result['required_coverage'] >= 80:
            insights['strengths_to_highlight'].append(
                f"Strong technical match ({skill_result['required_coverage']:.0f}% coverage)"
            )
        
        if skill_result['matched_required']:
            top_matched = [s['skill'] for s in skill_result['matched_required'][:3]]
            insights['talking_points'].append(f"Emphasize: {', '.join(top_matched)}")
        
        # Gaps
        if skill_result['missing_required']:
            critical = skill_result['missing_required'][:3]
            insights['gaps_to_address'].append(f"Address: {', '.join(critical)}")
        
        insights['cover_letter_tips'].append("Highlight relevant projects and quick learning")
        
        return insights
    
    def _generate_action_items(self, skill_result: Dict, exp_result: Dict) -> List[str]:
        """Generate action items."""
        actions = []
        
        if skill_result['missing_required']:
            actions.append(f"🎯 Learn: {', '.join(skill_result['missing_required'][:2])}")
        
        if skill_result['score'] >= 0.7:
            actions.append("✍️ Tailor resume to highlight matching skills")
        
        actions.append("🔗 Research company and recent projects")
        
        return actions