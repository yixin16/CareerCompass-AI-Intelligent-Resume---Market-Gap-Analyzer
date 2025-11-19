"""
Dynamic Learning Roadmap (GenAI Edition)
Uses Large Language Models (Groq/Llama3) to act as a Career Coach.
Generates specific time estimates, strategies, and project ideas for EACH skill.
"""

import os
import json
import re
from typing import Dict, List
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
        self.semantic_ai = SemanticMatcher() # Local BERT (Fallback & Categorization)
        
        # Setup GenAI (Groq)
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)

    def _ask_genai_for_advice(self, skill: str, category: str) -> Dict:
        """
        Uses LLM to generate specific advice for a single skill.
        """
        if not self.client:
            return None

        prompt = f"""
        Act as a Senior Technical Mentor. 
        I need a learning plan for the skill: "{skill}" (Category: {category}).
        
        Provide a response in this EXACT format (no other text):
        Complexity: [Low/Medium/High]
        Time: [e.g. 2 weeks, 3 months]
        Strategy: [One sentence strategic advice on how to learn this specific skill effectively]
        Project: [A specific, cool capstone project idea using this skill]
        """

        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.3, # Low temp for consistent formatting
                max_tokens=150
            )
            response_text = completion.choices[0].message.content
            
            # Parse the response
            data = {}
            for line in response_text.split('\n'):
                if "Complexity:" in line: data['diff'] = line.split(":")[1].strip()
                if "Time:" in line: data['time'] = line.split(":")[1].strip()
                if "Strategy:" in line: data['strategy'] = line.split(":")[1].strip()
                if "Project:" in line: data['project'] = line.split(":")[1].strip()
            
            # Validation
            if all(k in data for k in ['diff', 'time', 'strategy', 'project']):
                return data
        except Exception as e:
            logger.warning(f"  ⚠️ GenAI Roadmap Error for {skill}: {e}")
        
        return None

    def _get_fallback_advice(self, skill: str, category: str) -> Dict:
        """
        Semantic / Heuristic fallback if GenAI is offline.
        """
        # Basic heuristics based on category
        if category == "Programming":
            return {
                'diff': 'High', 'time': '8-10 weeks', 
                'strategy': 'Focus on syntax first, then DSA.', 
                'project': f'Build a CLI automation tool using {skill}.'
            }
        elif category == "Data & AI":
            return {
                'diff': 'High', 'time': '6-8 weeks',
                'strategy': 'Apply immediately on datasets, do not just watch videos.',
                'project': f'Analyze a Kaggle dataset using {skill}.'
            }
        else:
            return {
                'diff': 'Medium', 'time': '4 weeks',
                'strategy': 'Read official docs and build a hello-world app.',
                'project': f'Build a small component using {skill}.'
            }

    def create_personalized_roadmap(self, missing_skills: List[str], career_focus: str = "General") -> Dict:
        """
        Generates the roadmap using GenAI + Semantic Search.
        """
        logger.info(f"  🧠 AI Drafting Learning Roadmap for {len(missing_skills)} skills...")
        
        resources = []
        
        # Only process top 8 skills to save API time/limits if list is huge
        priority_skills = missing_skills[:8]
        
        for skill in priority_skills:
            # 1. Categorize using Local BERT (Fast & Accurate)
            category = self.semantic_ai.classify_category(skill)
            
            # 2. Get Advice (Try GenAI first, then Fallback)
            advice = self._ask_genai_for_advice(skill, category)
            if not advice:
                advice = self._get_fallback_advice(skill, category)
            
            # 3. Generate Standard Links (Reliable)
            q = quote_plus(skill)
            links = [
                {'name': 'Coursera', 'url': f"https://www.coursera.org/search?query={q}"},
                {'name': 'Udemy', 'url': f"https://www.udemy.com/courses/search/?q={q}"},
                {'name': 'YouTube', 'url': f"https://www.youtube.com/results?search_query={q}+tutorial"}
            ]
            
            # Add specific platform links
            if category == "Programming":
                links.insert(0, {'name': 'LeetCode', 'url': f"https://leetcode.com/problemset/?search={q}"})
            elif category == "Data & AI":
                links.insert(0, {'name': 'Kaggle', 'url': f"https://www.kaggle.com/search?q={q}"})

            resources.append({
                'skill': skill,
                'category': category,
                'difficulty': advice['diff'],
                'estimated_time': advice['time'],
                'strategy_tip': advice['strategy'],
                'recommended_project': advice['project'],
                'online_courses': links,
                'documentation': [],
                'practice_platforms': []
            })
            
            if self.client:
                logger.info(f"    ✓ GenAI generated plan for: {skill}")

        # Timeline Grouping
        timeline = {
            "Phase 1 (Foundations)": [r['skill'] for r in resources if 'High' in r['difficulty']],
            "Phase 2 (Application)": [r['skill'] for r in resources if 'Medium' in r['difficulty']],
            "Phase 3 (Specialization)": [r['skill'] for r in resources if 'Low' in r['difficulty']]
        }

        return {
            'career_focus': career_focus,
            'detailed_resources': resources,
            'total_skills': len(missing_skills),
            'timeline': timeline,
            'total_estimated_time': "Variable (Dependent on GenAI estimates)"
        }