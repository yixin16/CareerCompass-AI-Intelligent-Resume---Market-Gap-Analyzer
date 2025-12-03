"""
Semantic Matcher & AI Classifier (Final Fixed Version)
Combines High-Performance Batch Processing with granular helper methods.
"""

import numpy as np
import torch
from typing import List, Tuple, Union, Dict
from sentence_transformers import SentenceTransformer, util
from utils.logger import logger

class SemanticMatcher:
    _instance = None
    
    # Anchors define the "Center" of a concept in vector space
    ANCHORS = {
        'technical_skill': [
            "software engineering skill", "programming language", "framework", 
            "cloud platform", "database technology", "machine learning tool", 
            "developer tool", "technical competency", "library", "api"
        ],
        'categories': {
            'Programming': "software development coding java python c++ code algorithms",
            'Data & AI': "machine learning artificial intelligence statistics data analysis sql pandas pytorch",
            'Web & UI': "frontend backend react angular html css javascript user interface ux",
            'Cloud & DevOps': "aws azure docker kubernetes ci/cd infrastructure server linux terraform",
            'Soft Skills': "leadership communication management agile collaboration team problem-solving"
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticMatcher, cls).__new__(cls)
            logger.info("🧠 Loading Neural Network (all-MiniLM-L6-v2)...")
            cls._instance.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # --- Pre-compute Embeddings for Speed ---
            logger.info("⚡ Pre-computing Vector Anchors...")
            
            # 1. Technical Skill Anchors
            cls._instance.skill_anchor_embs = cls._instance.model.encode(
                cls.ANCHORS['technical_skill'], convert_to_tensor=True
            )
            
            # 2. Category Anchors
            cls._instance.cat_keys = list(cls.ANCHORS['categories'].keys())
            cls._instance.cat_embs = cls._instance.model.encode(
                list(cls.ANCHORS['categories'].values()), convert_to_tensor=True
            )
            logger.info("✅ AI Model & Vectors Ready.")
        return cls._instance

    def get_embedding(self, text: str):
        return self.model.encode(text, convert_to_tensor=True)

    def get_similarity(self, text1: str, text2: str) -> float:
        """Get semantic similarity (0.0 to 1.0) between two texts."""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return float(util.pytorch_cos_sim(emb1, emb2)[0])

    # ✅ RESTORED: Single Item Classification (Fixes the AttributeError)
    def classify_category(self, skill: str) -> str:
        """
        Zero-Shot Classification for a single skill.
        Assigns a category based on semantic proximity to pre-computed anchors.
        """
        # Encode the single skill
        skill_emb = self.model.encode(skill, convert_to_tensor=True)
        
        # Compare against pre-computed category embeddings
        scores = util.pytorch_cos_sim(skill_emb, self.cat_embs)[0]
        
        # Find index of highest score
        best_idx = torch.argmax(scores).item()
        
        return self.cat_keys[best_idx]

    # ✅ RESTORED: Single Item Matcher
    def find_best_match(self, query: str, options: List[str], threshold: float = 0.65) -> Tuple[Union[str, None], float]:
        """
        Finds the best matching string in a list of options.
        """
        if not options: return None, 0.0
        
        query_emb = self.model.encode(query, convert_to_tensor=True)
        option_embs = self.model.encode(options, convert_to_tensor=True)
        
        scores = util.pytorch_cos_sim(query_emb, option_embs)[0]
        best_idx = torch.argmax(scores).item()
        best_score = float(scores[best_idx])
        
        if best_score >= threshold:
            return options[best_idx], best_score
            
        return None, 0.0

    # 🚀 BATCH METHOD: Filter Skills
    def batch_filter_skills(self, candidates: List[str], threshold: float = 0.35) -> List[str]:
        """
        Filters a list of candidates to keep only technical skills.
        Uses Matrix Multiplication for speed.
        """
        if not candidates:
            return []
            
        candidate_embs = self.model.encode(candidates, convert_to_tensor=True)
        
        # Compare all candidates against all technical anchors
        cosine_scores = util.pytorch_cos_sim(candidate_embs, self.skill_anchor_embs)
        
        # Max score per candidate
        max_scores, _ = torch.max(cosine_scores, dim=1)
        
        valid_skills = []
        for i, score in enumerate(max_scores):
            if score.item() > threshold:
                valid_skills.append(candidates[i])
                
        return valid_skills

    # 🚀 BATCH METHOD: Categorize Skills
    def batch_classify_categories(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Classifies a list of skills into categories using matrix multiplication.
        """
        if not skills:
            return {}

        skill_embs = self.model.encode(skills, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(skill_embs, self.cat_embs)
        best_category_indices = torch.argmax(scores, dim=1)
        
        categorized = {k: [] for k in self.cat_keys}
        
        for i, cat_idx in enumerate(best_category_indices):
            cat_name = self.cat_keys[cat_idx.item()]
            categorized[cat_name].append(skills[i])
            
        return categorized