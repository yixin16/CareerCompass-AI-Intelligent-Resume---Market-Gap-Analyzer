# 🧭 Career Compass AI: Intelligent Resume & Market gap Analyzer

**Agentic Career Coach | Real-Time Voice Interviewer | Semantic Market Analyzer**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-ff4b4b.svg)
![Llama 3.3](https://img.shields.io/badge/Llama%203.3-Groq-purple)
![LangGraph](https://img.shields.io/badge/Agentic-LangGraph-orange)
![Multimodal](https://img.shields.io/badge/Multimodal-Whisper%20%7C%20EdgeTTS-yellow)
![NLP](https://img.shields.io/badge/NLP-BERT%20%7C%20SentenceTransformers-green)

---

## 📖 Overview

**CareerCompass AI** is an autonomous, multimodal AI ecosystem designed to bridge the gap between job seekers and the live job market. Unlike standard resume parsers, this system employs **Agentic AI** and **Vector Embeddings** to actively research live job opportunities, quantify skill gaps semantically, and provide real-time voice coaching.

It solves the "blind application" problem by analyzing the mathematical distance between a candidate's profile and market demands, offering **Transfer Learning** roadmaps and **Voice-Enabled interview** simulations.

![Dashboard Screenshot](assets/dashboard.png)

---

## 🏗️ System Architecture
The application is built on a modular, event-driven architecture optimized for high throughput and low latency.
graph TD
    subgraph "Data Ingestion"
    A[User Resume (PDF)] -->|OCR & Regex| B[Structured Profile]
    B -->|Batch Embedding| C[Vector Store (FAISS)]
    D[Live Job Market] -->|Scraper| E[Job Listings]
    E -->|Batch Embedding| C
    end

    subgraph "Intelligence Engine"
    C -->|Cosine Similarity| F[Gap Analysis Engine]
    F -->|Clustering| G[Critical Skill Gaps]
    G -->|Llama 3.3 Agent| H[Transfer Learning Roadmap]
    end

    subgraph "Real-Time Interaction"
    I[Audio Input] -->|Whisper V3 Turbo| J[Transcriber]
    J -->|Llama 3.3 Json Mode| K[Interviewer Logic]
    K -->|JSON| L[Question + Sample Answer]
    L -->|EdgeTTS| M[Audio Output]
    end


## 🚀 Key Features & Engineering Decisions

### 1. High-Performance Semantic Analysis
*   **Batch Vector Processing:** Instead of iterating through skills one-by-one, the system uses matrix multiplication to validate and categorize hundreds of skills instantly using sentence-transformers/all-MiniLM-L6-v2.
*   **Context-Aware Parser:** Extracts skills, experience timeline (handling gaps and overlaps), and contact info using a hybrid of Regex heuristics and BERT-based validation.

### 2. Smart Gap Analyzer
*   Implements **DuckDuckGo** search dorking with rotating headers to build a resilient, anti-bot resistant scraping pipeline.
*   **Severity Scoring:** Calculates a priority score based on Frequency × Domain Weight (e.g., missing a core Language is weighted higher than missing a soft skill).
*   **Market Penetration:** Calculates the exact percentage of jobs requiring a specific missing skill.

### 3. Agentic Learning Roadmap (Transfer Learning)
*   **Contextual Curriculum:** Instead of generic advice, the AI analyzes the user's current stack to generate Transfer Learning strategies (e.g., "Since you know Java, learn Python by focusing on these syntax differences...").
*   **Hybrid Resources:** Combines AI-generated project ideas with deterministic, high-quality links (LeetCode, Kaggle, Official Docs) to ensure reliability.

### 4. Real-Time Mock Interviewer
*   **Latency Optimized:** Utilizes Groq LPU (Language Processing Unit) to achieve <1s response times, creating a fluid conversation.
*   **Multimodal Pipeline** Instantly renders the tailored content into a clean, ATS-friendly **PDF** using a professional template.
      * **Input:** Whisper-Large-V3-Turbo for instant speech-to-text.
      * **Logic:** Llama-3.3-70b generating structured JSON (Feedback + Question + Sample Answer).
      * **Output:** EdgeTTS for neural voice synthesis.
*  **Guided Coaching:** The UI displays a hidden "Sample Answer" for every question, allowing users to compare their response with a Senior Engineer's ideal answer.

### 🎤 5. AI Resume Tailor
*   **STAR Method Injection:** Rewrites experience bullet points to follow the **S**ituation, **T**ask, **A**ction, **R**esult format using generative AI.
*   **ATS Keyword Optimization:** Dynamically re-ranks skill lists to place job-specific keywords at the top for higher ATS scoring.


---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **LLM Inference** | Groq (Llama 3.3 70B) | Delivers 300+ tokens/sec, essential for real-time voice interaction. |
| **Voice (STT)** | Whisper Large V3 Turbo | 8x faster than standard Whisper with comparable accuracy. |
| **Voice (TTS)** | Edge-TTS | High-quality neural voices without the cost/latency of ElevenLabs. |
| **Embeddings** | Sentence-Transformers | Local inference for free, high-speed semantic similarity matching. |
| **Backend/UI** | Streamlit | Rapid prototyping with session state management for chat history. |
| **Orchestration** | LangChain | Manages prompt templates and structured JSON parsing. |
| **PDF Engine** | xhtml2pdf | HTML-to-PDF rendering for resume tailoring |
| **Data Acquisition** | DuckDuckGo Search | Live market data aggregation |
---

## 📂 Project Structure

```
CareerCompass-AI/
├── app.py                   # Main Streamlit application
├── core/
│   ├── agent_graph.py  # LangGraph Agent (Research + Writing)
│   ├── interviewer.py  # Voice Pipeline
│   ├── resume_tailor.py  # ATS Optimization Agent
│   ├── cover_letter_generator.py   # Tone-aware Writer
│   ├── gap_analyzer.py
│   ├── job_matcher.py
│   ├── job_scraper.py
│   ├── learning_roadmap.py   # Transfer Learning Agent
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
│   └── pdf_generator.py   # HTML to PDF Conversion
├── main.py
├── config.py
├── requirements.txt
└── README.md
```

---

## ⚡ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yixin16/CareerCompass-AI-Intelligent-Resume---Market-Gap-Analyzer.git
cd CareerCompass-AI-Intelligent-Resume---Market-Gap-Analyzer
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
* Get a free key at [console.groq.com](https://console.groq.com) and configure it in the sidebar / or place in the .env file.

### 5. Run the Application

```bash
streamlit run app.py
```

---

## Usage Guide

1. **Resume Analysis:** Upload a PDF. The system extracts skills using batch vector processing.
2. **Market Scan:** Enter a job title (e.g., "Data Scientist"). The system scrapes live jobs and performs 3. semantic matching.
4. **Gap Analysis:** View the "Critical Gaps" chart to see which skills you are missing that are highly weighted in the current market.
5. **Roadmap:** Generate a study plan. The AI will look at your existing skills and tell you exactly how to bridge the gap.
6. **Mock Interview:** Switch to the Interview tab. Click "Start Session," speak into your microphone, and receive immediate technical questions and sample answers.

---

## 🔮 Future Roadmap

* **Video Analysis:** Integrate OpenCV to analyze facial expressions and confidence during the mock interview.
* **Dockerization:** Containerize the application for easy deployment on AWS/Azure.
* **Database Integration:** Implement PostgreSQL to persist user progress and chat history.

---


*This project was developed as a comprehensive portfolio showcase demonstrating expertise in Full-Stack GenAI, RAG Systems, Agentic Workflows, and Low-Latency Architecture.*
