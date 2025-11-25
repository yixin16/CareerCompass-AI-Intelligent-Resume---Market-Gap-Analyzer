"""
CareerCompass AI - Web Interface
A Streamlit-based dashboard for the Resume Analyzer system.
"""

import os
from dotenv import load_dotenv

load_dotenv()
# 1. Suppress TensorFlow/Keras Warnings immediately
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
default_key = os.getenv("GROQ_API_KEY", "")

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
    from core.resume_tailor import tailor_resume
    from core.agent_graph import init_agent_graph 
    from core.interviewer import MockInterviewer
    from utils.visualizer import ReportVisualizer
    from utils.pdf_generator import create_resume_pdf
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

# --- SESSION STATE INITIALIZATION ---
if 'analysis_complete' not in st.session_state:
    st.session_state['analysis_complete'] = False
if 'resume_profile' not in st.session_state:
    st.session_state['resume_profile'] = None

if not default_key and "GROQ_API_KEY" in st.secrets:
    default_key = st.secrets["GROQ_API_KEY"]
    
# NEW: Add these for the Mock Interviewer
if 'interview_history' not in st.session_state:
    st.session_state['interview_history'] = []

if 'last_audio' not in st.session_state:
    st.session_state['last_audio'] = None

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
    # We set 'value' to default_key. 
    # If the key exists in .env, it will be pre-filled (masked).
    # If not, it will be empty.
        groq_key = st.text_input(
            "Groq API Key", 
            value=default_key, 
            type="password", 
            help="Required for AI Analysis. Loaded from .env if available."
        )

        if groq_key:
            # Set the environment variable to whatever is in the box (auto or manual)
            os.environ["GROQ_API_KEY"] = groq_key
            
            # Optional: Show a subtle indicator of where the key came from
            if groq_key == default_key and default_key != "":
                st.caption("✅ Loaded from environment/config")
            else:
                st.caption("✅ Using manually entered key")
                
        else:
            st.warning("⚠️ Please enter an API Key to proceed.")

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Profile & Market", 
        "💼 Job Matches", 
        "🎓 Learning Roadmap", 
        "✍️ AI Cover Letter",
        "🎤 Mock Interview"
    ])
    
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
            # 1. Display DataFrame (Existing code)
            df_data = []
            for i, m in enumerate(matches):
                skill_match = m.get('skill_match', {})
                missing = skill_match.get('missing_required', [])
                df_data.append({
                    "ID": i, # Add ID for selection
                    "Score": f"{m.get('overall_score', 0):.0%}",
                    "Company": m.get('company', 'N/A'),
                    "Title": m.get('job_title', 'N/A'),
                    "Missing": ", ".join(missing[:3])
                })
            
            st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

            st.divider()

            # 2. Resume Tailoring Section
            st.subheader("🎨 AI Resume Tailor")
            
            # Select Job
            job_list = [f"{m['company']} - {m['job_title']}" for m in matches]
            selected_idx = st.selectbox("Select a job to tailor your resume for:", range(len(job_list)), format_func=lambda x: job_list[x])
            
            if st.button("✨ Generate Tailored Resume PDF"):
                target_job = matches[selected_idx]
                
                # API Key Check
                active_key = groq_key if groq_key else os.environ.get("GROQ_API_KEY")
                if not active_key:
                    st.error("API Key required.")
                    st.stop()

                with st.status("Processing...", expanded=True) as status:
                    status.write("📝 Rewriting resume content (Llama 3)...")
                    
                    # 1. Tailor Content
                    tailored_data = tailor_resume(
                        st.session_state['resume_profile'], 
                        # Pass a string representation of the job
                        f"{target_job['job_title']} at {target_job['company']}. Skills: {target_job.get('raw_text', '')}",
                        active_key
                    )
                    
                    status.write("📄 Rendering PDF...")
                    
                    # 2. Generate PDF
                    pdf_bytes = create_resume_pdf(tailored_data)
                    
                    status.update(label="Done!", state="complete", expanded=False)

                    # 3. Download Button
                    st.success(f"Resume tailored for {target_job['company']}!")
                    st.download_button(
                        label="📥 Download Tailored Resume (.pdf)",
                        data=pdf_bytes,
                        file_name=f"Resume_{target_job['company']}.pdf",
                        mime="application/pdf"
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
            
            if st.button("✨ Draft Cover Letter (Agentic Mode)", type="primary"):
        
                # Check Logic
                if not st.session_state.get('resume_text'):
                    st.error("Please analyze your resume first.")
                elif not groq_key and "GROQ_API_KEY" not in os.environ:
                    st.error("Please provide a Groq API Key in the sidebar.")
                else:
                    # Get the key (either from input or env)
                    active_key = groq_key if groq_key else os.environ.get("GROQ_API_KEY")
                    
                    selected_job = job_options[selected_job_name]
                    
                    with st.status("🤖 AI Agent Working...", expanded=True) as status:
                        
                        # 1. INITIALIZE THE GRAPH (The Fix)
                        status.write("⚙️ Spinning up AI Agents...")
                        try:
                            agent_app = init_agent_graph(active_key)
                        except Exception as e:
                            st.error(f"Failed to initialize AI: {e}")
                            st.stop()
                        
                        # 2. Setup Input State
                        initial_state = {
                            "company_name": selected_job.get('company', 'the company'),
                            "job_title": selected_job.get('job_title', 'the role'),
                            "job_description": "See matched skills context.", 
                            "resume_text": st.session_state['resume_text'],
                            "research_data": "",
                            "cover_letter": ""
                        }
                        
                        # 3. Run the Graph
                        status.write("🕵️ Researching Company Culture & News...")
                        result = agent_app.invoke(initial_state)
                        
                        status.write("✍️ Drafting Personalized Letter...")
                        final_letter = result['cover_letter']
                        
                        status.update(label="✅ Draft Complete!", state="complete", expanded=False)
                        
                        # 4. Display Result
                        st.subheader("Agent-Generated Letter")
                        st.caption(f"Incorporating research on: {result['company_name']}")
                        st.text_area("Edit your letter:", value=final_letter, height=500)
                        
                        st.download_button(
                            label="📥 Download .txt",
                            data=final_letter,
                            file_name="Agentic_Cover_Letter.txt",
                            mime="text/plain"
                        )
        else:
            st.warning("Please run analysis to find jobs first.")
    
    # === TAB 5: MOCK INTERVIEW ===
    with tab5:
        st.subheader("🎤 Voice-Enabled Technical Interviewer")
        st.caption("Practice answering questions out loud. The AI will listen, evaluate, and respond.")

        # Ensure API Key
        active_key = groq_key if groq_key else os.environ.get("GROQ_API_KEY")
        if not active_key:
            st.error("Please configure Groq API Key in sidebar first.")
            st.stop()

        interviewer = MockInterviewer(active_key)

        # 1. Start/Reset Button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Start New Session"):
                st.session_state['interview_history'] = []
                # Initial Greeting
                initial_msg = "Hello. I have reviewed your resume. Tell me about yourself and why you are a good fit for this role."
                st.session_state['interview_history'].append({"role": "assistant", "content": initial_msg})
                # Generate Audio for greeting
                audio_path = interviewer.text_to_speech(initial_msg)
                st.session_state['last_audio'] = audio_path
                st.rerun()

        # 2. Display Chat History
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state['interview_history']:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        # 3. Play Audio of last AI response
        if 'last_audio' in st.session_state and st.session_state['last_audio']:
            st.audio(st.session_state['last_audio'], format="audio/mp3", autoplay=True)

        # 4. Audio Input (The Mic)
        # Note: st.audio_input is available in Streamlit 1.40+
        audio_value = st.audio_input("Record your answer")

        if audio_value:
            # Process only if we haven't processed this specific audio yet
            # (Streamlit reruns on interaction, so we need to prevent loops if desired, 
            # but standard audio_input usually clears or handles state well)
            
            with st.spinner("👂 Listening & Transcribing..."):
                # A. Transcribe
                user_text = interviewer.transcribe_audio(audio_value)
                
                # Append User Message
                st.session_state['interview_history'].append({"role": "user", "content": user_text})
            
            with st.spinner("🧠 Thinking & Speaking..."):
                # B. Get AI Response
                ai_text = interviewer.get_ai_response(st.session_state['interview_history'])
                
                # Append AI Message
                st.session_state['interview_history'].append({"role": "assistant", "content": ai_text})
                
                # C. Convert to Speech
                audio_path = interviewer.text_to_speech(ai_text)
                st.session_state['last_audio'] = audio_path
                
                st.rerun()
                
elif not uploaded_file:
    # Sidebar hint handled in sidebar, showing empty state here
    pass