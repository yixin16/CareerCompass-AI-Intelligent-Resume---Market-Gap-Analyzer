
"""
Semantic Matcher & AI Classifier
The central intelligence unit using BERT-based embeddings.
"""

import numpy as np
from typing import List, Tuple, Union
from sentence_transformers import SentenceTransformer, util
from utils.logger import logger

class SemanticMatcher:
    _instance = None
    _model = None
    
    # Anchors define the "Center" of a concept in vector space
    ANCHORS = {
        'technical_skill': [
            "software engineering skill", "programming language", "framework", 
            "cloud platform", "database technology", "machine learning tool", 
            "developer tool", "technical competency"
        ],
        'categories': {
            'Programming': "software development coding java python c++ code",
            'Data & AI': "machine learning artificial intelligence statistics data analysis sql pandas",
            'Web & UI': "frontend backend react angular html css javascript user interface",
            'Cloud & DevOps': "aws azure docker kubernetes ci/cd infrastructure server",
            'Soft Skills': "leadership communication management agile collaboration team"
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticMatcher, cls).__new__(cls)
            logger.info("🧠 Loading Neural Network (all-MiniLM-L6-v2)...")
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ AI Model Ready.")
        return cls._instance

    def get_embedding(self, text: str):
        return self._model.encode(text, convert_to_tensor=True)

    def get_similarity(self, text1: str, text2: str) -> float:
        """Get semantic similarity (0.0 to 1.0) between two texts."""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return float(util.pytorch_cos_sim(emb1, emb2)[0])

    def is_technical_skill(self, candidate_word: str, threshold: float = 0.35) -> bool:
        """
        Binary Classifier: Is this word likely a technical skill?
        Compares candidate against 'technical_skill' anchors.
        """
        if len(candidate_word) < 2: return False
        
        # Encode candidate
        cand_emb = self.get_embedding(candidate_word)
        # Encode anchors
        anchor_embs = self._model.encode(self.ANCHORS['technical_skill'], convert_to_tensor=True)
        
        # Find max similarity
        scores = util.pytorch_cos_sim(cand_emb, anchor_embs)[0]
        max_score = float(scores.max())
        
        return max_score > threshold

    def classify_category(self, skill: str) -> str:
        """
        Zero-Shot Classification: Assigns a category based on semantic proximity.
        """
        categories = list(self.ANCHORS['categories'].keys())
        definitions = list(self.ANCHORS['categories'].values())
        
        skill_emb = self.get_embedding(skill)
        cat_embs = self._model.encode(definitions, convert_to_tensor=True)
        
        scores = util.pytorch_cos_sim(skill_emb, cat_embs)[0]
        best_idx = int(np.argmax(scores.cpu().numpy()))
        
        return categories[best_idx]

    def find_best_match(self, query: str, options: List[str], threshold: float = 0.65) -> Tuple[Union[str, None], float]:
        """
        Finds the best matching string in a list of options.
        Example: Query="K8s", Options=["Kubernetes", "Java"] -> Returns "Kubernetes"
        """
        if not options: return None, 0.0
        
        query_emb = self.get_embedding(query)
        option_embs = self._model.encode(options, convert_to_tensor=True)
        
        scores = util.pytorch_cos_sim(query_emb, option_embs)[0]
        best_idx = int(np.argmax(scores.cpu().numpy()))
        best_score = float(scores[best_idx])
        
        if best_score >= threshold:
            return options[best_idx], best_score
            
        return None, 0.0