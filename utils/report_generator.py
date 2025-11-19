"""
Report Generator
Creates comprehensive CSV and JSON reports
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from utils.logger import logger


class ReportGenerator:
    """Generates comprehensive reports."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def generate_all_reports(self, resume_profile: Dict, match_results: List[Dict],
                            gap_analysis: Dict, learning_roadmap: Dict) -> Dict[str, Path]:
        """Generate all reports and return file paths."""
        
        report_paths = {}
        
        if match_results:
            # 1. Main job matches report
            report_paths['job_matches'] = self._generate_job_matches_report(
                match_results, resume_profile
            )
            
            # 2. High priority jobs
            high_priority = [r for r in match_results if r['overall_score'] >= 0.65]
            if high_priority:
                report_paths['high_priority'] = self._generate_high_priority_report(
                    high_priority
                )
            
            # 3. Learning roadmap
            report_paths['learning_roadmap'] = self._generate_learning_roadmap_report(
                learning_roadmap, gap_analysis
            )
            
            # 4. Complete JSON analysis
            report_paths['complete_analysis'] = self._generate_json_report(
                resume_profile, match_results, gap_analysis, learning_roadmap
            )
        
        return report_paths
    
    def _generate_job_matches_report(self, results: List[Dict],
                                     resume_profile: Dict) -> Path:
        """Generate main job matches CSV."""
        
        df_data = []
        for r in results:
            df_data.append({
                'Priority': r['priority'],
                'Job Title': r['job_title'],
                'Company': r['company'],
                'Location': r['location'],
                'Match Score': f"{r['overall_score']:.1%}",
                'Match Quality': r['match_quality'],
                'Skills Coverage': f"{r['skill_match']['required_coverage']:.0f}%",
                'Missing Skills': ', '.join(r['skill_match']['missing_required'][:3]) if r['skill_match']['missing_required'] else 'None',
                'Gap Severity': r['skill_match']['gap_severity'],
                'Experience Match': r['experience_match']['years_analysis'],
                'Recommendation': r['recommendation'],
                'Source': r['source'],
                'URL': r['url']
            })
        
        df = pd.DataFrame(df_data)
        path = self.output_dir / f"JOB_MATCHES_DETAILED_{self.timestamp}.csv"
        df.to_csv(path, index=False)
        
        logger.info(f"  ✓ Job matches report: {path.name}")
        return path
    
    def _generate_high_priority_report(self, high_priority: List[Dict]) -> Path:
        """Generate high priority jobs CSV."""
        
        df_data = []
        for r in high_priority:
            strengths = r['insights']['strengths_to_highlight']
            talking_points = r['insights']['talking_points']
            
            df_data.append({
                'Priority': r['priority'],
                'Job Title': r['job_title'],
                'Company': r['company'],
                'Match Score': f"{r['overall_score']:.1%}",
                'Why Good Fit': strengths[0] if strengths else 'Strong overall match',
                'What to Emphasize': talking_points[0] if talking_points else 'Your experience',
                'Action Items': r['action_items'][0] if r['action_items'] else 'Tailor resume',
                'URL': r['url']
            })
        
        df = pd.DataFrame(df_data)
        path = self.output_dir / f"HIGH_PRIORITY_APPLY_NOW_{self.timestamp}.csv"
        df.to_csv(path, index=False)
        
        logger.info(f"  ✓ High priority report: {path.name}")
        return path
    
    def _generate_learning_roadmap_report(self, roadmap: Dict,
                                         gap_analysis: Dict) -> Path:
        """Generate learning roadmap CSV with resource links."""
        
        df_data = []
        
        for resource in roadmap.get('detailed_resources', []):
            skill = resource['skill']
            
            # Get course links
            courses = resource.get('online_courses', [])
            course_links = []
            for course in courses[:3]:  # Top 3 platforms
                course_links.append(f"{course['platform']}: {course['url']}")
            
            # Get practice links
            practice = resource.get('practice_platforms', [])
            practice_links = []
            for p in practice[:2]:  # Top 2 platforms
                practice_links.append(f"{p['name']}: {p['url']}")
            
            # Get documentation
            docs = resource.get('documentation', [])
            doc_links = []
            for doc in docs[:1]:  # Official docs
                doc_links.append(f"{doc['name']}: {doc['url']}")
            
            # Determine priority
            if skill in gap_analysis.get('critical_gaps', []):
                priority = 'CRITICAL'
                priority_emoji = '🔴'
            elif skill in gap_analysis.get('high_priority_gaps', []):
                priority = 'HIGH'
                priority_emoji = '🟡'
            else:
                priority = 'MEDIUM'
                priority_emoji = '🟢'
            
            df_data.append({
                'Priority': f"{priority_emoji} {priority}",
                'Skill': skill,
                'Difficulty': resource.get('difficulty', 'Intermediate'),
                'Est. Time': resource.get('estimated_time', '4 weeks'),
                'Prerequisites': ', '.join(resource.get('prerequisites', [])[:2]) or 'None',
                'Related Skills': ', '.join(resource.get('related_skills', [])[:3]),
                'Top Course Platforms': ' | '.join(course_links) if course_links else 'Search online',
                'Practice Platforms': ' | '.join(practice_links) if practice_links else 'N/A',
                'Documentation': ' | '.join(doc_links) if doc_links else 'N/A',
                'Certifications': ', '.join(resource.get('certifications', [])) or 'N/A'
            })
        
        df = pd.DataFrame(df_data)
        path = self.output_dir / f"SKILL_GAPS_LEARNING_ROADMAP_{self.timestamp}.csv"
        df.to_csv(path, index=False)
        
        logger.info(f"  ✓ Learning roadmap: {path.name}")
        return path
    
    def _generate_json_report(self, resume_profile: Dict, match_results: List[Dict],
                             gap_analysis: Dict, learning_roadmap: Dict) -> Path:
        """Generate complete JSON analysis."""
        
        analysis = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_jobs': len(match_results),
                'high_priority_count': len([r for r in match_results if r['overall_score'] >= 0.65])
            },
            'resume_summary': {
                'career_level': resume_profile.get('career_level'),
                'years_experience': resume_profile['experience']['total_years'],
                'total_skills': resume_profile['total_skills'],
                'expert_skills': resume_profile.get('expert_skills', 0),
                'strengths': resume_profile.get('strengths', [])
            },
            'top_5_matches': [
                {
                    'job': f"{r['job_title']} at {r['company']}",
                    'score': r['overall_score'],
                    'priority': r['priority'],
                    'strengths': r['insights']['strengths_to_highlight'],
                    'gaps': r['insights']['gaps_to_address'],
                    'actions': r['action_items'],
                    'url': r['url']
                }
                for r in match_results[:5]
            ],
            'skill_gaps': {
                'critical': gap_analysis.get('critical_gaps', []),
                'high_priority': gap_analysis.get('high_priority_gaps', []),
                'summary': gap_analysis.get('gap_summary', '')
            },
            'learning_plan': {
                'total_skills': learning_roadmap.get('total_skills', 0),
                'estimated_time': learning_roadmap.get('total_estimated_time', 'N/A'),
                'timeline': learning_roadmap.get('timeline', {})
            }
        }
        
        path = self.output_dir / f"COMPLETE_ANALYSIS_{self.timestamp}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✓ Complete analysis: {path.name}")
        return path