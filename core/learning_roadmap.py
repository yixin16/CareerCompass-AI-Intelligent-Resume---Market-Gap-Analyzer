"""
Dynamic Agentic Learning Roadmap
Uses Llama 3.3 to act as a Personalized Career Coach.
Generates context-aware strategies (Transfer Learning) based on existing skills.
"""

import os
import json
import re
from typing import Dict, List, Any, Union
from urllib.parse import quote_plus
from core.semantic_matcher import SemanticMatcher
from utils.logger import logger

# Try importing Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class LearningRoadmapGenerator:
    def __init__(self, api_key: str = None):
        self.semantic_ai = SemanticMatcher() 
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        
        # Use the high-reasoning model for curriculum design
        self.model = "llama-3.3-70b-versatile" 
        
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)

    def _generate_search_links(self, skill: str, category: str) -> List[Dict]:
        """
        Generates deterministic, high-quality resource links based on skill category.
        This ensures the user always has valid links even if AI hallucinates URLs.
        """
        q = quote_plus(skill)
        links = [
            {'name': 'Official Documentation', 'url': f"https://www.google.com/search?q={q}+documentation"},
            {'name': 'YouTube Crash Course', 'url': f"https://www.youtube.com/results?search_query={q}+crash+course"}
        ]
        
        if category == "Programming":
            links.append({'name': 'LeetCode Problems', 'url': f"https://leetcode.com/problemset/?search={q}"})
            links.append({'name': 'GitHub Projects', 'url': f"https://github.com/search?q={q}&type=repositories"})
        elif category == "Data & AI":
            links.append({'name': 'Kaggle Kernels', 'url': f"https://www.kaggle.com/search?q={q}"})
            links.append({'name': 'Papers With Code', 'url': f"https://paperswithcode.com/search?q_meta=&q={q}"})
        elif category == "Cloud & DevOps":
            links.append({'name': 'AWS/Azure Workshops', 'url': f"https://www.google.com/search?q={q}+workshops"})
            links.append({'name': 'Docker Hub Images', 'url': f"https://hub.docker.com/search?q={q}"})
        elif category == "Web & UI":
            links.append({'name': 'MDN Web Docs', 'url': f"https://developer.mozilla.org/en-US/search?q={q}"})
            
        return links

    def _get_fallback_roadmap(self, missing_skills: List[str]) -> List[Dict]:
        """Classic fallback if API is down or Key is missing."""
        resources = []
        for skill in missing_skills:
            cat = self.semantic_ai.classify_category(skill)
            resources.append({
                'skill': skill,
                'category': cat,
                'difficulty': "Medium",
                'estimated_time': "4 weeks",
                'strategy_tip': "Focus on documentation and building a small hello-world project.",
                'recommended_project': f"Build a simple CRUD application using {skill}",
                'online_courses': self._generate_search_links(skill, cat)
            })
        return resources

    def create_personalized_roadmap(self, missing_skills: List[str], resume_profile: Union[Dict, str]) -> Dict:
        """
        Agentic Workflow:
        1. Analyzes User's Current Stack (from resume_profile).
        2. Identifies gaps.
        3. Generates a curriculum that leverages *Transfer Learning*.
        """
        if not missing_skills:
            return {}

        # --- SAFETY CHECK: Input Validation ---
        # This prevents the 'AttributeError: str object has no attribute get'
        current_skills = []
        current_level = "Mid-Level"
        experience_years = 0

        if isinstance(resume_profile, dict):
            # Safe extraction logic
            current_level = resume_profile.get('career_level', 'Mid-Level')
            exp_data = resume_profile.get('experience', {})
            if isinstance(exp_data, dict):
                experience_years = exp_data.get('total_years', 0)
            
            # Extract skills list
            skills_data = resume_profile.get('skills_by_category', {})
            if isinstance(skills_data, dict):
                for cat, skills in skills_data.items():
                    # Handle if skills is a list of strings OR list of dicts
                    if isinstance(skills, list):
                        for s in skills[:5]: # Take top 5 from each category to limit tokens
                            if isinstance(s, dict): 
                                current_skills.append(s.get('skill', ''))
                            else: 
                                current_skills.append(str(s))
        else:
            logger.warning(f"⚠️ Roadmap received invalid profile type: {type(resume_profile)}. Proceeding with generic plan.")
        
        # Limit to top 6 critical skills to keep context window focused
        target_skills = missing_skills[:6]
        
        logger.info(f"  🧠 AI Architecting Roadmap for {len(target_skills)} skills...")

        # If no API key, use fallback
        if not self.client:
            return {
                'career_focus': "General Upskilling",
                'detailed_resources': self._get_fallback_roadmap(target_skills),
                'timeline': {}
            }

        # --- THE INTELLIGENT PROMPT ---
        system_prompt = (
            "You are an expert Technical Career Coach. "
            "Create a learning roadmap for a candidate. "
            "CRITICAL: Use TRANSFER LEARNING strategies. "
            "Example: If they know Java, teach Python by comparing syntax, not from scratch. "
            "Output strictly valid JSON."
        )

        user_prompt = f"""
        **Candidate Profile:**
        - Current Level: {current_level} ({experience_years} years exp)
        - Known Skills: {', '.join(current_skills[:25])}
        
        **Target Skills to Learn:**
        {', '.join(target_skills)}
        
        **Task:**
        Create a JSON plan for EACH target skill.
        
        **JSON Format:**
        {{
            "roadmap": [
                {{
                    "skill": "Skill Name",
                    "difficulty": "Low/Medium/High",
                    "estimated_time": "e.g. 2 weeks",
                    "strategy_tip": "Specific advice connecting their CURRENT skills to this NEW skill.",
                    "recommended_project": "A specific project idea combining old and new skills."
                }}
            ]
        }}
        """

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}, # Enforces JSON structure
                temperature=0.4,
                max_tokens=2048
            )
            
            response_text = completion.choices[0].message.content
            ai_data = json.loads(response_text)
            ai_roadmap = ai_data.get('roadmap', [])
            
            # Post-process: Add static links to the AI's wisdom
            final_resources = []
            for item in ai_roadmap:
                skill_name = item.get('skill', 'Unknown')
                
                # Double-check category locally for accurate linking
                cat = self.semantic_ai.classify_category(skill_name)
                
                # Merge AI wisdom with Deterministic Links
                item['category'] = cat
                item['online_courses'] = self._generate_search_links(skill_name, cat)
                final_resources.append(item)
            
            # Sort by difficulty for the timeline
            difficulty_order = {"Low": 1, "Medium": 2, "High": 3}
            final_resources.sort(key=lambda x: difficulty_order.get(x.get('difficulty', 'Medium'), 2))

            return {
                'career_focus': f"Transition to {current_level}+ Role",
                'detailed_resources': final_resources,
                'total_skills': len(target_skills)
            }

        except Exception as e:
            logger.error(f"GenAI Roadmap Failed: {e}")
            return {
                'career_focus': "Standard Path",
                'detailed_resources': self._get_fallback_roadmap(target_skills)
            }