"""
Smart Cover Letter Generator
Uses Llama 3.3 to write narrative-driven, value-focused cover letters.
Auto-adapts tone based on the role and emphasizes 'Problem-Solution' logic.
"""

import os
import re
from typing import Dict, List, Any
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
        # ✅ UPGRADE: Use the 70B model for nuanced writing
        self.model = "llama-3.3-70b-versatile"
        
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)

    def _extract_candidate_details(self, profile: Dict) -> Dict:
        """Smart extraction of candidate details."""
        contact = profile.get('contact_info', {})
        
        # 1. Try to find a name in the resume text if not explicitly parsed
        # This is a basic fallback; usually, the parser should provide this.
        name = contact.get('name', "Candidate") 
        if name == "Candidate":
             # Sometimes name is in the first line of the raw text, but we'll stick to a safe placeholder
             # to avoid embarrassing "Dear Hiring Manager, I am [Wrong Name]" errors.
             name = "[Your Name]"

        return {
            'name': name,
            'email': contact.get('email', '[Your Email]'),
            'phone': contact.get('phone', '[Your Phone]'),
            'linkedin': contact.get('linkedin', ''),
            'github': contact.get('github', '')
        }

    def _determine_tone(self, job_title: str, company: str) -> str:
        """
        Heuristic to decide if the letter should be Corporate or Startup-style.
        """
        job_lower = job_title.lower()
        if any(x in job_lower for x in ['manager', 'director', 'vp', 'executive', 'consultant', 'analyst']):
            return "Professional, Confident, and Results-Oriented"
        elif any(x in job_lower for x in ['ninja', 'hacker', 'guru', 'lead', 'senior', 'startup']):
            return "Passionate, Innovative, and Direct"
        else:
            return "Professional yet Enthusiastic"

    def generate_cover_letter(self, resume_profile: Dict, job_match: Dict) -> str:
        """
        Generates a highly personalized cover letter.
        """
        # 1. Context Setup
        job_title = job_match.get('job_title', 'Position')
        company = job_match.get('company', 'the company')
        
        # 2. Candidate Context
        candidate = self._extract_candidate_details(resume_profile)
        years_exp = resume_profile.get('experience', {}).get('total_years', 0)
        
        # 3. Intelligent Skill Selection
        # Prioritize "Matched" skills (what they want) over just "My strengths"
        matched_data = job_match.get('skill_match', {}).get('matched_required', [])
        
        # Extract just the skill names
        top_matched = [m['skill'] for m in matched_data[:4]]
        
        # If we don't have enough matches, pad with candidate strengths
        if len(top_matched) < 3:
            strengths = resume_profile.get('strengths', [])
            # Clean up strength strings if they are sentences
            clean_strengths = [s.replace("Strong background in ", "") for s in strengths[:2]]
            top_matched.extend(clean_strengths)
            
        skills_str = ", ".join(top_matched)
        
        # 4. Fallback Check
        if not self.client:
            return self._fallback_template(candidate, job_title, company, skills_str)

        logger.info(f"  ✍️ AI drafting 'Smart' cover letter for {company}...")

        # 5. The "Smart" Prompt
        # We instruct the AI to use the "T-Shape" approach: Broad value + Deep expertise.
        tone_instruction = self._determine_tone(job_title, company)
        
        prompt = f"""
        You are an expert Career Strategist and Copywriter. 
        Write a cover letter for the following scenario.

        **CANDIDATE PROFILE:**
        - Name: {candidate['name']}
        - Experience: {years_exp} years
        - Key Technical Assets: {skills_str}
        - Contact: {candidate['email']} | {candidate['phone']}

        **TARGET ROLE:**
        - Job Title: {job_title}
        - Company: {company}
        
        **WRITING INSTRUCTIONS:**
        1. **Tone:** {tone_instruction}.
        2. **The Hook:** Do NOT start with "I am writing to apply". Start with a strong statement about the candidate's value or passion for the industry.
        3. **The 'Why':** Connect the candidate's {years_exp} years of experience specifically to solving problems using {skills_str}.
        4. **Structure:**
           - Paragraph 1: The Hook & Introduction.
           - Paragraph 2: The "Meat" (Technical achievements using the listed skills).
           - Paragraph 3: Cultural Fit & Soft Skills.
           - Paragraph 4: Call to Action (Confident closing).
        5. **Length:** Concise (Under 250 words).
        6. **Formatting:** Return only the body of the letter (No subject line needed, I will handle that).
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a world-class professional resume writer."},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=0.7, # Balanced creativity
                max_tokens=600
            )
            
            content = chat_completion.choices[0].message.content
            
            # Post-process: Remove markdown code blocks if AI added them
            content = re.sub(r'```.*?', '', content, flags=re.DOTALL).strip()
            
            # Add header/footer if AI didn't provide them nicely
            final_letter = f"""
{candidate['name']}
{candidate['email']} | {candidate['phone']}

Date: [Current Date]

Hiring Manager
{company}

Re: Application for {job_title}

{content}

Sincerely,

{candidate['name']}
"""
            return final_letter

        except Exception as e:
            logger.error(f"GenAI Error: {e}")
            return self._fallback_template(candidate, job_title, company, skills_str)

    def _fallback_template(self, cand: Dict, title: str, company: str, skills: str) -> str:
        """Robust fallback template."""
        return f"""
{cand['name']}
{cand['email']} | {cand['phone']}

Hiring Manager
{company}

Re: Application for {title}

Dear Hiring Team,

I am writing to express my enthusiasm for the {title} position at {company}. As a professional with experience in {skills}, I have long admired {company}'s work and see this role as a perfect intersection of my technical skills and professional goals.

In my previous experience, I have honed my abilities in {skills.split(',')[0] if skills else 'software development'}, consistently delivering robust solutions. I am eager to bring this technical rigor to your team.

I am confident that my background makes me a strong candidate for this role. I look forward to the possibility of discussing how I can contribute to {company}'s success.

Sincerely,

{cand['name']}
"""