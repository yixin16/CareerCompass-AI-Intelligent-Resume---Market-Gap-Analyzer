"""
Helper Functions
Utility functions for printing banners, summaries, etc.
"""

import pandas as pd
from typing import Dict, List
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*100)
    print("🎯 ULTRA-INTELLIGENT AI RESUME ANALYZER".center(100))
    print("Professional Resume Analysis | Job Matching | Learning Roadmap".center(100))
    print("="*100 + "\n")


def print_summary(resume_profile: Dict, match_results: List[Dict],
                 gap_analysis: Dict, learning_roadmap: Dict,
                 report_paths: Dict[str, Path]):
    """Print beautiful summary to console."""
    
    print("\n" + "="*100)
    print("📊 ANALYSIS SUMMARY".center(100))
    print("="*100)
    
    # Profile Summary
    print(f"\n{'📋 YOUR PROFILE':.^100}")
    print(f"Career Level: {resume_profile.get('career_level', 'N/A')}")
    print(f"Experience: {resume_profile['experience']['total_years']} years "
          f"({resume_profile['experience']['seniority_level'].upper()})")
    print(f"Skills: {resume_profile['total_skills']} total "
          f"({resume_profile.get('expert_skills', 0)} expert-level)")
    print(f"Achievements: {len(resume_profile.get('achievements', []))} quantified")
    
    # Strengths
    if resume_profile.get('strengths'):
        print(f"\n💪 Your Key Strengths:")
        for strength in resume_profile['strengths'][:3]:
            print(f"  • {strength}")
    
    if not match_results:
        print(f"\n⚠️ No job matches found")
        print("="*100 + "\n")
        return
    
    # Statistics
    df = pd.DataFrame(match_results)
    print(f"\n{'📊 MATCHING STATISTICS':.^100}")
    print(f"Total Jobs Analyzed: {len(match_results)}")
    print(f"🔥 Urgent/Excellent (80%+): {len(df[df['overall_score'] >= 0.80])}")
    print(f"✅ High Priority (65%+): {len(df[df['overall_score'] >= 0.65])}")
    print(f"📝 Medium Priority (50%+): {len(df[df['overall_score'] >= 0.50])}")
    print(f"Average Match Score: {df['overall_score'].mean():.1%}")
    
    # Skill Gaps
    print(f"\n{'🎯 SKILL GAP ANALYSIS':.^100}")
    print(f"Critical Gaps: {len(gap_analysis.get('critical_gaps', []))}")
    print(f"High Priority: {len(gap_analysis.get('high_priority_gaps', []))}")
    print(f"Medium Priority: {len(gap_analysis.get('medium_priority_gaps', []))}")
    if gap_analysis.get('critical_gaps'):
        print(f"\nTop Skills to Learn: {', '.join(gap_analysis['critical_gaps'][:3])}")
    
    # Learning Plan
    print(f"\n{'📚 LEARNING PLAN':.^100}")
    print(f"Skills to Learn: {learning_roadmap.get('total_skills', 0)}")
    print(f"Estimated Time: {learning_roadmap.get('total_estimated_time', 'N/A')}")
    
    # Top Matches
    print(f"\n{'🏆 TOP 5 OPPORTUNITIES':.^100}")
    print("-"*100)
    
    for idx, result in enumerate(match_results[:5], 1):
        print(f"\n{idx}. {result['priority']} {result['job_title']}")
        print(f"   Company: {result['company']} | Location: {result['location']}")
        print(f"   Match: {result['overall_score']:.1%} ({result['match_quality']})")
        print(f"   {result['recommendation']}")
        
        if result['insights']['strengths_to_highlight']:
            print(f"   ✨ {result['insights']['strengths_to_highlight'][0]}")
        
        if result['action_items']:
            print(f"   📋 {result['action_items'][0]}")
        
        print(f"   🔗 {result['url']}")
    
    print("\n" + "="*100)
    print("✅ ANALYSIS COMPLETE!".center(100))
    print("="*100)