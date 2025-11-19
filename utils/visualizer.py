"""
Report Visualizer
Generates radar charts and word clouds for the analysis.
"""

import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
from pathlib import Path
from typing import Dict, List
from utils.logger import logger

class ReportVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def generate_skill_radar(self, skill_categories: Dict) -> Path:
        """Creates a Radar/Spider chart of skill distribution."""
        logger.info("  📊 Generating Skill Radar Chart...")
        
        categories = list(skill_categories.keys())
        counts = [len(v) for v in skill_categories.values()]
        
        # Close the loop for radar chart
        categories = [*categories, categories[0]]
        counts = [*counts, counts[0]]
        
        label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(counts))

        plt.figure(figsize=(8, 8))
        plt.subplot(polar=True)
        plt.plot(label_loc, counts, label='Skill Count')
        plt.fill(label_loc, counts, alpha=0.25)
        plt.title('Skill Distribution by Category', size=20, y=1.05)
        plt.lines, plt.labels = plt.thetagrids(np.degrees(label_loc), labels=categories)
        
        filepath = self.output_dir / "visual_skill_radar.png"
        plt.savefig(filepath)
        plt.close()
        return filepath

    def generate_market_wordcloud(self, jobs: List[Dict]) -> Path:
        """Creates a Word Cloud from all job descriptions."""
        logger.info("  ☁️ Generating Market Keyword Cloud...")
        
        text = " ".join([j.get('description', '') for j in jobs])
        
        wc = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(text)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title('Top Market Keywords', size=15)
        
        filepath = self.output_dir / "visual_market_wordcloud.png"
        plt.savefig(filepath)
        plt.close()
        return filepath