"""
Configuration Settings
Global settings for file paths, scanning parameters, and matching weights
"""

from pathlib import Path

# ==========================================
# FILE PATHS
# ==========================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESUME_DIR = BASE_DIR / "sample_data" / "resumes"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, RESUME_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==========================================
# JOB SEARCH SETTINGS
# ==========================================
# Keywords to search for (customizable)
JOB_SEARCH_KEYWORDS = [
    "Data Scientist",
    "Machine Learning Engineer", 
    "Python Developer",
    "AI Engineer"
]

# Location for job search
JOB_SEARCH_LOCATION = "Malaysia"

# Maximum jobs to fetch total
TOTAL_MAX_JOBS = 30

# Enable synthetic jobs if scraper results are low
INCLUDE_SYNTHETIC_JOBS = True

# User Agent for scraping to avoid blocking
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)

# ==========================================
# MATCHING & SCORING
# ==========================================
# Weights for the overall match score
MATCHING_WEIGHTS = {
    'skills': 0.50,      # 50% weight on skills
    'experience': 0.30,  # 30% weight on experience
    'education': 0.10,   # 10% weight on education
    'industry': 0.10     # 10% weight on industry
}

# Weights for different skill categories in resume analysis
SKILL_CATEGORY_WEIGHTS = {
    'languages': 1.0,
    'ml_ai': 1.2,        # High value skills
    'data_engineering': 1.1,
    'cloud': 1.1,
    'web_frameworks': 0.9,
    'databases': 1.0,
    'tools': 0.8
}

# Thresholds for match quality classification
MATCH_THRESHOLDS = {
    'excellent': 0.85,
    'strong': 0.70,
    'good': 0.55,
    'fair': 0.40
}

# ==========================================
# LEARNING RESOURCES
# ==========================================
LEARNING_PLATFORMS = {
    'coursera': 'https://www.coursera.org/search?query=',
    'udemy': 'https://www.udemy.com/courses/search/?q=',
    'edx': 'https://www.edx.org/search?q=',
    'pluralsight': 'https://www.pluralsight.com/search?q=',
    'youtube': 'https://www.youtube.com/results?search_query=',
    'freecodecamp': 'https://www.freecodecamp.org/news/search/?query='
}

DOCUMENTATION_SITES = {
    'python': 'https://docs.python.org/3/',
    'pandas': 'https://pandas.pydata.org/docs/',
    'numpy': 'https://numpy.org/doc/',
    'scikit-learn': 'https://scikit-learn.org/stable/documentation.html',
    'tensorflow': 'https://www.tensorflow.org/learn',
    'pytorch': 'https://pytorch.org/docs/stable/index.html',
    'docker': 'https://docs.docker.com/',
    'kubernetes': 'https://kubernetes.io/docs/home/',
    'react': 'https://react.dev/',
    'django': 'https://docs.djangoproject.com/en/stable/'
}