"""
Intelligent Gap Analyzer
Clusters missing skills semantically, categorizes them by domain, 
and calculates a 'Severity Score' for the learning roadmap.
"""

from typing import Dict, List, Tuple
from collections import Counter
from core.semantic_matcher import SemanticMatcher
from utils.logger import logger

class SkillGapAnalyzer:
    def __init__(self):
        self.ai = SemanticMatcher()
        
    def analyze_gaps(self, resume_profile: Dict, match_results: List[Dict]) -> Dict:
        """
        1. Aggregates missing skills from all job matches.
        2. Clusters synonyms (e.g., "AWS" == "Amazon Web Services").
        3. Classifies gaps by Domain (Cloud, Coding, etc.).
        4. Prioritizes based on Frequency + Domain Weight.
        """
        logger.info("📊 AI analyzing skill gaps across market data...")
        
        if not match_results:
            return {'critical_gaps': [], 'medium_priority_gaps': [], 'all_gaps': []}

        # --- STEP 1: Aggregation & Semantic Clustering ---
        # We want to map { "Raw Skill Name": count }
        clustered_gaps = {} 
        
        raw_missing_list = []
        for match in match_results:
            # We look at 'missing_required' from the job_matcher output
            raw_missing_list.extend(match.get('skill_match', {}).get('missing_required', []))

        # Optimization: Process most frequent first
        raw_counts = Counter(raw_missing_list)
        
        # Canonical Mapping: "ReactJS" -> "React"
        canonical_map = {} 
        
        for raw_skill, count in raw_counts.most_common():
            # Check if this raw_skill matches an existing canonical cluster
            existing_clusters = list(clustered_gaps.keys())
            
            # Use strict threshold to avoid merging distinct tools (e.g., Java vs JavaScript)
            match, score = self.ai.find_best_match(raw_skill, existing_clusters, threshold=0.85)
            
            if match:
                # It's a synonym for an existing cluster
                clustered_gaps[match] += count
                canonical_map[raw_skill] = match
            else:
                # Create new cluster
                clustered_gaps[raw_skill] = count
                canonical_map[raw_skill] = raw_skill

        # --- STEP 2: Intelligent Categorization ---
        # We classify all unique gap names to understand WHAT kind of gap it is.
        unique_gaps = list(clustered_gaps.keys())
        
        # Batch classification using the vector engine
        categorized_gaps = self.ai.batch_classify_categories(unique_gaps)
        
        # Invert the map: Skill -> Category
        skill_to_cat = {}
        for cat, skills in categorized_gaps.items():
            for s in skills:
                skill_to_cat[s] = cat

        # --- STEP 3: Severity Scoring ---
        # Formula: Frequency * Domain_Weight
        # Tech skills (Programming/Data) are harder to learn -> Higher Priority
        domain_weights = {
            'Programming': 1.5,
            'Data & AI': 1.4,
            'Cloud & DevOps': 1.3,
            'Web & UI': 1.2,
            'Soft Skills': 0.8, # Important, but usually not a "Hard blocker" for initial screening
            'Unknown': 1.0
        }

        scored_gaps = []
        total_jobs = len(match_results)

        for skill, frequency in clustered_gaps.items():
            category = skill_to_cat.get(skill, 'General')
            weight = domain_weights.get(category, 1.0)
            
            # Severity Calculation
            severity_score = frequency * weight
            
            # Market Penetration: What % of jobs asked for this?
            penetration = (frequency / total_jobs) * 100

            scored_gaps.append({
                'skill': skill,
                'category': category,
                'frequency': frequency,
                'market_penetration': round(penetration, 1),
                'severity_score': round(severity_score, 2)
            })

        # --- STEP 4: Sorting & Grouping ---
        # Sort by Severity Score (Highest first)
        scored_gaps.sort(key=lambda x: x['severity_score'], reverse=True)
        
        critical_gaps = []
        medium_gaps = []
        low_gaps = []

        for gap in scored_gaps:
            # Dynamic Thresholds
            if gap['market_penetration'] > 40 or gap['severity_score'] >= 2.5:
                # If it appears in >40% of jobs OR has high weighted score
                gap['priority_label'] = "Critical"
                critical_gaps.append(gap['skill'])
            elif gap['frequency'] > 1:
                gap['priority_label'] = "High"
                medium_gaps.append(gap['skill'])
            else:
                gap['priority_label'] = "Nice-to-Have"
                low_gaps.append(gap['skill'])

        logger.info(f"  ✓ Identified {len(critical_gaps)} critical gaps.")

        return {
            'critical_gaps': critical_gaps,      # List[str] for simple consumption
            'medium_priority_gaps': medium_gaps, # List[str]
            'low_priority_gaps': low_gaps,       # List[str]
            'detailed_analysis': scored_gaps,    # Full dict with scores for UI
            'domain_breakdown': {k: len(v) for k, v in categorized_gaps.items()} # Stats for charts
        }