"""
Semantic Gap Analyzer
Clusters missing skills by meaning to give accurate recommendations.
"""

from typing import Dict, List
from collections import Counter
from core.semantic_matcher import SemanticMatcher
from utils.logger import logger

class SkillGapAnalyzer:
    def __init__(self):
        self.ai = SemanticMatcher()
        
    def analyze_gaps(self, resume_profile: Dict, match_results: List[Dict]) -> Dict:
        """
        Collects all missing skills and clusters synonyms.
        """
        logger.info("📊 AI analyzing skill gaps...")
        
        all_missing_raw = []
        for match in match_results:
            all_missing_raw.extend(match['skill_match']['missing_required'])
            
        # Semantic Deduplication / Clustering
        # We maintain a list of unique "canonical" skills.
        # If a new skill matches a canonical one semantically, we increment the canonical count.
        
        clustered_counts = {} # { 'Canonical Name': count }
        
        for raw in all_missing_raw:
            # Is this similar to an existing cluster?
            existing_clusters = list(clustered_counts.keys())
            match, score = self.ai.find_best_match(raw, existing_clusters, threshold=0.85)
            
            if match:
                clustered_counts[match] += 1
            else:
                clustered_counts[raw] = 1
                
        # Prioritize
        sorted_gaps = sorted(clustered_counts.items(), key=lambda x: x[1], reverse=True)
        
        critical = [k for k, v in sorted_gaps if v >= 2] # Appeared in at least 2 jobs
        medium = [k for k, v in sorted_gaps if v == 1]
        
        return {
            'critical_gaps': critical[:5], # Top 5 most frequent unique skills
            'medium_priority_gaps': medium[:5],
            'total_unique_gaps': len(clustered_counts),
            'gap_frequencies': clustered_counts
        }