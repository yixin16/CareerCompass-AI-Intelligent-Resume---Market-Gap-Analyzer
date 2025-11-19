"""
Skill Gap Analyzer
Analyzes skill gaps and categorizes by priority
"""

from typing import Dict, List
from collections import Counter
from utils.logger import logger


class SkillGapAnalyzer:
    """Analyzes skill gaps from job matches."""
    
    def analyze_gaps(self, resume_profile: Dict, match_results: List[Dict]) -> Dict:
        """
        Analyze skill gaps across all job matches.
        
        Args:
            resume_profile: Analyzed resume profile
            match_results: List of job match results
            
        Returns:
            Comprehensive gap analysis
        """
        logger.info("Analyzing skill gaps across all matches...")
        
        # Collect all missing skills
        all_missing_required = []
        all_missing_preferred = []
        
        for match in match_results:
            skill_match = match.get('skill_match', {})
            all_missing_required.extend(skill_match.get('missing_required', []))
            all_missing_preferred.extend(skill_match.get('missing_preferred', []))
        
        # Count frequency
        required_counter = Counter(all_missing_required)
        preferred_counter = Counter(all_missing_preferred)
        
        # Categorize by priority
        total_jobs = len(match_results)
        critical_threshold = total_jobs * 0.5  # 50%+ of jobs
        high_threshold = total_jobs * 0.3      # 30%+ of jobs
        
        critical_gaps = []
        high_priority_gaps = []
        medium_priority_gaps = []
        
        for skill, count in required_counter.most_common():
            if count >= critical_threshold:
                critical_gaps.append(skill)
            elif count >= high_threshold:
                high_priority_gaps.append(skill)
            else:
                medium_priority_gaps.append(skill)
        
        # Add some preferred skills to medium
        for skill, count in preferred_counter.most_common(5):
            if skill not in critical_gaps and skill not in high_priority_gaps:
                if skill not in medium_priority_gaps:
                    medium_priority_gaps.append(skill)
        
        analysis = {
            'critical_gaps': critical_gaps,
            'high_priority_gaps': high_priority_gaps,
            'medium_priority_gaps': medium_priority_gaps,
            'total_unique_gaps': len(set(all_missing_required + all_missing_preferred)),
            'gap_frequency': {
                'required': dict(required_counter.most_common(20)),
                'preferred': dict(preferred_counter.most_common(20))
            },
            'gap_summary': self._generate_gap_summary(
                critical_gaps, high_priority_gaps, medium_priority_gaps
            )
        }
        
        logger.info(f"  Critical gaps: {len(critical_gaps)}")
        logger.info(f"  High priority: {len(high_priority_gaps)}")
        logger.info(f"  Medium priority: {len(medium_priority_gaps)}")
        
        return analysis
    
    def _generate_gap_summary(self, critical: List[str], high: List[str],
                             medium: List[str]) -> str:
        """Generate human-readable gap summary."""
        if not critical and not high:
            return "Excellent skill match! Only minor gaps to address."
        elif len(critical) <= 2:
            return f"Focus on learning {len(critical)} critical skills to significantly improve your match."
        elif len(critical) <= 5:
            return f"You have {len(critical)} critical skill gaps. Prioritize learning the top 2-3."
        else:
            return f"Significant skill gaps detected. Consider focusing on a more specific role or intensive upskilling."