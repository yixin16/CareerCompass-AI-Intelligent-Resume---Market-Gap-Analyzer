"""
Job Templates for Synthetic Data Generation
Used when live scraping yields limited results to ensure analysis can proceed.
"""

def get_job_templates():
    """Returns templates for generating synthetic job postings."""
    return {
        'data_scientist': {
            'titles': [
                'Data Scientist', 'Junior Data Scientist', 'Senior Data Scientist',
                'AI Data Scientist', 'Data Science Consultant'
            ],
            'requirements': [
                'Python, SQL, and experience with pandas/numpy',
                'Strong knowledge of Machine Learning algorithms',
                'Experience with deep learning frameworks (TensorFlow/PyTorch)',
                'Data visualization skills (Tableau/PowerBI/Matplotlib)',
                'Master\'s or PhD in Computer Science or related field',
                'Experience with AWS/Azure cloud platforms',
                'Statistical analysis and A/B testing'
            ],
            'responsibilities': [
                'Analyze large datasets to extract actionable insights',
                'Build and deploy predictive models',
                'Collaborate with engineering teams to implement ML solutions',
                'Present findings to stakeholders',
                'Design and implement A/B tests'
            ]
        },
        'machine_learning': {
            'titles': [
                'Machine Learning Engineer', 'ML Engineer', 'AI Engineer',
                'Deep Learning Specialist', 'Computer Vision Engineer'
            ],
            'requirements': [
                'Strong Python programming skills',
                'Experience with TensorFlow, PyTorch, or Keras',
                'Knowledge of Docker and Kubernetes',
                'Understanding of MLOps principles',
                'Experience with NLP or Computer Vision',
                'REST API development (FastAPI/Flask)',
                'Cloud deployment experience (AWS SageMaker)'
            ],
            'responsibilities': [
                'Design and build scalable ML pipelines',
                'Optimize models for production environments',
                'Deploy models using Docker and Kubernetes',
                'Maintain and monitor model performance',
                'Research state-of-the-art AI techniques'
            ]
        },
        'python_developer': {
            'titles': [
                'Python Developer', 'Backend Developer (Python)', 
                'Software Engineer', 'Full Stack Python Developer'
            ],
            'requirements': [
                'Proficiency in Python and Django/Flask',
                'Experience with SQL and NoSQL databases',
                'Knowledge of RESTful API design',
                'Familiarity with Git and CI/CD pipelines',
                'Understanding of front-end technologies (JS/React)',
                'Unit testing and debugging skills'
            ],
            'responsibilities': [
                'Develop robust backend services and APIs',
                'Write clean, maintainable, and efficient code',
                'Design database schemas',
                'Integrate user-facing elements with server-side logic',
                'Troubleshoot and debug applications'
            ]
        },
        'general_tech': {
            'titles': [
                'Software Engineer', 'Tech Lead', 'Solutions Architect'
            ],
            'requirements': [
                'Bachelor\'s degree in Computer Science',
                'Strong problem-solving skills',
                'Experience with Agile methodologies',
                'Excellent communication skills'
            ],
            'responsibilities': [
                'Develop high-quality software solutions',
                'Mentor junior developers',
                'Participate in code reviews',
                'Drive technical architecture decisions'
            ]
        }
    }