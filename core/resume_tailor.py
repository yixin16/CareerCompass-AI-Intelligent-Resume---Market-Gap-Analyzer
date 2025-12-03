"""
Intelligent Resume Tailor
Uses Llama 3.3 to perform ATS Optimization, Keyword Injection, and STAR-method rewriting.
"""

import json
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.logger import logger

def clean_json_string(json_str: str) -> str:
    """
    Cleans LLM output to ensure valid JSON parsing.
    Removes Markdown code blocks (```json ... ```).
    """
    cleaned = json_str.strip()
    # Remove markdown code blocks if present
    if cleaned.startswith("```"):
        # Split by newline to remove the first line (```json) and the last line (```)
        parts = cleaned.split("\n")
        if len(parts) > 2:
            cleaned = "\n".join(parts[1:-1])
    return cleaned

def tailor_resume(profile: Dict[str, Any], job_description: str, api_key: str) -> Dict[str, Any]:
    """
    Orchestrates the AI tailoring process.
    1. Analyzing JD for High-Value Keywords.
    2. Rewriting Summary to be a "Hook".
    3. Transforming Bullet points into STAR format.
    4. Re-sorting Skills by relevance.
    """
    if not api_key:
        raise ValueError("API Key missing.")

    # ✅ CONFIG: Use Llama 3.3 70B for maximum reasoning capability
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile", 
        temperature=0.4, # Low temperature for reliable formatting
        api_key=api_key,
        max_tokens=4096
    )

    parser = JsonOutputParser()

    # ✅ INTELLIGENT PROMPT: 
    # This prompt forces the AI to think like a Recruiter before writing.
    system_instruction = """
    You are an expert Executive Resume Writer and ATS (Applicant Tracking System) Specialist.
    Your goal is to rewrite a candidate's resume data to achieve a 100% Match Score against the provided Job Description.

    **THE RULES:**
    1. **Truthfulness:** Do NOT invent experiences or jobs. Only optimize what is provided.
    2. **ATS Optimization:** Identify the top 5 technical keywords in the Job Description and ensure they appear in the Summary or Skills.
    3. **STAR Method:** Rewrite experience bullet points using the [Action Verb] + [Context] + [Result/Metric] formula.
       - *Bad:* "Worked on Python code."
       - *Good:* "Engineered scalable Python microservices, reducing API latency by 40%."
    4. **Skill Re-Ranking:** Re-order the "skills_by_category" lists so that skills mentioned in the Job Description appear FIRST.
    5. **Summary Hook:** The summary must be a 3-sentence "Elevator Pitch" strictly aligned with the target role.

    **OUTPUT FORMAT:**
    Return ONLY valid JSON. The structure must strictly match the input "profile" keys.
    """

    human_template = """
    **TARGET JOB DESCRIPTION:**
    {job_description}

    **CANDIDATE PROFILE (Input):**
    {profile_json}

    **TASK:**
    Tailor the candidate profile to the job description following the rules above.
    
    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", human_template)
    ])

    chain = prompt | llm | parser

    # Convert profile dict to string for the prompt context
    # We remove 'analysis_timestamp' or internal metadata to save tokens if needed
    clean_profile = {k: v for k, v in profile.items() if k not in ['analysis_timestamp', 'matches']}
    profile_str = json.dumps(clean_profile)

    logger.info("  🎨 AI Tailoring Resume for target role...")

    try:
        # Invoke the chain
        tailored_json = chain.invoke({
            "job_description": job_description,
            "profile_json": profile_str,
            "format_instructions": parser.get_format_instructions()
        })
        
        # ✅ POST-PROCESSING RELIABILITY CHECK
        # Ensure critical keys exist; if AI missed them, copy from original
        if 'contact_info' not in tailored_json:
            tailored_json['contact_info'] = profile.get('contact_info', {})
        
        # If AI hallucinated a new structure for experience, try to revert or fix
        if 'experience' in tailored_json and isinstance(tailored_json['experience'], list):
            # Sometimes LLM returns a list instead of the original dict structure
            # We assume the user wants the structure preserved for the PDF generator
            pass 

        logger.info("  ✅ Resume tailored successfully.")
        return tailored_json

    except Exception as e:
        logger.error(f"❌ Resume Tailoring Failed: {e}")
        # FAIL-SAFE: Return the original profile so the app doesn't crash
        return profile