"""
AI Cover Letter Generator (Smart Edition)
Injects specific resume skills and contact details into the prompt
to ensure every letter is unique and hyper-personalized.
"""

import os
from typing import Dict, List
from utils.logger import logger

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class CoverLetterGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)

    def _extract_candidate_details(self, profile: Dict) -> Dict:
        """Helper to pull contact info from the analyzed profile."""
        contact = profile.get('contact_info', {})
        
        # Try to guess name from first line of text if not explicit, else generic
        # (Assuming the analyzer passed the full text or we use a placeholder)
        name = "Candidate" 
        
        return {
            'name': name,
            'email': contact.get('email', '[Email]'),
            'phone': contact.get('phone', '[Phone]'),
            'linkedin': contact.get('linkedin', ''),
            'github': contact.get('github', '')
        }

    def generate_cover_letter(self, resume_profile: Dict, job_match: Dict) -> str:
        """
        Generates a personalized cover letter using LLM with specific skill injection.
        """
        # 1. Get Job Details
        job_title = job_match.get('job_title', 'Position')
        company = job_match.get('company', 'Hiring Team')
        
        # 2. Get Candidate Details
        candidate = self._extract_candidate_details(resume_profile)
        
        # 3. Identify "Winning Skills" (Intersection of Resume & Job)
        matched_skills = [m['skill'] for m in job_match.get('skill_match', {}).get('matched_required', [])]
        top_skills = matched_skills[:4] if matched_skills else resume_profile.get('strengths', [])[:3]
        
        skills_str = ", ".join(top_skills)
        
        # 4. Fallback if no API
        if not self.client:
            return self._fallback_template(candidate, job_title, company, skills_str)

        logger.info(f"  ✍️ AI writing unique letter for {company} (Focus: {skills_str})...")

        # 5. Advanced Prompting
        prompt = f"""
        You are an expert career coach writing a cover letter for a job application.
        
        CANDIDATE INFO:
        Email: {candidate['email']} | Phone: {candidate['phone']}
        Top Relevant Skills for this specific job: {skills_str}
        Years of Exp: {resume_profile.get('experience', {}).get('total_years', 0)}
        
        JOB DETAILS:
        Role: {job_title}
        Company: {company}
        
        INSTRUCTIONS:
        1. Write a high-impact cover letter (max 200 words).
        2. OPENING: Mention the specific role and company enthusiastically.
        3. BODY: Explicitly mention how the candidate's experience with {skills_str} solves the company's needs.
        4. TONE: Professional, confident, but not robotic.
        5. FORMAT: Standard business letter format.
        6. SIGNATURE: Use the placeholders [Your Name].
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt},
                ],
                model="llama3-8b-8192",
                temperature=1.0, # Higher temperature = more creativity/variation
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"GenAI Error: {e}")
            return self._fallback_template(candidate, job_title, company, skills_str)

    def _fallback_template(self, cand: Dict, title: str, company: str, skills: str) -> str:
        """Dynamic template used if AI fails."""
        return f"""
From: {cand['email']}
To: Hiring Manager at {company}

Subject: Application for {title} - {cand['email']}

Dear Hiring Manager,

I am writing to express my strong interest in the {title} position at {company}. With my background in technology and my specific expertise in {skills}, I am confident in my ability to contribute immediately to your engineering team.

My experience aligns well with the requirements I read in your job description. I am particularly excited about the opportunity to apply my skills in {skills.split(',')[0] if skills else 'software development'} to solve real-world challenges at {company}.

I would welcome the opportunity to discuss how my background and technical skills would benefit your team. Thank you for your time and consideration.

Sincerely,

[Your Name]
{cand['phone']}
{cand['linkedin']}
"""