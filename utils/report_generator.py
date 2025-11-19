"""
Report Generator (Intelligence Edition)
Creates reports with strategic advice, not just raw data.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from utils.logger import logger

class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _derive_strategy(self, match_score: float, missing_skills: List[str]) -> str:
        """Generates intelligent advice based on the score."""
        if match_score >= 0.8:
            return "🚀 PRIME TARGET: Customize resume keywords and apply immediately."
        elif match_score >= 0.6:
            return f"📈 GOOD FIT: Address gap in '{missing_skills[0]}' via cover letter." if missing_skills else "Good fit, apply."
        elif match_score >= 0.4:
            return "📚 STRETCH ROLE: Requires 2-3 weeks upskilling before applying."
        else:
            return "🛑 LONG TERM: Add to career roadmap, do not apply yet."

    def generate_all_reports(self, resume_profile: Dict, match_results: List[Dict],
                            gap_analysis: Dict, learning_roadmap: Dict) -> Dict[str, Path]:
        
        paths = {}
        if match_results:
            paths['job_matches'] = self._generate_job_matches_report(match_results)
            
            # Filter high priority
            high_priority = [r for r in match_results if r['overall_score'] >= 0.60]
            if high_priority:
                paths['high_priority'] = self._generate_high_priority_report(high_priority)
            
            paths['learning_roadmap'] = self._generate_learning_roadmap_report(learning_roadmap)
            paths['complete_analysis'] = self._generate_json_report(
                resume_profile, match_results, gap_analysis
            )
        return paths
    
    def _generate_job_matches_report(self, results: List[Dict]) -> Path:
        """Detailed CSV with Strategy Column."""
        df_data = []
        for r in results:
            missing = r['skill_match'].get('missing_required', [])
            
            # Safely handle insights structure
            insights = r.get('insights', {})
            talking_points = insights.get('talking_points', [])
            ai_insight_text = talking_points[0] if talking_points else ''

            df_data.append({
                'Strategy': self._derive_strategy(r['overall_score'], missing),
                'Job Title': r['job_title'],
                'Company': r['company'],
                'Match Score': f"{r['overall_score']:.1%}",
                'Missing Critical Skills': ', '.join(missing[:3]) if missing else 'None',
                'AI Insights': ai_insight_text,
                'Location': r['location'],
                'Source': r.get('source', 'Unknown'),
                'URL': r['url']
            })
        
        df = pd.DataFrame(df_data)
        path = self.output_dir / f"JOB_MATCHES_STRATEGIC_{self.timestamp}.csv"
        df.to_csv(path, index=False)
        logger.info(f"  ✓ Strategic Job Report: {path.name}")
        return path
    
    def _generate_high_priority_report(self, high_priority: List[Dict]) -> Path:
        """Focus list for immediate application."""
        df_data = []
        for r in high_priority:
            insights = r.get('insights', {})
            strengths = insights.get('strengths_to_highlight', [])
            gaps = insights.get('gaps_to_address', [])

            df_data.append({
                'Job': r['job_title'],
                'Company': r['company'],
                'Score': f"{r['overall_score']:.1%}",
                'Why You Match': strengths[0] if strengths else "Skills Align",
                'Gap to Fix': gaps[0] if gaps else "None",
                'Apply URL': r['url']
            })
        
        df = pd.DataFrame(df_data)
        path = self.output_dir / f"HIGH_PRIORITY_HOTLIST_{self.timestamp}.csv"
        df.to_csv(path, index=False)
        logger.info(f"  ✓ Hotlist Report: {path.name}")
        return path
    
    def _generate_learning_roadmap_report(self, roadmap: Dict) -> Path:
        """Roadmap CSV."""
        df_data = []
        for res in roadmap.get('detailed_resources', []):
            
            # --- FIX: Handle 'name' instead of 'platform' ---
            courses_list = res.get('online_courses', [])
            # Limit to top 2 links to keep CSV clean
            courses_str = " | ".join([f"{c.get('name', 'Link')}: {c.get('url', '#')}" for c in courses_list[:2]])
            
            df_data.append({
                'Skill': res['skill'],
                'Category': res.get('category', 'General'),
                'Difficulty': res.get('difficulty', 'Medium'),
                'Est. Time': res.get('estimated_time', 'Unknown'),
                'Coach Strategy': res.get('strategy_tip', 'Practice daily.'),
                'Suggested Project': res.get('recommended_project', 'Build a portfolio project.'),
                'Top Resources': courses_str
            })
        
        df = pd.DataFrame(df_data)
        path = self.output_dir / f"LEARNING_ROADMAP_{self.timestamp}.csv"
        df.to_csv(path, index=False)
        logger.info(f"  ✓ Roadmap Report: {path.name}")
        return path

    def _generate_json_report(self, profile: Dict, matches: List, gaps: Dict) -> Path:
        """Full JSON dump."""
        data = {
            'metadata': {'timestamp': datetime.now().isoformat()},
            'candidate_summary': {
                'level': profile.get('career_level'),
                'top_strengths': profile.get('strengths', [])
            },
            'market_fit_analysis': {
                'total_jobs_scanned': len(matches),
                'average_match_score': sum(m['overall_score'] for m in matches) / max(len(matches), 1)
            },
            'matches': matches[:10], # Top 10 only to save space
            'gaps': gaps
        }
        path = self.output_dir / f"FULL_ANALYSIS_{self.timestamp}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return path