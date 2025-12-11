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
                roadmap = roadmap_gen.create_personalized_roadmap(
                            missing_skills=skills_to_learn, 
                            resume_profile=profile
                        )
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
    st.header("👤 Your Professional Profile")
    
    # === AI-GENERATED SUMMARY ===
    if profile.get('profile_summary'):
        st.info(f"**🎯 AI Analysis**\n\n{profile['profile_summary']}")
    
    st.markdown("###")  # Spacer
    # Top Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1: 
        career_level = profile.get('career_level', 'N/A')
        career_stage = profile.get('career_stage', '')
        st.metric("Career Level", career_level, delta=career_stage, delta_color="off")
    
    with col2:
        exp = profile.get('experience', {})
        years = exp.get('total_years', 0) if isinstance(exp, dict) else 0
        st.metric("Experience", f"{years} Year{'s' if years != 1 else ''}")
    
    with col3: 
        total_skills = profile.get('total_skills', 0)
        st.metric("Skills Identified", total_skills)
    
    with col4: 
        jobs_count = len(matches) if matches else 0
        st.metric("Jobs Analyzed", jobs_count)

    st.divider()
    if profile.get('skill_diversity'):
        diversity = profile['skill_diversity']
        
        st.subheader("🎨 Skill Profile Analysis")
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.markdown(f"""
            **Profile Type:** {diversity.get('profile_type', 'N/A')}
            
            **Analysis:**
            - Total Skills: {diversity.get('total_skills', 0)}
            - Skill Categories: {diversity.get('num_categories', 0)}
            - Avg Skills per Category: {diversity.get('avg_skills_per_category', 0)}
            - Strongest Domain: {diversity.get('strongest_category', 'N/A')}
            
            **Insight:** {diversity.get('recommendation', 'Continue developing your skillset.')}
            """)
        
        with col_b:
            # Visual indicator
            profile_type = diversity.get('profile_type', '')
            if 'Full-Stack' in profile_type or 'Generalist' in profile_type:
                st.success("🌐 **Full-Stack Profile**\nBroad technical expertise")
            elif 'Specialist' in profile_type or 'Expert' in profile_type:
                st.info("🎯 **Specialist Profile**\nDeep domain expertise")
            elif 'Balanced' in profile_type:
                st.success("⚖️ **Balanced Profile**\nGood breadth & depth")
            else:
                st.warning("🌱 **Growing Profile**\nBuilding foundation")
    
    st.divider()
    
    # === STRENGTHS & ACHIEVEMENTS ===
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("💪 Key Strengths")
        if profile.get('strengths'):
            for idx, strength in enumerate(profile['strengths'], 1):
                st.markdown(f"{idx}. {strength}")
        else:
            st.info("Continue building your professional portfolio")
    
    with col_right:
        st.subheader("🏆 Achievements Detected")
        achievements = profile.get('achievements', [])
        if achievements:
            metric_achievements = [a for a in achievements if 'metric' in a]
            recognition_achievements = [a for a in achievements if 'type' == 'recognition']
            
            st.metric("Quantifiable Results", len(metric_achievements))
            st.metric("Recognitions", len(recognition_achievements))
            
            # Show top 3 achievements
            if metric_achievements:
                with st.expander("📊 View Top Achievements"):
                    for i, achievement in enumerate(metric_achievements[:3], 1):
                        st.markdown(f"**{i}.** {achievement.get('metric', 'N/A')}")
                        st.caption(achievement.get('context', '')[:150] + "...")
        else:
            st.info("Add quantifiable achievements to strengthen your resume (e.g., 'Increased performance by 40%')")
    
    st.divider()
    
    # === CONTACT & DIGITAL PRESENCE ===
    st.subheader("📞 Contact & Digital Presence")
    
    contact_col1, contact_col2, contact_col3 = st.columns(3)
    
    contact_info = profile.get('contact_info', {})
    
    with contact_col1:
        email = contact_info.get('email')
        if email:
            st.markdown(f"**Email:** {email}")
        else:
            st.caption("No email detected")
    
    with contact_col2:
        phone = contact_info.get('phone')
        if phone:
            st.markdown(f"**Phone:** {phone}")
        else:
            st.caption("No phone detected")
    
    with contact_col3:
        links = contact_info.get('links', [])
        if links:
            st.markdown("**Links:**")
            for link in links:
                link_type = link.get('type', 'Link')
                link_url = link.get('url', '#')
                st.markdown(f"- [{link_type}]({link_url})")
        else:
            st.caption("No portfolio links detected")
    
    st.divider()
    
    # === RECOMMENDATIONS ===
    recommendations = profile.get('recommendations', [])
    if recommendations:
        st.subheader("💡 Personalized Recommendations")
        
        for rec in recommendations:
            priority = rec.get('priority', 'Medium')
            category = rec.get('category', 'General')
            suggestion = rec.get('suggestion', '')
            reasoning = rec.get('reasoning', '')
            
            # Color-code by priority
            if priority == 'High':
                st.error(f"**🔴 {priority} Priority - {category}**")
            elif priority == 'Medium':
                st.warning(f"**🟡 {priority} Priority - {category}**")
            else:
                st.info(f"**🟢 {priority} Priority - {category}**")
            
            st.markdown(f"**Suggestion:** {suggestion}")
            st.caption(f"*Why?* {reasoning}")
            st.markdown("")  # Spacer

    st.markdown("###")  # Spacer

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Analysis", 
        "💼 Job Matches", 
        "🎓 Learning Roadmap", 
        "✍️ AI Cover Letter",
        "🎤 Mock Interview"
    ])
    
    # === TAB 1: PROFILE ===
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Your Skill Distribution")
            if os.path.exists("output/visual_skill_radar.png"):
                st.image("output/visual_skill_radar.png", caption="Skill Radar Chart")
            else:
                st.info("Not enough data for Radar Chart.")
                
        with col2:
            st.subheader("Market Demand Heatmap")
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
    
    # === TAB 5: ENHANCED MOCK INTERVIEW ===
    with tab5:
        st.header("🎤 AI Mock Interviewer")
        st.caption("Realistic, role-specific interview simulation with customizable focus and difficulty")
        
        active_key = groq_key if groq_key else os.environ.get("GROQ_API_KEY")
        if not active_key:
            st.warning("⚠️ Please enter your Groq API Key.")
            st.stop() 

        # State Management
        if 'interview_active' not in st.session_state: 
            st.session_state.interview_active = False
        if 'interview_history' not in st.session_state: 
            st.session_state.interview_history = []
        if 'last_processed_audio' not in st.session_state: 
            st.session_state.last_processed_audio = None
        if 'current_audio_path' not in st.session_state: 
            st.session_state.current_audio_path = None
        if 'selected_interview_job' not in st.session_state:
            st.session_state.selected_interview_job = None
        if 'interview_config' not in st.session_state:
            st.session_state.interview_config = {
                'focus': 'balanced',
                'difficulty': 'medium'
            }
        
        try:
            interviewer = MockInterviewer(api_key=active_key)
        except Exception as e:
            st.error(f"Init Error: {e}")
            st.stop()

        # Helper: Cleanup
        def cleanup_old_audio():
            if st.session_state.current_audio_path and os.path.exists(st.session_state.current_audio_path):
                try:
                    os.remove(st.session_state.current_audio_path)
                except:
                    pass

        # --- SCENE 1: CONFIGURATION & START ---
        if not st.session_state.interview_active:
            
            # === JOB SELECTION ===
            st.subheader("📋 Step 1: Select Target Position")
            
            if matches and len(matches) > 0:
                # Create job options
                job_options = {}
                for idx, m in enumerate(matches[:10]):
                    job_label = f"{m.get('company', 'Unknown')} - {m.get('job_title', 'Position')}"
                    match_score = m.get('overall_score', 0)
                    job_options[job_label] = {
                        'company': m.get('company', ''),
                        'title': m.get('job_title', ''),
                        'description': m.get('raw_text', '')[:2000],
                        'score': match_score
                    }
                
                # Add generic option
                job_options["🎯 AI Engineer (Generic Interview)"] = {
                    'company': '',
                    'title': 'AI Engineer',
                    'description': 'General AI/ML engineering interview',
                    'score': 0
                }
                
                selected_job_label = st.selectbox(
                    "Choose a position:",
                    list(job_options.keys()),
                    help="Select a specific job for tailored interview questions"
                )
                
                selected_job_data = job_options[selected_job_label]
                
                # Display job details
                if selected_job_data['company']:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info(f"**Company:** {selected_job_data['company']}  \n**Role:** {selected_job_data['title']}")
                    with col2:
                        st.metric("Match", f"{selected_job_data['score']:.0%}")
            else:
                st.info("💡 No job matches found. Starting with generic AI Engineer interview.")
                selected_job_data = {
                    'company': '',
                    'title': 'AI Engineer',
                    'description': 'General AI/ML engineering interview',
                    'score': 0
                }
            
            st.divider()
            
            # === INTERVIEW CONFIGURATION ===
            st.subheader("⚙️ Step 2: Configure Interview Settings")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Interview Focus**")
                focus_option = st.radio(
                    "Select primary focus:",
                    options=["balanced", "behavioral", "technical"],
                    format_func=lambda x: {
                        "balanced": "⚖️ Balanced (50% Technical / 50% Behavioral)",
                        "behavioral": "💬 Behavioral (80% Behavioral / 20% Technical)",
                        "technical": "💻 Technical (90% Technical / 10% Behavioral)"
                    }[x],
                    help="Choose what aspect of the interview to emphasize",
                    key="focus_radio"
                )
                
                # Description
                focus_descriptions = {
                    "balanced": "Alternates between technical and behavioral questions. Tests both hard and soft skills.",
                    "behavioral": "Focuses on leadership, teamwork, communication, and past experiences. Great for management roles.",
                    "technical": "Deep technical deep-dives into ML algorithms, system design, and coding. For IC roles."
                }
                st.caption(focus_descriptions[focus_option])
            
            with col_b:
                st.markdown("**Difficulty Level**")
                difficulty_option = st.radio(
                    "Select experience level:",
                    options=["entry", "medium", "senior", "staff"],
                    format_func=lambda x: {
                        "entry": "🌱 Entry Level (0-2 years)",
                        "medium": "🚀 Mid Level (2-5 years)",
                        "senior": "⭐ Senior (5-10 years)",
                        "staff": "👑 Staff/Principal (10+ years)"
                    }[x],
                    help="Match your current experience level",
                    key="difficulty_radio"
                )
                
                # Description
                difficulty_descriptions = {
                    "entry": "Fundamentals, basic concepts, willingness to learn. Academic projects.",
                    "medium": "Practical implementation, debugging, system design basics. Real-world projects.",
                    "senior": "Architecture, scalability, trade-offs. Leadership and mentoring.",
                    "staff": "Multi-system architecture, org-wide impact. Strategic vision."
                }
                st.caption(difficulty_descriptions[difficulty_option])
            
            # Save config
            st.session_state.interview_config = {
                'focus': focus_option,
                'difficulty': difficulty_option
            }
            
            st.divider()
            
            # === INTERVIEW PREVIEW ===
            st.subheader("📖 What to Expect")
            
            preview_col1, preview_col2 = st.columns(2)
            
            with preview_col1:
                st.markdown("**Interview Structure:**")
                if difficulty_option == "entry":
                    st.markdown("""
                    - Rounds 1-2: Introduction & basic concepts
                    - Rounds 3-5: Fundamental technical/behavioral
                    - Rounds 6-8: Applied scenarios
                    - Rounds 9+: Learning mindset questions
                    """)
                elif difficulty_option in ["senior", "staff"]:
                    st.markdown("""
                    - Rounds 1-2: Background & leadership intro
                    - Rounds 3-5: System design & architecture
                    - Rounds 6-8: Strategic decisions & trade-offs
                    - Rounds 9+: Org-level impact & vision
                    """)
                else:
                    st.markdown("""
                    - Rounds 1-2: Warm-up & introduction
                    - Rounds 3-5: Core technical/behavioral
                    - Rounds 6-8: Problem-solving deep-dive
                    - Rounds 9+: Advanced scenarios
                    """)
            
            with preview_col2:
                st.markdown("**Sample Topics:**")
                if focus_option == "behavioral":
                    st.markdown("""
                    - Leadership & team collaboration
                    - Conflict resolution
                    - Project management
                    - Stakeholder communication
                    - Learning from failure
                    """)
                elif focus_option == "technical":
                    st.markdown("""
                    - ML algorithms & deep learning
                    - System design & architecture
                    - MLOps & deployment
                    - Code optimization
                    - Real-world debugging
                    """)
                else:
                    st.markdown("""
                    - Technical problem-solving
                    - Team collaboration
                    - System design basics
                    - Communication skills
                    - Project delivery
                    """)
            
            st.divider()
            
            # === START BUTTON ===
            st.info("💡 **Pro Tip:** Have specific examples from your experience ready. Use the STAR method for behavioral questions (Situation, Task, Action, Result).")
            
            if st.button("🚀 Start Interview Session", type="primary", use_container_width=True):
                st.session_state.interview_active = True
                st.session_state.selected_interview_job = selected_job_data
                
                with st.spinner("Initializing AI interviewer..."):
                    # Generate personalized greeting
                    greeting = interviewer.generate_initial_greeting(
                        target_role=selected_job_data['title'],
                        company_name=selected_job_data['company'],
                        job_description=selected_job_data['description'],
                        interview_focus=st.session_state.interview_config['focus'],
                        difficulty=st.session_state.interview_config['difficulty']
                    )
                    
                    st.session_state.interview_history = [{
                        "role": "assistant", 
                        "content": greeting['question'],
                        "sample_answer": greeting['sample_answer']
                    }]
                    
                    # Generate audio
                    cleanup_old_audio()
                    new_path = interviewer.text_to_speech(greeting['question'])
                    
                    if new_path:
                        st.session_state.current_audio_path = new_path
                    else:
                        st.warning("Audio generation had issues, but interview will continue.")
                
                st.rerun()

        # --- SCENE 2: ACTIVE INTERVIEW ---
        else:
            # ✅ FIX: Add null safety checks
            job_context = st.session_state.selected_interview_job
            config = st.session_state.interview_config
            
            # ✅ FIX: Provide default values if job_context is None
            if job_context is None:
                job_context = {
                    'company': '',
                    'title': 'AI Engineer',
                    'description': 'General AI/ML engineering interview',
                    'score': 0
                }
                st.session_state.selected_interview_job = job_context
            
            # ✅ FIX: Provide default config if None
            if config is None:
                config = {
                    'focus': 'balanced',
                    'difficulty': 'medium'
                }
                st.session_state.interview_config = config
            
            # === HEADER ===
            if job_context.get('company'):
                st.info(f"🎯 **Interviewing for**: {job_context['title']} at {job_context['company']}")
            else:
                st.info(f"🎯 **Position**: {job_context.get('title', 'AI Engineer')} (Generic Interview)")
            
            # Show config badges
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                focus_emoji = {"balanced": "⚖️", "behavioral": "💬", "technical": "💻"}
                current_focus = config.get('focus', 'balanced')
                st.caption(f"{focus_emoji.get(current_focus, '⚖️')} Focus: **{current_focus.title()}**")
            with col_info2:
                diff_emoji = {"entry": "🌱", "medium": "🚀", "senior": "⭐", "staff": "👑"}
                current_diff = config.get('difficulty', 'medium')
                st.caption(f"{diff_emoji.get(current_diff, '🚀')} Level: **{current_diff.title()}**")
            with col_info3:
                round_num = len(st.session_state.interview_history) // 2 + 1
                st.caption(f"🔴 **Round {round_num}**")
            
            st.divider()
            
            # === TOOLBAR ===
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a: 
                st.caption("🔴 Live Session Active")
            with col_b:
                if st.button("🔄 Restart", help="Keep settings, restart conversation"):
                    cleanup_old_audio()
                    st.session_state.interview_history = []
                    st.session_state.last_processed_audio = None
                    st.session_state.current_audio_path = None
                    
                    # Regenerate greeting
                    greeting = interviewer.generate_initial_greeting(
                        target_role=job_context.get('title', 'AI Engineer'),
                        company_name=job_context.get('company', ''),
                        job_description=job_context.get('description', ''),
                        interview_focus=config.get('focus', 'balanced'),
                        difficulty=config.get('difficulty', 'medium')
                    )
                    st.session_state.interview_history = [{
                        "role": "assistant", 
                        "content": greeting['question'],
                        "sample_answer": greeting['sample_answer']
                    }]
                    new_path = interviewer.text_to_speech(greeting['question'])
                    st.session_state.current_audio_path = new_path
                    st.rerun()
            with col_c: 
                if st.button("❌ Exit"):
                    cleanup_old_audio()
                    st.session_state.interview_active = False
                    st.session_state.interview_history = []
                    st.session_state.current_audio_path = None
                    st.session_state.selected_interview_job = None
                    st.rerun()

            # === AUDIO PLAYER ===
            if st.session_state.current_audio_path and os.path.exists(st.session_state.current_audio_path):
                st.audio(
                    st.session_state.current_audio_path, 
                    format="audio/mp3", 
                    autoplay=True
                )

            # === CHAT HISTORY ===
            chat_container = st.container()
            with chat_container:
                for idx, message in enumerate(st.session_state.interview_history):
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                        
                        # Sample Answer
                        if message["role"] == "assistant" and "sample_answer" in message:
                            with st.expander("💡 View Sample Answer / Hint"):
                                st.info(message["sample_answer"])

            # === AUDIO INPUT ===
            if hasattr(st, 'audio_input'):
                audio_value = st.audio_input("🎙️ Record your answer")
            else:
                st.error("Please upgrade Streamlit to the latest version.")
                st.stop()

            # === PROCESS INPUT ===
            if audio_value is not None and audio_value != st.session_state.last_processed_audio:
                with st.spinner("🎧 Analyzing your response..."):
                    st.session_state.last_processed_audio = audio_value
                    
                    # 1. Transcribe
                    user_text = interviewer.transcribe_audio(audio_value)
                    
                    if user_text.startswith("Error"):
                        st.error(user_text)
                        st.stop()
                    
                    st.session_state.interview_history.append({
                        "role": "user", 
                        "content": user_text
                    })
                    
                    # 2. Get AI Response with full context
                    resume_data = st.session_state.get('resume_profile', {})
                    resume_context = st.session_state.get('resume_text', '')[:1500]
                    
                    ai_response = interviewer.get_ai_response(
                        history=st.session_state.interview_history, 
                        target_role=job_context.get('title', 'AI Engineer'),
                        company_name=job_context.get('company', ''),
                        job_description=job_context.get('description', ''),
                        resume_context=resume_context,
                        interview_focus=config.get('focus', 'balanced'),
                        difficulty=config.get('difficulty', 'medium')
                    )
                    
                    # 3. Save response
                    st.session_state.interview_history.append({
                        "role": "assistant", 
                        "content": ai_response['question'],
                        "sample_answer": ai_response['sample_answer']
                    })
                    
                    # 4. Generate audio
                    cleanup_old_audio()
                    new_path = interviewer.text_to_speech(ai_response['question'])
                    st.session_state.current_audio_path = new_path
                    
                    st.rerun()
                    
elif not uploaded_file:
    pass
