# 🧭 CareerCompass AI

**Intelligent Resume & Market Gap Analyzer**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-ff4b4b.svg)
![Llama 3](https://img.shields.io/badge/Llama%203-Groq-purple)
![NLP](https://img.shields.io/badge/NLP-BERT%20%7C%20SentenceTransformers-green)

---

## 📖 Overview

**CareerCompass AI** is a next-generation career intelligence tool designed to bridge the gap between job seekers and market demands. Unlike traditional keyword-based systems, it leverages **BERT-based vector embeddings** to understand the semantic meaning of skills and **Llama 3 (via Groq)** to generate hyper-personalized application materials and learning roadmaps.

![Dashboard Screenshot](assets/dashboard.png)

---

## 🚀 Key Features

### 🧠 Semantic Resume Analysis

* Parses PDF/DOCX resumes to extract skills, experience, and education.
* Creates vector embeddings of the candidate's profile using **BERT** and **Sentence-Transformers**.

### 🌍 Real-Time Market Scanner

* Aggregates live job listings from LinkedIn, Indeed, and other sources.
* Uses DuckDuckGo search dorking to bypass basic anti-bot restrictions.

### ⚖️ Intelligent Gap Analysis

* Calculates a **Match Score** based on semantic similarity, not just keywords.
* Identifies **missing skills** trending in the market but absent in the profile.

### 🤖 GenAI Agent (Llama 3)

* **Cover Letter Generator:** Drafts tailored cover letters referencing specific projects and job requirements.
* **Learning Roadmap:** Generates personalized 3-month study plans to fill identified skill gaps.

---

## 🛠️ Tech Stack

| Component        | Technology                | Description                               |
| ---------------- | ------------------------- | ----------------------------------------- |
| Frontend         | Streamlit                 | Interactive web dashboard & UI            |
| LLM Inference    | Groq Cloud                | Ultra-low latency API for Llama 3         |
| NLP & Embeddings | HuggingFace / BERT        | Semantic similarity and entity extraction |
| Data Processing  | Pandas, NumPy             | Structured data manipulation              |
| Web Scraping     | BeautifulSoup, DuckDuckGo | Resilient scraping pipeline for job data  |
| Visualization    | Matplotlib, Altair        | Radar charts, word clouds                 |

---

## 📂 Project Structure

```
CareerCompass-AI/
├── app.py                   # Main Streamlit application
├── core/
│   ├── cover_letter_generator.py
│   ├── gap_analyzer.py
│   ├── job_matcher.py
│   ├── job_scraper.py
│   ├── learning_roadmap.py
│   ├── resume_analyzer.py
│   ├── resume_parser.py
│   └── semantic_matcher.py
├── data/
│   ├── job_templates.py
│   └── skills_categories.py
├── sample_data/
│   └── resumes/Resume.pdf
├── utils/
│   ├── helpers.py
│   ├── logger.py
│   ├── report_generator.py
│   └── visualizer.py
├── main.py
├── config.py
├── requirements.txt
└── README.md
```

---

## ⚡ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/CareerCompass-AI.git
cd CareerCompass-AI
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys

* Groq API Key is required for LLM features.
* Get a free key at [console.groq.com](https://console.groq.com) and configure it in the sidebar.

### 5. Run the Application

```bash
streamlit run app.py
```

---

## 📸 Usage Guide

1. **Upload Profile:** Drag & drop your PDF resume in the sidebar.
2. **Set Preferences:** Enter target role and location.
3. **Run Analysis:** Click **Run Analysis** to parse data and scrape live job listings.
4. **View Insights:**

   * **Market Tab:** Compare your skills with market trends via radar charts.
   * **Matches Tab:** View ranked job opportunities with match scores.
   * **Roadmap Tab:** Generate a step-by-step learning plan for missing skills.
   * **Cover Letter Tab:** Select a job and let AI draft a personalized cover letter.

---

## 🔮 Future Roadmap

* **Agentic Workflow:** Integrate LangGraph for AI-driven web browsing before generating cover letters.
* **Resume Tailoring:** Auto-generate resume PDF highlighting relevant keywords for each job.
* **Mock Interviewer:** Add a voice-enabled chatbot (Whisper + TTS) to practice technical interview questions.

---


*This project demonstrates expertise in Full-Stack GenAI Development, NLP, and System Architecture.*
