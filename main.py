"""
Ultra-Intelligent Resume Analyzer - Main Entry Point
A professional-grade system for resume analysis, job matching, and learning roadmaps
"""

import sys
from pathlib import Path
from datetime import datetime

# Add core and utils to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    JOB_SEARCH_KEYWORDS,
    JOB_SEARCH_LOCATION,
    TOTAL_MAX_JOBS,
    OUTPUT_DIR
)
from utils.logger import logger
from core.resume_parser import ResumeParser
from core.resume_analyzer import UltraIntelligentResumeAnalyzer
from core.job_scraper import MultiSourceJobScraper
from core.job_matcher import IntelligentJobMatcher
from core.gap_analyzer import SkillGapAnalyzer
from core.learning_roadmap import LearningRoadmapGenerator
from utils.report_generator import ReportGenerator
from utils.helpers import print_banner, print_summary


def main():
    """Main execution flow."""
    
    # Print welcome banner
    print_banner()
    
    try:
        # ========================================
        # STEP 1: LOAD & PARSE RESUME
        # ========================================
        logger.info("="*80)
        logger.info("STEP 1: LOADING RESUME")
        logger.info("="*80)
        
        resume_path = ResumeParser.find_resume()
        if not resume_path:
            logger.error("❌ No resume found in sample_data/resumes/")
            logger.info("💡 Place your resume (PDF/DOCX/TXT) in: sample_data/resumes/")
            return
        
        logger.info(f"📄 Found: {resume_path.name}")
        
        resume_text = ResumeParser.extract_text(resume_path)
        if not resume_text or len(resume_text) < 100:
            logger.error("❌ Could not extract text from resume or file is too short")
            return
        
        logger.info(f"✓ Extracted {len(resume_text)} characters")
        
        # ========================================
        # STEP 2: ANALYZE RESUME
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 2: ANALYZING RESUME WITH AI")
        logger.info("="*80)
        
        analyzer = UltraIntelligentResumeAnalyzer()
        resume_profile = analyzer.analyze_resume(resume_text)
        
        if not resume_profile:
            logger.error("❌ Resume analysis failed")
            return
        
        logger.info(f"✓ Analysis complete")
        logger.info(f"  📊 Career Level: {resume_profile.get('career_level', 'N/A')}")
        logger.info(f"  💼 Experience: {resume_profile['experience']['total_years']} years")
        logger.info(f"  🎯 Skills: {resume_profile['total_skills']} (including {resume_profile.get('expert_skills', 0)} expert)")
        logger.info(f"  🏆 Achievements: {len(resume_profile.get('achievements', []))}")
        
        # ========================================
        # STEP 3: SEARCH FOR JOBS
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 3: SEARCHING FOR RELEVANT JOBS")
        logger.info("="*80)
        logger.info(f"Keywords: {', '.join(JOB_SEARCH_KEYWORDS)}")
        logger.info(f"Location: {JOB_SEARCH_LOCATION}")
        
        scraper = MultiSourceJobScraper()
        jobs = scraper.search_all_sources(
            keywords=JOB_SEARCH_KEYWORDS,
            location=JOB_SEARCH_LOCATION,
            max_jobs=TOTAL_MAX_JOBS
        )
        
        if not jobs:
            logger.warning("⚠️ No jobs found. Check your internet connection or keywords.")
            return
        
        logger.info(f"✓ Collected {len(jobs)} jobs for analysis")
        
        # ========================================
        # STEP 4: MATCH JOBS TO PROFILE
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 4: INTELLIGENT JOB MATCHING")
        logger.info("="*80)
        
        matcher = IntelligentJobMatcher()
        match_results = []
        
        for idx, job in enumerate(jobs, 1):
            try:
                match_result = matcher.match_with_intelligent_insights(
                    resume_profile=resume_profile,
                    job=job
                )
                match_results.append(match_result)
                
                # Progress indicator
                if idx % 5 == 0 or idx == len(jobs):
                    logger.info(f"  Progress: {idx}/{len(jobs)} jobs analyzed...")
            
            except Exception as e:
                logger.error(f"  Error matching job {idx}: {e}")
                continue
        
        # Sort by match score
        match_results.sort(key=lambda x: x['overall_score'], reverse=True)
        logger.info(f"✓ Successfully matched {len(match_results)} jobs")
        
        # ========================================
        # STEP 5: ANALYZE SKILL GAPS
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 5: SKILL GAP ANALYSIS")
        logger.info("="*80)
        
        gap_analyzer = SkillGapAnalyzer()
        gap_analysis = gap_analyzer.analyze_gaps(
            resume_profile=resume_profile,
            match_results=match_results
        )
        
        logger.info(f"✓ Identified {gap_analysis['total_unique_gaps']} unique skill gaps")
        logger.info(f"  🔴 Critical: {len(gap_analysis['critical_gaps'])}")
        logger.info(f"  🟡 High: {len(gap_analysis['high_priority_gaps'])}")
        logger.info(f"  🟢 Medium: {len(gap_analysis['medium_priority_gaps'])}")
        
        # ========================================
        # STEP 6: GENERATE LEARNING ROADMAP
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 6: GENERATING LEARNING ROADMAP")
        logger.info("="*80)
        
        roadmap_generator = LearningRoadmapGenerator()
        
        # Get top missing skills
        all_missing_skills = (
            gap_analysis['critical_gaps'] +
            gap_analysis['high_priority_gaps'][:5] +
            gap_analysis['medium_priority_gaps'][:3]
        )
        
        learning_roadmap = roadmap_generator.create_personalized_roadmap(
            missing_skills=all_missing_skills,
            career_focus=resume_profile.get('career_level', 'data_scientist')
        )
        
        logger.info(f"✓ Learning roadmap created")
        logger.info(f"  📚 Skills to learn: {learning_roadmap['total_skills']}")
        logger.info(f"  ⏱️  Estimated time: {learning_roadmap['total_estimated_time']}")
        
        # ========================================
        # STEP 7: GENERATE COMPREHENSIVE REPORTS
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 7: GENERATING REPORTS")
        logger.info("="*80)
        
        report_gen = ReportGenerator(output_dir=OUTPUT_DIR)
        
        # Generate all reports
        report_paths = report_gen.generate_all_reports(
            resume_profile=resume_profile,
            match_results=match_results,
            gap_analysis=gap_analysis,
            learning_roadmap=learning_roadmap
        )
        
        for report_type, path in report_paths.items():
            logger.info(f"  ✓ {report_type}: {path.name}")
        
        # ========================================
        # STEP 8: DISPLAY SUMMARY
        # ========================================
        print_summary(
            resume_profile=resume_profile,
            match_results=match_results,
            gap_analysis=gap_analysis,
            learning_roadmap=learning_roadmap,
            report_paths=report_paths
        )
        
        # ========================================
        # SUCCESS!
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("✅ ANALYSIS COMPLETE!")
        logger.info("="*80)
        logger.info(f"\n📁 All reports saved to: {OUTPUT_DIR.resolve()}\n")
        
        logger.info("💡 NEXT STEPS:")
        logger.info("  1. Open 'HIGH_PRIORITY_APPLY_NOW_*.csv' for immediate opportunities")
        logger.info("  2. Review 'SKILL_GAPS_LEARNING_ROADMAP_*.csv' for learning plan")
        logger.info("  3. Check 'COMPLETE_ANALYSIS_*.json' for detailed insights")
        logger.info("\n" + "="*80 + "\n")
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Analysis interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"\n❌ Critical error: {e}", exc_info=True)
        logger.error("Check resume_analyzer.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()