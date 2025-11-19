# 🎯 Ultra-Intelligent AI Resume Analyzer

> **Professional-grade resume analysis and job matching system with intelligent learning roadmaps**

An advanced Python application that analyzes your resume, searches for relevant jobs across multiple sources, provides intelligent matching with gap analysis, and generates personalized learning roadmaps with direct links to resources.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ Key Features

### 1. 🔍 **Multi-Source Job Search** (No Login Required)
- **Indeed RSS Feed**: Real job postings without authentication
- **Google Jobs**: Direct search links to latest openings
- **LinkedIn Public URLs**: Quick access to job listings
- **Intelligent Fallback**: Synthetic realistic jobs for comprehensive analysis

### 2. 🧠 **Ultra-Intelligent Resume Analysis**
- **Skill Proficiency Detection**: Automatically detects Expert/Intermediate/Basic levels
- **100+ Skills**: Across 8 categories with intelligent weighting
- **Career Trajectory Analysis**: Understands your career progression
- **Impact Scoring**: Ranks achievements by business value
- **Industry Confidence**: Shows domain expertise strength

### 3. 📊 **Advanced Gap Analysis**
- **Critical vs Nice-to-Have**: Separates must-have from preferred skills
- **Gap Severity Assessment**: Minor/Moderate/Significant/Critical levels
- **Skill Relationships**: Shows complementary skills to learn together
- **Learning Time Estimates**: Realistic timeframes for each skill
- **Personalized Recommendations**: Tailored action items

### 4. 🎓 **Intelligent Learning Roadmap**
- **Direct Resource Links**: Coursera, Udemy, edX, YouTube, and more
- **Week-by-Week Plans**: Structured learning paths
- **Practice Platforms**: LeetCode, Kaggle, HackerRank links
- **Official Documentation**: Direct links to docs
- **Certification Paths**: Recommended certifications
- **Timeline Generation**: Month-by-month learning schedule

### 5. 📈 **Comprehensive Reports**
- **Job Match Analysis**: Detailed breakdown of each match
- **High Priority List**: "Apply Now" recommendations
- **Learning Roadmap CSV**: Prioritized skills with resources
- **Gap Analysis Report**: Frequency and priority of missing skills
- **JSON Export**: Complete data for further processing

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Resume Format**: PDF, DOCX, or TXT

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone or download this repository
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your resume
# Place your resume in: sample_data/resumes/
# Supported formats: PDF, DOCX, TXT

# 4. Run the analyzer
python main.py
```

### First Run

The system will:
1. ✅ Find and analyze your resume
2. ✅ Search for relevant jobs (Indeed, Google Jobs, LinkedIn)
3. ✅ Match jobs to your profile
4. ✅ Generate learning roadmap for missing skills
5. ✅ Create comprehensive reports in `outputs/` folder

---

## 📁 Project Structure

```
ai-resume-analyzer/
│
├── main.py                          # Main entry point
├── config.py                        # Configuration settings
├── requirements.txt                 # Dependencies
├── README.md                        # This file
│
├── core/                            # Core modules
│   ├── __init__.py
│   ├── resume_parser.py            # Text extraction
│   ├── resume_analyzer.py          # Intelligent analysis
│   ├── job_scraper.py              # Multi-source scraping
│   ├── job_matcher.py              # Smart matching
│   ├── gap_analyzer.py             # Gap analysis
│   └── learning_roadmap.py         # Learning paths
│
├── utils/                           # Utilities
│   ├── __init__.py
│   ├── logger.py                   # Logging setup
│   ├── report_generator.py        # Report creation
│   └── helpers.py                  # Helper functions
│
├── sample_data/                     # Your resumes go here
│   └── resumes/
│       └── your_resume.pdf
│
└── outputs/                         # Generated reports
    ├── JOB_MATCHES_DETAILED_*.csv
    ├── HIGH_PRIORITY_APPLY_NOW_*.csv
    ├── SKILL_GAPS_LEARNING_ROADMAP_*.csv
    └── COMPLETE_ANALYSIS_*.json
```

---

## 🎯 Usage Guide

### Basic Usage

```bash
python main.py
```

### Custom Job Search

Edit `config.py` to customize:

```python
# Change job search keywords
JOB_SEARCH_KEYWORDS = [
    "your job title",
    "alternative title",
    "related position"
]

# Change location
JOB_SEARCH_LOCATION = "Your City, Country"

# Adjust number of jobs
MAX_JOBS_PER_SOURCE = 10
```

### Understanding the Output

#### 1. **JOB_MATCHES_DETAILED_*.csv**
- All analyzed jobs sorted by match score
- Includes: Priority, Company, Match Score, Gap Severity, Recommendations
- Use this to understand all opportunities

#### 2. **HIGH_PRIORITY_APPLY_NOW_*.csv**
- Jobs with 65%+ match score
- Your best opportunities
- Includes "Why You're a Good Fit" explanations
- **Action**: Start applying here!

#### 3. **SKILL_GAPS_LEARNING_ROADMAP_*.csv**
Contains:
- **Missing Skill**: What you need to learn
- **Frequency**: How many jobs require it
- **Priority**: CRITICAL/HIGH/MEDIUM
- **Direct Links**: Coursera, Udemy, YouTube URLs
- **Practice Platforms**: LeetCode, Kaggle links
- **Learning Time**: Realistic estimates
- **Related Skills**: What to learn together

#### 4. **COMPLETE_ANALYSIS_*.json**
- Full analysis data
- Top 5 matches with insights
- Career recommendations
- Skill gap summary

---

## 📊 Match Score Interpretation

| Score | Quality | Priority | Action |
|-------|---------|----------|--------|
| 80%+ | Excellent | 🔥 URGENT | Apply immediately |
| 65-80% | Strong | ✅ HIGH | Apply within 2-3 days |
| 50-65% | Good | 📝 MEDIUM | Prepare and apply |
| 35-50% | Fair | ⚠️ LOW | Consider if interested |
| <35% | Weak | ❌ SKIP | Focus on better matches |

---

## 🎓 Learning Roadmap Features

### What You Get

For **each missing skill**, the roadmap provides:

#### 1. **Online Courses** (with direct links)
- **Coursera**: University-backed courses - [$49-99/month]
  - Example: `https://www.coursera.org/search?query=machine+learning`
- **Udemy**: Practical projects - [$10-200, often on sale]
  - Example: `https://www.udemy.com/courses/search/?q=python`
- **edX**: Professional certificates - [Free to audit]
  - Example: `https://www.edx.org/search?q=data+science`
- **YouTube**: Free tutorials - [Free]
  - Example: `https://www.youtube.com/results?search_query=tensorflow+tutorial`

#### 2. **Practice Platforms** (with direct links)
- **LeetCode**: Coding challenges
  - Example: `https://leetcode.com/problemset/?search=python`
- **Kaggle**: ML competitions and datasets
  - Example: `https://www.kaggle.com/search?q=machine+learning`
- **HackerRank**: Skills certification
  - Example: `https://www.hackerrank.com/domains/python`
- **FreeCodeCamp**: Interactive learning
  - Example: `https://www.freecodecamp.org/news/search/?query=javascript`

#### 3. **Official Documentation** (with direct links)
- Python: `https://docs.python.org/`
- TensorFlow: `https://www.tensorflow.org/learn`
- AWS: `https://docs.aws.amazon.com/`
- React: `https://react.dev/learn`

#### 4. **Learning Timeline**
- Week-by-week breakdown
- Month-by-month schedule
- Time commitments
- Milestones and goals

#### 5. **Related Skills**
- Complementary technologies
- Prerequisite knowledge
- Advanced topics
- Career path suggestions

### Example: Learning "Machine Learning"

```
Skill: Machine Learning
Priority: CRITICAL - Learn First
Difficulty: Intermediate
Estimated Time: 10 weeks (2.5 months)

📚 Online Courses:
  • Coursera: https://www.coursera.org/search?query=machine+learning
    - Free to audit, $49-99/month for certificate
  • Udemy: https://www.udemy.com/courses/search/?q=machine+learning
    - $10-200 per course (often on sale)
  • YouTube: https://www.youtube.com/results?search_query=machine+learning+tutorial
    - Free

🏋️ Practice:
  • Kaggle: https://www.kaggle.com/search?q=machine+learning
  • LeetCode: https://leetcode.com/problemset/?search=machine+learning

📖 Documentation:
  • Scikit-learn: https://scikit-learn.org/stable/
  • TensorFlow: https://www.tensorflow.org/learn

🎯 Learning Path (10 weeks):
  Week 1-2: Supervised Learning Basics
  Week 3-4: Unsupervised Learning
  Week 5-6: Model Evaluation & Tuning
  Week 7-8: Advanced Algorithms
  Week 9-10: Final Project

🔗 Related Skills: Python, Statistics, Pandas, TensorFlow
```

---

## ⚙️ Configuration

### Matching Weights

Adjust in `config.py`:

```python
MATCHING_WEIGHTS = {
    'skills': 0.50,      # Technical skills (default: 50%)
    'experience': 0.30,  # Years of experience (default: 30%)
    'education': 0.10,   # Education level (default: 10%)
    'industry': 0.10     # Industry match (default: 10%)
}
```

### Skill Category Importance

```python
SKILL_CATEGORY_WEIGHTS = {
    'programming': 1.0,
    'ml_ai': 1.2,        # Higher weight = more important
    'data': 1.1,
    'cloud_devops': 1.15,
    'specialized': 1.3   # Rare skills = highest weight
}
```

---

## 🎨 Sample Output

```
================================================================================
                   🎯 INTELLIGENT RESUME ANALYSIS RESULTS
================================================================================

📋 YOUR PROFILE
Career Level: Mid-Senior Level
Experience: 6 years (SENIOR)
Skills: 45 total (12 expert-level)
Achievements: 15 quantified impacts

💪 Your Key Strengths:
  • Deep specialization in ML/AI
  • Strong track record of measurable business impact
  • Extensive industry experience (6 years)

📊 MATCHING STATISTICS
Total Jobs Analyzed: 25
🔥 Urgent/Excellent (80%+): 5
✅ High Priority (65%+): 12
📝 Medium Priority (50%+): 6
Average Match Score: 68.2%

🏆 TOP 5 OPPORTUNITIES
--------------------------------------------------------------------------------

1. 🔥 URGENT Senior Data Scientist
   Company: Tech Innovations Malaysia | Location: Kuala Lumpur
   Overall Match: 85.3% (Excellent Match)
   Skills Coverage: 92% | Gap Severity: Minor
   Apply immediately - You're an ideal candidate!
   ✨ Strengths: Strong technical match (92% of required skills)
   📋 Next Step: 🎯 Tailor resume to highlight matching skills
   🔗 https://www.indeed.com/job/12345

2. ✅ HIGH Machine Learning Engineer
   Company: AI Solutions | Location: Selangor
   Overall Match: 72.8% (Strong Match)
   Skills Coverage: 85% | Gap Severity: Moderate
   Highly recommended - Address minor gaps in cover letter
   ✨ Strengths: Experience level aligns perfectly
   📋 Next Step: 📚 Nice to have: keras, computer vision
   🔗 https://www.indeed.com/job/67890

================================================================================
✅ ANALYSIS COMPLETE - Check 'outputs' folder for detailed reports!
================================================================================

📁 All reports saved to: /path/to/outputs/

💡 Next Steps:
1. Review 'HIGH_PRIORITY_APPLY_NOW_*.csv' for immediate applications
2. Check 'SKILL_GAPS_LEARNING_ROADMAP_*.csv' for learning priorities
3. Read 'COMPLETE_ANALYSIS_*.json' for detailed insights
```

---

## 🔧 Troubleshooting

### Issue: "No resume found"

**Solution**:
```bash
# Ensure resume is in correct location
mkdir -p sample_data/resumes
cp /path/to/your/resume.pdf sample_data/resumes/
```

### Issue: "Could not extract text from PDF"

**Solutions**:
1. Try converting PDF to DOCX or TXT
2. Ensure PDF is text-based (not scanned image)
3. Save PDF as "Text (Accessible)"

### Issue: Low match scores

**Causes & Solutions**:
- ❌ **Cause**: Missing technical keywords
  - ✅ **Fix**: Add specific technologies to resume
- ❌ **Cause**: Experience years not clear
  - ✅ **Fix**: Use format "2020 - Present" or "2018 - 2023"
- ❌ **Cause**: Skills not explicitly listed
  - ✅ **Fix**: Create a "Technical Skills" section

### Issue: Job scraping not working

**Note**: This system uses **no-login methods**:
- ✅ Indeed RSS (works reliably)
- ✅ Google Jobs (creates search links)
- ✅ Synthetic jobs (for comprehensive analysis)

If real jobs aren't found, the system automatically generates realistic synthetic jobs for analysis.

---

## 🎯 Best Practices

### Resume Optimization

```markdown
✅ DO:
  • Use date ranges: "2020 - Present"
  • Quantify achievements: "Increased revenue by 30%"
  • List skills explicitly: "Python, SQL, AWS"
  • Use clear section headers
  • Include certifications

❌ DON'T:
  • Use images or graphics only
  • Omit years of experience
  • Use vague descriptions
  • Forget to update regularly
```

### Application Strategy

1. **High Priority (65%+)**
   - Apply within 2-3 days
   - Tailor resume for each
   - Write custom cover letter
   - Research company thoroughly

2. **Medium Priority (50-65%)**
   - Review skill gaps first
   - Prepare to demonstrate transferable skills
   - Apply if truly interested
   - Highlight learning ability

3. **Low Priority (<50%)**
   - Focus learning on gap skills
   - Revisit after upskilling
   - Use for market research

### Learning Strategy

1. **Month 1**: Focus on 1-2 critical skills
2. **Month 2-3**: Build projects with new skills
3. **Month 4+**: Apply for jobs requiring those skills
4. **Continuous**: Keep updating resume

---

## 📈 Advanced Features

### Custom Skill Categories

Add your domain-specific skills in `config.py`:

```python
SKILL_CATEGORIES = {
    'your_domain': {
        'skills': ['skill1', 'skill2', 'skill3'],
        'weight': 1.2  # Importance multiplier
    }
}
```

### Export for Further Analysis

```python
import json

# Load detailed analysis
with open('outputs/COMPLETE_ANALYSIS_*.json') as f:
    data = json.load(f)

# Access specific data
top_matches = data['top_5_matches']
skill_gaps = data['skill_gap_summary']
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- [ ] Additional job sources
- [ ] ML-based skill extraction
- [ ] Resume formatting suggestions
- [ ] Interview preparation tips
- [ ] Salary insights

---

## 🙏 Acknowledgments

- Built with Python, Pandas, BeautifulSoup
- Inspired by modern recruitment challenges
- Designed for job seekers in tech industry

---


## 🔮 Roadmap

- [ ] Web interface
- [ ] Resume builder integration
- [ ] Interview preparation module
- [ ] Salary prediction
- [ ] Job market trends analysis
- [ ] ATS compatibility checker

---

**Made with ❤️ for job seekers worldwide**

*Star ⭐ this repo if you find it helpful!*