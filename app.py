"""
CareerCompass AI - Web Interface
A Streamlit-based dashboard for the Resume Analyzer system.
"""

import os
# 1. Suppress TensorFlow/Keras Warnings immediately
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import streamlit as st
import pandas as pd
import time
from pathlib import Path
import shutil
import json

# --- IMPORT CORE MODULES ---
# Wrap imports in try/except to prevent crash if run from wrong directory
try:
    from core.resume_parser import ResumeParser
    from core.resume_analyzer import UltraIntelligentResumeAnalyzer
    from core.job_scraper import MultiSourceJobScraper
    from core.job_matcher import IntelligentJobMatcher
    from core.gap_analyzer import SkillGapAnalyzer
    from core.learning_roadmap import LearningRoadmapGenerator
    from core.cover_letter_generator import CoverLetterGenerator
    from utils.visualizer import ReportVisualizer
except ImportError as e:
    st.error(f"Error importing core modules: {e}")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CareerCompass AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    
    /* Fix for Metric Cards in Dark Mode */
    div[data-testid="stMetric"] {
        background-color: #262730; /* Dark grey background */
        border: 1px solid #464b59; /* Slightly lighter border */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    
    /* Force text color inside metrics to be readable just in case */
    div[data-testid="stMetric"] > div {
        color: #ffffff !important;
    }
    
    /* Button Styling */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        height: 3em;
    }
    
    /* Status Box */
    .success-box { padding: 1rem; background-color: #1e4030; color: #66ff99; border-radius: 5px; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---

def safe_json_parse(data):
    """
    Fixes 'AttributeError: str object has no attribute get'.
    Ensures the input is a Dictionary, even if the AI returned a JSON string.
    """
    if isinstance(data, dict):
        return data
    
    if isinstance(data, str):
        try:
            # Try to clean code blocks if LLM wrapped them in ```json ... ```
            clean_str = data.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str.split("```json")[1].split("```")[0]
            elif clean_str.startswith("```"):
                clean_str = clean_str.split("```")[1].split("```")[0]
            
            return json.loads(clean_str)
        except json.JSONDecodeError:
            st.warning("Warning: AI response was not valid JSON. Using partial data.")
            return {}
    
    return {}

def save_uploaded_file(uploadedfile):
    """Helper to save uploaded file to disk so parser can read it."""
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    file_path = temp_dir / uploadedfile.name
    with open(file_path, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return file_path

# --- SESSION STATE INITIALIZATION ---
if 'analysis_complete' not in st.session_state:
    st.session_state['analysis_complete'] = False
if 'resume_profile' not in st.session_state:
    st.session_state['resume_profile'] = None
if 'resume_text' not in st.session_state:
    st.session_state['resume_text'] = ""
if 'matches' not in st.session_state:
    st.session_state['matches'] = None
if 'roadmap' not in st.session_state:
    st.session_state['roadmap'] = None


# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("CareerCompass")
    st.markdown("**Intelligent Resume & Market Gap Analyzer**")
    st.divider()
    
    # 1. API Configuration
    with st.expander("⚙️ Configuration", expanded=True):
        groq_key = st.text_input("Groq API Key", type="password", help="Required for AI Analysis")
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

    # 2. Resume Upload
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload PDF/DOCX", type=['pdf', 'docx', 'txt'])
    
    # 3. Search Parameters
    st.subheader("2. Job Preferences")
    default_keywords = "Data Scientist, Machine Learning Engineer"
    keywords_input = st.text_area("Job Keywords", value=default_keywords, help="Comma separated job titles")
    location_input = st.text_input("Location", value="Malaysia")
    
    st.divider()
    run_btn = st.button("🚀 Run Analysis", type="primary")
    
    if st.session_state['analysis_complete']:
        st.success("✅ System Ready")

# --- MAIN LOGIC ---

# Header
if not st.session_state['analysis_complete']:
    st.title("👋 Welcome to Career Compass AI! \nYour Intelligent Resume & Market Gap Analyzer ")
    st.markdown("""
    Upload your resume to get started. This tool will:
    1. **Analyze** your skills and experience.
    2. **Scan** the live job market for opportunities.
    3. **Identify** skill gaps.
    4. **Generate** a learning roadmap and cover letters.
    """)

if run_btn:
    if not uploaded_file:
        st.error("Please upload a resume first.")
    elif not groq_key and "GROQ_API_KEY" not in os.environ:
         st.error("Please provide a Groq API Key in configuration.")
    else:
        # Clear previous results
        st.session_state['analysis_complete'] = False
        
        # --- PROCESSING STATUS ---
        with st.status("🚀 Starting Career Analysis...", expanded=True) as status:
            
            # --- PHASE 1: RESUME ANALYSIS ---
            status.write("📄 Reading file and parsing text...")
            file_path = save_uploaded_file(uploaded_file)
            resume_text = ResumeParser.extract_text(file_path)
            st.session_state['resume_text'] = resume_text
            
            status.write("🧠 AI analyzing skills & experience...")
            analyzer = UltraIntelligentResumeAnalyzer()
            # Get Raw Result
            raw_profile = analyzer.analyze_resume(resume_text)
            # FIX 1: SAFE PARSE TO DICT
            profile = safe_json_parse(raw_profile)
            st.session_state['resume_profile'] = profile
            
            # --- PHASE 2: JOB SEARCH ---
            status.write("🌍 Scouring the web for live jobs...")
            keywords = [k.strip() for k in keywords_input.split(',')]
            scraper = MultiSourceJobScraper()
            jobs = scraper.search_all_sources(keywords, location_input, max_jobs=10)
            status.write(f"✓ Found {len(jobs)} relevant positions")
            
            # --- PHASE 3: MATCHING ---
            if len(jobs) > 0:
                status.write("🤝 calculating match scores...")
                matcher = IntelligentJobMatcher()
                matches = []
                for job in jobs:
                    res = matcher.match_with_intelligent_insights(profile, job)
                    matches.append(res)
                
                matches.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
                st.session_state['matches'] = matches
                
                # --- PHASE 4: GAP ANALYSIS & ROADMAP ---
                status.write("🎓 Identifying skill gaps & building roadmap...")
                gap_analyzer = SkillGapAnalyzer()
                gaps = gap_analyzer.analyze_gaps(profile, matches)
                
                # Select top gaps
                skills_to_learn = gaps.get('critical_gaps', [])[:5] + gaps.get('medium_priority_gaps', [])[:3]
                
                roadmap_gen = LearningRoadmapGenerator()
                roadmap = roadmap_gen.create_personalized_roadmap(skills_to_learn, profile.get('career_level', 'Mid-Level'))
                st.session_state['roadmap'] = roadmap
                
                # --- VISUALS ---
                status.write("📊 Generating charts...")
                vis = ReportVisualizer(Path("output"))
                Path("output").mkdir(exist_ok=True)
                
                skills_cat = profile.get('skills_by_category', {})
                if skills_cat:
                    vis.generate_skill_radar(skills_cat)
                vis.generate_market_wordcloud(jobs)
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                st.session_state['analysis_complete'] = True
            else:
                status.update(label="❌ No jobs found. Try different keywords.", state="error")
                st.error("No jobs found for these keywords. Please try broader terms.")

# --- DASHBOARD DISPLAY ---

if st.session_state['analysis_complete']:
    profile = st.session_state['resume_profile']
    matches = st.session_state['matches']
    roadmap = st.session_state['roadmap']
    
    st.divider()
    
    # Top Stats Row
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Career Level", profile.get('career_level', 'N/A'))
    
    # Handle Experience safely
    exp = profile.get('experience', {})
    if isinstance(exp, dict):
        years = exp.get('total_years', 'N/A')
    else:
        years = "N/A"
    with c2: st.metric("Experience", f"{years} Years")
    
    with c3: st.metric("Skills Identified", profile.get('total_skills', 0))
    with c4: st.metric("Jobs Analyzed", len(matches) if matches else 0)

    st.markdown("###") # Spacer

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Profile & Market", "💼 Job Matches", "🎓 Learning Roadmap", "✍️ AI Cover Letter"])
    
    # === TAB 1: PROFILE ===
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Your Skill Profile")
            if os.path.exists("output/visual_skill_radar.png"):
                # FIX 2: Replaced use_column_width/use_container_width with standard streamlit approach
                st.image("output/visual_skill_radar.png", caption="Skill Distribution")
            else:
                st.info("Not enough data for Radar Chart.")
                
        with col2:
            st.subheader("Market Demand")
            if os.path.exists("output/visual_market_wordcloud.png"):
                st.image("output/visual_market_wordcloud.png", caption="Trending Keywords")
                
    # === TAB 2: JOB MATCHES ===
    with tab2:
        st.subheader("Top Opportunities")
        
        if matches:
            # Convert to DataFrame for display
            df_data = []
            for m in matches:
                # Safe access to nested keys
                skill_match = m.get('skill_match', {})
                missing = skill_match.get('missing_required', [])
                
                df_data.append({
                    "Score": f"{m.get('overall_score', 0):.0%}",
                    "Company": m.get('company', 'N/A'),
                    "Title": m.get('job_title', 'N/A'),
                    "Match Quality": m.get('match_quality', 'N/A'),
                    "Missing Skills": ", ".join(missing[:3]),
                    "URL": m.get('url', '#')
                })
            
            df = pd.DataFrame(df_data)
            
            # FIX 2: use_container_width deprecated -> width="stretch"
            st.dataframe(
                        df, 
                        column_config={
                            "URL": st.column_config.LinkColumn("Apply Link"),
                            "Score": st.column_config.ProgressColumn(
                                "Match Score", 
                                format="%.0f%%", 
                                min_value=0, 
                                max_value=1
                            ),
                            "Company": st.column_config.TextColumn("Company"),
                            "Missing Skills": st.column_config.ListColumn("Missing Skills") # Displays as tags
                        },
                        use_container_width=True, 
                        hide_index=True
                    )
        else:
            st.warning("No matches found.")
        
    # === TAB 3: ROADMAP ===
    with tab3:
        st.subheader("Your Personalized AI Curriculum")
        
        if roadmap and 'detailed_resources' in roadmap:
            for res in roadmap['detailed_resources']:
                with st.expander(f"📚 Learn: {res['skill']} ({res.get('estimated_time', 'N/A')})"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**Strategy:** {res.get('strategy_tip', '')}")
                        st.markdown(f"**Project Idea:** {res.get('recommended_project', '')}")
                    with c2:
                        st.info(f"**Difficulty:** {res.get('difficulty', 'Medium')}")
                        
                    st.markdown("**Top Resources:**")
                    for course in res.get('online_courses', [])[:2]:
                        st.markdown(f"- [{course['name']}]({course['url']})")
        else:
            st.info("Roadmap generation pending or failed.")

    # === TAB 4: COVER LETTER ===
    with tab4:
        st.subheader("AI Cover Letter Generator")
        
        if matches:
            # Dropdown to select job
            job_options = {f"{m['company']} - {m['job_title']}": m for m in matches[:10]}
            selected_job_name = st.selectbox("Select a Job to Apply for:", list(job_options.keys()))
            
            if st.button("✨ Draft Cover Letter", type="primary"):
                with st.spinner("Consulting LLM..."):
                    generator = CoverLetterGenerator()
                    selected_job = job_options[selected_job_name]
                    
                    # FIX 1 (CRITICAL): PASS THE PROFILE DICT, NOT TEXT STRING
                    # We use st.session_state['resume_profile'] instead of ['resume_text']
                    letter = generator.generate_cover_letter(
                        st.session_state['resume_profile'], 
                        selected_job
                    )
                    
                    st.text_area("Generated Letter:", value=letter, height=500)
                    
                    # Download Button
                    st.download_button(
                        label="📥 Download .txt",
                        data=letter,
                        file_name=f"Cover_Letter_{selected_job.get('company','Company')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please run analysis to find jobs first.")

elif not uploaded_file:
    # Sidebar hint handled in sidebar, showing empty state here
    pass