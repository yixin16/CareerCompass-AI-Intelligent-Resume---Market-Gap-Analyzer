"""
Ultra-Intelligent CareerCompass AI - Main Entry Point
Features:
1. BERT Semantic Analysis
2. Search Engine Dorking (Scraper)
3. Vector Matching
4. Dynamic Roadmaps
5. Visual Analytics (Charts)
6. GenAI Cover Letters (Groq)
7. Detailed CSV/JSON Reporting
"""

import sys
import os
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
from core.cover_letter_generator import CoverLetterGenerator # AI Writer
from utils.report_generator import ReportGenerator           # CSV/JSON
from utils.visualizer import ReportVisualizer                # Charts
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
        # STEP 2: ANALYZE RESUME (AI POWERED)
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 2: ANALYZING RESUME WITH AI (BERT)")
        logger.info("="*80)
        
        analyzer = UltraIntelligentResumeAnalyzer()
        resume_profile = analyzer.analyze_resume(resume_text)
        
        if not resume_profile:
            logger.error("❌ Resume analysis failed")
            return
        
        logger.info(f"✓ Analysis complete")
        logger.info(f"  📊 Career Level: {resume_profile.get('career_level', 'N/A')}")
        logger.info(f"  💼 Experience: {resume_profile.get('experience', {}).get('total_years', 0)} years")
        logger.info(f"  🎯 Total Identified Skills: {resume_profile.get('total_skills', 0)}")
        
        # ========================================
        # STEP 3: SEARCH FOR JOBS (REAL-WORLD DORKING)
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
            logger.warning("⚠️ No jobs found. Check internet connection.")
            return
        
        logger.info(f"✓ Collected {len(jobs)} jobs for analysis")
        
        # ========================================
        # STEP 4: MATCH JOBS TO PROFILE (SEMANTIC)
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 4: INTELLIGENT SEMANTIC MATCHING")
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
                
                if idx % 5 == 0 or idx == len(jobs):
                    logger.info(f"  Progress: {idx}/{len(jobs)} jobs analyzed...")
            
            except Exception as e:
                logger.error(f"  Error matching job {idx}: {e}")
                continue
        
        # Sort by match score
        match_results.sort(key=lambda x: x['overall_score'], reverse=True)
        logger.info(f"✓ Successfully matched {len(match_results)} jobs using AI")
        
        # ========================================
        # STEP 5: ANALYZE SKILL GAPS
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 5: SEMANTIC GAP ANALYSIS")
        logger.info("="*80)
        
        gap_analyzer = SkillGapAnalyzer()
        gap_analysis = gap_analyzer.analyze_gaps(
            resume_profile=resume_profile,
            match_results=match_results
        )
        
        # Safe retrieval of gaps
        critical_gaps = gap_analysis.get('critical_gaps', [])
        medium_gaps = gap_analysis.get('medium_priority_gaps', [])
        
        logger.info(f"✓ Identified {gap_analysis.get('total_unique_gaps', 0)} unique skill clusters")
        logger.info(f"  🔴 Critical: {len(critical_gaps)}")
        logger.info(f"  🟢 Medium: {len(medium_gaps)}")
        
        # ========================================
        # STEP 6: GENERATE LEARNING ROADMAP
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 6: GENERATING DYNAMIC LEARNING ROADMAP")
        logger.info("="*80)
        
        roadmap_generator = LearningRoadmapGenerator()
        
        # Combine gaps for roadmap
        skills_to_learn = critical_gaps[:6] + medium_gaps[:4]
        
        learning_roadmap = roadmap_generator.create_personalized_roadmap(
            missing_skills=skills_to_learn,
            career_focus=resume_profile.get('career_level', 'Professional')
        )
        
        logger.info(f"✓ Roadmap created dynamically")
        logger.info(f"  📚 Skills mapped: {learning_roadmap.get('total_skills', 0)}")
        
        # ========================================
        # STEP 7: GENERATE VISUALS & COVER LETTERS
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 7: GENERATING VISUALS & AI ASSETS")
        logger.info("="*80)
        
        # 1. Visuals
        visualizer = ReportVisualizer(OUTPUT_DIR)
        try:
            visualizer.generate_skill_radar(resume_profile['skills_by_category'])
            visualizer.generate_market_wordcloud(jobs)
            logger.info(f"  ✓ Created charts in output folder")
        except Exception:
            pass

        # 2. AI Cover Letters
        writer = CoverLetterGenerator()
        logger.info("  ✍️ Generating cover letters for top 3 matches...")
        
        # Only generate for matches that are at least "Fair" (> 40%)
        viable_matches = [m for m in match_results if m['overall_score'] > 0.4][:3]
        
        for i, match in enumerate(viable_matches):
            try:
                # Pass the FULL resume profile so we can get contact info
                letter = writer.generate_cover_letter(resume_profile, match)
                
                company_safe = "".join(c for c in match['company'] if c.isalnum()).strip()
                filename = f"COVER_LETTER_{i+1}_{company_safe}.txt"
                
                with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(letter)
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to write letter {i+1}: {e}")

        # ========================================
        # STEP 8: GENERATE DATA REPORTS (RESTORED!)
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 8: FINALIZING CSV/JSON REPORTS")
        logger.info("="*80)
        
        # This is the logic that was missing!
        report_gen = ReportGenerator(output_dir=OUTPUT_DIR)
        
        report_paths = report_gen.generate_all_reports(
            resume_profile=resume_profile,
            match_results=match_results,
            gap_analysis=gap_analysis,
            learning_roadmap=learning_roadmap
        )
        
        for report_type, path in report_paths.items():
            logger.info(f"  ✓ {report_type.replace('_', ' ').title()}: {path.name}")
        
        # ========================================
        # SUMMARY & END
        # ========================================
        print_summary(
            resume_profile=resume_profile,
            match_results=match_results,
            gap_analysis=gap_analysis,
            learning_roadmap=learning_roadmap,
            report_paths=report_paths
        )
        
        logger.info("\n" + "="*80)
        logger.info("✅ ANALYSIS COMPLETE!")
        logger.info("="*80)
        logger.info(f"\n📁 All reports saved to: {OUTPUT_DIR.resolve()}\n")
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Analysis interrupted by user")
        sys.exit(0)
    
    except ImportError as ie:
        logger.error(f"\n❌ Missing Dependency: {ie}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Critical error: {e}", exc_info=True)
        logger.error("Check logs/resume_analyzer.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()