# core/interviewer.py
import os
import asyncio
import edge_tts
import uuid
import sys
import nest_asyncio
from gtts import gTTS 

# 1. Apply Nested Async Fix
nest_asyncio.apply()

# 2. Windows Async Fix
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

try:
    from groq import Groq
except ImportError:
    pass


class MockInterviewer:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key missing.")
        self.client = Groq(api_key=api_key)
        self.llm_model = "llama-3.3-70b-versatile" 
        self.stt_model = "whisper-large-v3-turbo"

    def transcribe_audio(self, audio_bytes):
        try:
            if hasattr(audio_bytes, 'seek'):
                audio_bytes.seek(0) 
                audio_data = audio_bytes.read()
            else:
                audio_data = audio_bytes

            transcription = self.client.audio.transcriptions.create(
                file=("input.wav", audio_data), 
                model=self.stt_model,
                response_format="text",
                language="en" 
            )
            return transcription
        except Exception as e:
            return f"Error: {e}"

    def get_ai_response(
        self, 
        history, 
        target_role="AI Engineer",
        company_name="",
        job_description="",
        resume_context="",
        interview_focus="balanced",  # "behavioral", "technical", "balanced"
        difficulty="medium"  # "entry", "medium", "senior", "staff"
    ):
        """
        Generates context-aware interview questions with difficulty and focus control.
        
        Args:
            history: Conversation history
            target_role: Job title (e.g., "AI Engineer", "Senior ML Engineer")
            company_name: Company name for context
            job_description: Job requirements and description
            resume_context: Candidate's resume summary
            interview_focus: "behavioral", "technical", or "balanced"
            difficulty: "entry", "medium", "senior", "staff"
        """
        import json
        
        # === DIFFICULTY CONFIGURATIONS ===
        difficulty_configs = {
            "entry": {
                "level": "Entry-Level / Junior",
                "expectation": "0-2 years experience",
                "technical_depth": "Focus on fundamentals, basic concepts, and willingness to learn",
                "behavioral_depth": "Academic projects, internships, learning experiences",
                "example_technical": "Explain what a neural network is and how backpropagation works",
                "example_behavioral": "Tell me about a challenging course project and how you overcame obstacles"
            },
            "medium": {
                "level": "Mid-Level",
                "expectation": "2-5 years experience",
                "technical_depth": "Practical implementation knowledge, system design basics, debugging skills",
                "behavioral_depth": "Real-world projects, team collaboration, handling production issues",
                "example_technical": "How would you debug a model that's overfitting? Walk me through your approach",
                "example_behavioral": "Describe a time when you had to explain a complex technical concept to non-technical stakeholders"
            },
            "senior": {
                "level": "Senior / Lead",
                "expectation": "5-10 years experience",
                "technical_depth": "Architecture decisions, scalability, trade-offs, optimization at scale",
                "behavioral_depth": "Leadership, mentoring, cross-team collaboration, strategic thinking",
                "example_technical": "Design a real-time recommendation system serving 10M users with <100ms latency",
                "example_behavioral": "Tell me about a time you had to make a difficult technical decision that involved trade-offs"
            },
            "staff": {
                "level": "Staff / Principal",
                "expectation": "10+ years, industry leadership",
                "technical_depth": "Multi-system architecture, research-level problems, innovation, org-wide impact",
                "behavioral_depth": "Strategic vision, influencing without authority, technical roadmaps, cross-org leadership",
                "example_technical": "How would you architect a distributed training system for foundation models across multiple datacenters?",
                "example_behavioral": "Describe how you've influenced technical direction across multiple teams or an entire organization"
            }
        }
        
        # === FOCUS CONFIGURATIONS ===
        focus_configs = {
            "behavioral": {
                "ratio": "80% Behavioral / 20% Technical",
                "emphasis": "Leadership, teamwork, conflict resolution, communication, growth mindset",
                "structure": "Use STAR method (Situation, Task, Action, Result) for all answers",
                "topics": [
                    "Leadership and influence",
                    "Conflict resolution",
                    "Project management",
                    "Communication with stakeholders",
                    "Learning from failure",
                    "Team collaboration",
                    "Prioritization and time management"
                ]
            },
            "technical": {
                "ratio": "90% Technical / 10% Behavioral",
                "emphasis": "Deep technical knowledge, problem-solving, system design, algorithms",
                "structure": "Expect code-level discussions, architecture diagrams, complexity analysis",
                "topics": [
                    "ML algorithms and theory",
                    "System design and architecture",
                    "Code optimization and debugging",
                    "Data structures and algorithms",
                    "MLOps and deployment",
                    "Model evaluation and metrics",
                    "Real-world problem solving"
                ]
            },
            "balanced": {
                "ratio": "50% Technical / 50% Behavioral",
                "emphasis": "Holistic evaluation of both technical skills and soft skills",
                "structure": "Alternate between technical deep-dives and behavioral questions",
                "topics": [
                    "Technical problem-solving with team context",
                    "Project delivery with technical challenges",
                    "Communication of technical concepts",
                    "Leadership in technical initiatives",
                    "Learning and adapting to new technologies"
                ]
            }
        }
        
        # Get configurations
        diff_config = difficulty_configs.get(difficulty, difficulty_configs["medium"])
        focus_config = focus_configs.get(interview_focus, focus_configs["balanced"])
        
        # === AI ENGINEER SPECIFIC KNOWLEDGE BASE ===
        ai_engineer_domains = """
**AI ENGINEER CORE COMPETENCIES:**

1. **Machine Learning Fundamentals**
   - Supervised/Unsupervised/Reinforcement Learning
   - Neural Networks (CNNs, RNNs, Transformers)
   - Training: Backpropagation, Gradient Descent, Optimizers (Adam, SGD)
   - Regularization: Dropout, Batch Norm, L1/L2
   - Evaluation: Precision, Recall, F1, ROC-AUC, Confusion Matrix

2. **Deep Learning Frameworks**
   - PyTorch, TensorFlow, JAX
   - Model architecture design
   - Custom layers and loss functions
   - Distributed training (DDP, FSDP)

3. **NLP & LLMs**
   - Transformers architecture (Attention, Multi-head attention)
   - Pre-training (MLM, CLM) and Fine-tuning
   - RAG (Retrieval-Augmented Generation)
   - Prompt Engineering, In-context Learning
   - LangChain, LlamaIndex
   - Vector databases (Pinecone, Weaviate, ChromaDB)

4. **Computer Vision**
   - Image classification, Object detection (YOLO, R-CNN)
   - Segmentation (U-Net, Mask R-CNN)
   - GANs, Diffusion Models
   - Transfer Learning (ResNet, EfficientNet)

5. **MLOps & Production**
   - Model versioning (MLflow, Weights & Biases)
   - Deployment (FastAPI, TensorFlow Serving, TorchServe)
   - Monitoring: Drift detection, A/B testing
   - CI/CD for ML pipelines
   - Docker, Kubernetes
   - Feature stores (Feast)

6. **Data Engineering**
   - Data pipelines (Airflow, Prefect)
   - Big data tools (Spark, Hadoop)
   - SQL, NoSQL databases
   - Data versioning (DVC)

7. **System Design for AI**
   - Real-time inference optimization
   - Model compression (Quantization, Pruning, Distillation)
   - Batch vs Real-time serving
   - Caching strategies
   - Scalability and latency trade-offs
"""
        
        # === CONSTRUCT SYSTEM PROMPT ===
        job_context = f"**Position**: {target_role}"
        if company_name:
            job_context += f" at {company_name}"
        
        system_content = f"""You are a world-class technical interviewer conducting a {diff_config['level']} interview for:

{job_context}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 INTERVIEW CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Difficulty Level**: {diff_config['level']} ({diff_config['expectation']})
**Interview Focus**: {interview_focus.upper()} ({focus_config['ratio']})
**Technical Depth**: {diff_config['technical_depth']}
**Behavioral Depth**: {diff_config['behavioral_depth']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 JOB REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{job_description if job_description else "Focus on AI/ML engineering competencies"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 CANDIDATE PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{resume_context if resume_context else "No resume provided"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 AI ENGINEER KNOWLEDGE DOMAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ai_engineer_domains}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 INTERVIEW STRUCTURE & RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Focus Areas**: {', '.join(focus_config['topics'][:5])}

**Your Mission**:
1. **Assess at the RIGHT level**: Questions must match {diff_config['level']} expectations
2. **Follow the focus**: Maintain {focus_config['ratio']} split
3. **Be realistic**: Ask questions a hiring manager for THIS EXACT ROLE would ask
4. **Progressive difficulty**: 
   - Rounds 1-2: Warm-up (behavioral intro OR basic technical)
   - Rounds 3-5: Core competency testing
   - Rounds 6-8: Deep-dive scenarios
   - Rounds 9+: Advanced edge cases OR strategic thinking

5. **Provide feedback**: When candidate answers incorrectly or incompletely:
   - Acknowledge what they got right
   - Gently correct misconceptions
   - Guide them toward the right answer
   - THEN move to next question

6. **Contextual questioning**:
   - Reference their resume experiences
   - Connect to job requirements
   - Build on previous answers
   - Ask follow-ups to dig deeper

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT (STRICT JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
    "question": "Your response. Include feedback on their previous answer (2-3 sentences), then ask the next question (1-2 sentences). Keep conversational and natural.",
    "sample_answer": "A {diff_config['level']} quality answer. Use STAR method for behavioral. Include specific metrics/technologies for technical. Keep under 5 sentences."
}}

**CRITICAL RULES**:
- Output ONLY valid JSON, no markdown code blocks
- Question should feel like a natural conversation
- Sample answer should demonstrate {diff_config['level']} expertise
- For technical questions: Include specific technologies, trade-offs, metrics
- For behavioral questions: Include STAR structure (Situation, Task, Action, Result)
- Match the difficulty to {difficulty} level
- Maintain {interview_focus} focus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 EXAMPLE OUTPUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Example 1 - Technical ({difficulty} level)**:
{diff_config['example_technical']}

**Example 2 - Behavioral ({difficulty} level)**:
{diff_config['example_behavioral']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Now, analyze the conversation history and generate the NEXT question that:
1. Matches the {diff_config['level']} difficulty
2. Maintains {focus_config['ratio']} focus on {interview_focus}
3. Tests competencies from the AI Engineer domain
4. Feels like a real interview with {company_name if company_name else "a top tech company"}
"""
        
        messages = [{"role": "system", "content": system_content}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=1200,
                temperature=0.7
            )
            response_dict = json.loads(completion.choices[0].message.content)
            
            # Validate
            if "question" not in response_dict or "sample_answer" not in response_dict:
                return self._get_fallback_response(target_role, company_name, difficulty, interview_focus)
            
            return response_dict
            
        except Exception as e:
            print(f"LLM error: {e}")
            return self._get_fallback_response(target_role, company_name, difficulty, interview_focus)

    def _get_fallback_response(self, target_role="", company_name="", difficulty="medium", focus="balanced"):
        """Enhanced fallback with difficulty and focus awareness."""
        
        fallbacks = {
            "entry": {
                "behavioral": {
                    "question": "Tell me about a project from your coursework or internship where you had to learn a new technology quickly.",
                    "sample_answer": "During my university capstone project, I had to learn React in 2 weeks to build our frontend. I watched tutorials, built small projects, and asked my teammate for code reviews. We successfully deployed the app and got an A on the project."
                },
                "technical": {
                    "question": "Can you explain what overfitting is and how you would detect it?",
                    "sample_answer": "Overfitting occurs when a model memorizes training data instead of learning patterns. I'd detect it by monitoring training vs validation loss - if training loss keeps decreasing but validation loss increases, that's overfitting. I'd address it using techniques like dropout, regularization, or getting more training data."
                }
            },
            "senior": {
                "behavioral": {
                    "question": "Describe a time when you had to make a critical architectural decision that affected multiple teams.",
                    "sample_answer": "When designing our ML platform, I chose to standardize on PyTorch over TensorFlow despite some teams' preference for TF. I ran POCs, presented trade-off analysis to leadership, and created a migration plan. This decision reduced maintenance overhead by 40% and enabled faster model iteration."
                },
                "technical": {
                    "question": "How would you design a distributed training system for large language models?",
                    "sample_answer": "I'd use a combination of data parallelism and model parallelism. For a 70B parameter model, I'd shard it across 8 GPUs using FSDP or DeepSpeed. Implement gradient checkpointing to reduce memory, use mixed precision training (fp16/bf16), and set up asynchronous data loading with multiple workers. Monitor GPU utilization and adjust batch size dynamically."
                }
            }
        }
        
        level = "senior" if difficulty in ["senior", "staff"] else "entry"
        focus_type = "behavioral" if focus == "behavioral" else "technical"
        
        return fallbacks[level][focus_type]

    def generate_initial_greeting(
        self, 
        target_role, 
        company_name="", 
        job_description="",
        interview_focus="balanced",
        difficulty="medium"
    ):
        """
        Generates a personalized opening based on focus and difficulty.
        """
        company_context = f" at {company_name}" if company_name else ""
        
        # Adjust greeting based on difficulty
        if difficulty == "entry":
            excitement = "excited to learn more about your background and potential"
            focus_mention = "We'll start with some foundational questions"
        elif difficulty in ["senior", "staff"]:
            excitement = "looking forward to discussing your technical leadership and architecture experience"
            focus_mention = "We'll dive deep into system design and strategic thinking"
        else:
            excitement = "eager to discuss your technical experience and problem-solving approach"
            focus_mention = "We'll cover both technical skills and collaboration experiences"
        
        # Adjust based on focus
        if interview_focus == "behavioral":
            question = (
                f"Hello! I'm {excitement}. This interview will focus primarily on your leadership, "
                f"teamwork, and communication experiences for the {target_role} position{company_context}. "
                f"To start, could you tell me about yourself and what motivates you to pursue this role?"
            )
            sample_answer = (
                f"I'm currently a [Current Role] with [X] years of experience in AI/ML. "
                f"I'm passionate about building intelligent systems that solve real problems. "
                f"I'm particularly drawn to {company_name if company_name else 'this opportunity'} because [specific reason]. "
                f"In my recent role, I led a team that [achievement], which taught me valuable lessons about [leadership/collaboration]."
            )
        elif interview_focus == "technical":
            question = (
                f"Hello! I'm {excitement}. This will be a technical deep-dive interview for the {target_role} position{company_context}. "
                f"We'll focus on your ML/AI engineering skills, system design, and problem-solving abilities. "
                f"Let's start with your background - what are your core technical strengths in AI/ML?"
            )
            sample_answer = (
                f"My core strengths are in [specific areas like NLP/Computer Vision/MLOps]. "
                f"I have extensive experience with PyTorch and TensorFlow, building models from scratch and optimizing them for production. "
                f"Recently, I [specific technical achievement with metrics], which involved [technologies used]. "
                f"I'm particularly interested in [specific technical area] because [reason]."
            )
        else:  # balanced
            question = (
                f"Hello! I'm {excitement}. {focus_mention}. "
                f"To begin, could you introduce yourself and tell me what attracts you to the {target_role} position{company_context}?"
            )
            sample_answer = (
                f"I'm an AI Engineer with [X] years of experience specializing in [domain]. "
                f"I've worked on projects ranging from [technical achievement] to [team/leadership achievement]. "
                f"What excites me about {company_name if company_name else 'this role'} is the opportunity to [specific reason related to company/role]. "
                f"I'm particularly skilled in [key technologies] and passionate about [area of interest]."
            )
        
        return {
            "question": question,
            "sample_answer": sample_answer
        }

    async def _generate_edge_tts(self, text, filename):
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(filename)

    def _generate_gtts(self, text, filename):
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

    def text_to_speech(self, text):
        """
        Generates audio with validation.
        """
        filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        
        # Try EdgeTTS first
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_edge_tts(text, filename))
            loop.close()
            
            if os.path.exists(filename) and os.path.getsize(filename) > 1024:
                return filename
            else:
                if os.path.exists(filename): 
                    os.remove(filename)
        except Exception as e:
            print(f"⚠️ EdgeTTS Failed: {e}")

        # Fallback to gTTS
        try:
            self._generate_gtts(text, filename)
            if os.path.exists(filename) and os.path.getsize(filename) > 1024:
                return filename
        except Exception as e:
            print(f"❌ gTTS Failed: {e}")
        
        return None
