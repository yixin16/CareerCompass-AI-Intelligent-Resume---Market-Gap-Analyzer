"""
Intelligent Learning Roadmap Generator
Creates personalized learning paths with resources and timelines
"""

from typing import Dict, List, Tuple
from urllib.parse import quote_plus
from config import LEARNING_PLATFORMS, DOCUMENTATION_SITES
from utils.logger import logger


class LearningRoadmapGenerator:
    """Generates intelligent learning roadmaps with resources."""
    
    def __init__(self):
        self.skill_metadata = self._load_skill_metadata()
        self.learning_paths = self._load_learning_paths()
    
    def _load_skill_metadata(self) -> Dict:
        """Load detailed skill information including difficulty and time estimates."""
        return {
            # Programming Languages
            'python': {
                'category': 'Programming',
                'difficulty': 'Beginner',
                'learning_time_weeks': 4,
                'prerequisites': [],
                'related_skills': ['pandas', 'numpy', 'django', 'flask'],
                'certifications': ['PCEP', 'PCAP'],
                'key_concepts': ['syntax', 'data structures', 'OOP', 'functions']
            },
            'javascript': {
                'category': 'Programming',
                'difficulty': 'Beginner',
                'learning_time_weeks': 4,
                'prerequisites': ['html', 'css'],
                'related_skills': ['react', 'node.js', 'typescript'],
                'certifications': [],
                'key_concepts': ['ES6+', 'async/await', 'DOM manipulation']
            },
            'java': {
                'category': 'Programming',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 6,
                'prerequisites': [],
                'related_skills': ['spring boot', 'maven', 'gradle'],
                'certifications': ['OCA', 'OCP'],
                'key_concepts': ['OOP', 'collections', 'streams', 'multithreading']
            },
            'sql': {
                'category': 'Data',
                'difficulty': 'Beginner',
                'learning_time_weeks': 2,
                'prerequisites': [],
                'related_skills': ['postgresql', 'mysql', 'data modeling'],
                'certifications': [],
                'key_concepts': ['queries', 'joins', 'aggregations', 'indexing']
            },
            
            # ML/AI
            'machine learning': {
                'category': 'ML/AI',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 10,
                'prerequisites': ['python', 'statistics', 'linear algebra'],
                'related_skills': ['scikit-learn', 'tensorflow', 'pytorch'],
                'certifications': ['TensorFlow Developer', 'AWS ML Specialty'],
                'key_concepts': ['supervised learning', 'unsupervised learning', 'model evaluation']
            },
            'deep learning': {
                'category': 'ML/AI',
                'difficulty': 'Advanced',
                'learning_time_weeks': 12,
                'prerequisites': ['machine learning', 'python', 'calculus'],
                'related_skills': ['tensorflow', 'pytorch', 'neural networks'],
                'certifications': ['Deep Learning Specialization'],
                'key_concepts': ['neural networks', 'CNNs', 'RNNs', 'transformers']
            },
            'tensorflow': {
                'category': 'ML/AI',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 6,
                'prerequisites': ['python', 'machine learning'],
                'related_skills': ['keras', 'deep learning'],
                'certifications': ['TensorFlow Developer Certificate'],
                'key_concepts': ['tensors', 'models', 'training', 'deployment']
            },
            'pytorch': {
                'category': 'ML/AI',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 6,
                'prerequisites': ['python', 'machine learning'],
                'related_skills': ['deep learning', 'neural networks'],
                'certifications': [],
                'key_concepts': ['tensors', 'autograd', 'nn module', 'training loops']
            },
            'nlp': {
                'category': 'ML/AI',
                'difficulty': 'Advanced',
                'learning_time_weeks': 8,
                'prerequisites': ['machine learning', 'python'],
                'related_skills': ['transformers', 'bert', 'spacy'],
                'certifications': [],
                'key_concepts': ['tokenization', 'embeddings', 'transformers', 'LLMs']
            },
            
            # Cloud & DevOps
            'aws': {
                'category': 'Cloud',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 8,
                'prerequisites': ['linux', 'networking basics'],
                'related_skills': ['ec2', 's3', 'lambda', 'cloudformation'],
                'certifications': ['AWS Solutions Architect', 'AWS Developer'],
                'key_concepts': ['EC2', 'S3', 'IAM', 'VPC', 'Lambda']
            },
            'docker': {
                'category': 'DevOps',
                'difficulty': 'Beginner',
                'learning_time_weeks': 3,
                'prerequisites': ['linux basics'],
                'related_skills': ['kubernetes', 'docker-compose'],
                'certifications': ['Docker Certified Associate'],
                'key_concepts': ['containers', 'images', 'volumes', 'networking']
            },
            'kubernetes': {
                'category': 'DevOps',
                'difficulty': 'Advanced',
                'learning_time_weeks': 10,
                'prerequisites': ['docker', 'linux', 'networking'],
                'related_skills': ['helm', 'istio', 'prometheus'],
                'certifications': ['CKA', 'CKAD'],
                'key_concepts': ['pods', 'services', 'deployments', 'ingress']
            },
            
            # Data Engineering
            'spark': {
                'category': 'Data Engineering',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 6,
                'prerequisites': ['python', 'sql', 'scala (optional)'],
                'related_skills': ['hadoop', 'kafka', 'databricks'],
                'certifications': ['Databricks Certified'],
                'key_concepts': ['RDDs', 'DataFrames', 'Spark SQL', 'streaming']
            },
            'kafka': {
                'category': 'Data Engineering',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 4,
                'prerequisites': ['java', 'distributed systems'],
                'related_skills': ['spark', 'flink'],
                'certifications': ['Confluent Certified'],
                'key_concepts': ['topics', 'producers', 'consumers', 'streams']
            },
            'airflow': {
                'category': 'Data Engineering',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 3,
                'prerequisites': ['python', 'sql'],
                'related_skills': ['spark', 'etl'],
                'certifications': [],
                'key_concepts': ['DAGs', 'operators', 'scheduling', 'monitoring']
            },
            
            # Web Development
            'react': {
                'category': 'Web Development',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 5,
                'prerequisites': ['javascript', 'html', 'css'],
                'related_skills': ['redux', 'nextjs', 'typescript'],
                'certifications': [],
                'key_concepts': ['components', 'hooks', 'state', 'props', 'routing']
            },
            'django': {
                'category': 'Web Development',
                'difficulty': 'Intermediate',
                'learning_time_weeks': 4,
                'prerequisites': ['python', 'html', 'sql'],
                'related_skills': ['flask', 'rest api', 'postgresql'],
                'certifications': [],
                'key_concepts': ['MVT', 'ORM', 'templates', 'authentication']
            }
        }
    
    def _load_learning_paths(self) -> Dict:
        """Define learning paths for common career tracks."""
        return {
            'data_scientist': [
                ('python', 0),
                ('sql', 1),
                ('pandas', 2),
                ('machine learning', 3),
                ('deep learning', 6),
                ('tensorflow', 8)
            ],
            'ml_engineer': [
                ('python', 0),
                ('machine learning', 2),
                ('tensorflow', 6),
                ('docker', 8),
                ('kubernetes', 10),
                ('mlops', 12)
            ],
            'data_engineer': [
                ('python', 0),
                ('sql', 1),
                ('spark', 4),
                ('kafka', 7),
                ('airflow', 9),
                ('aws', 11)
            ],
            'web_developer': [
                ('html', 0),
                ('css', 1),
                ('javascript', 2),
                ('react', 5),
                ('node.js', 7),
                ('postgresql', 9)
            ]
        }
    
    def generate_learning_resources(self, skill: str) -> Dict:
        """
        Generate comprehensive learning resources for a skill.
        
        Args:
            skill: Skill name
            
        Returns:
            Dictionary with learning resources
        """
        skill_lower = skill.lower()
        metadata = self.skill_metadata.get(skill_lower, {})
        
        # Generate search-optimized query
        search_query = f"{skill} tutorial"
        
        resources = {
            'skill': skill,
            'difficulty': metadata.get('difficulty', 'Intermediate'),
            'estimated_time': self._format_learning_time(
                metadata.get('learning_time_weeks', 4)
            ),
            'online_courses': self._generate_course_links(skill),
            'documentation': self._generate_doc_links(skill_lower),
            'practice_platforms': self._generate_practice_links(skill_lower),
            'certifications': metadata.get('certifications', []),
            'prerequisites': metadata.get('prerequisites', []),
            'related_skills': metadata.get('related_skills', []),
            'key_concepts': metadata.get('key_concepts', []),
            'learning_path': self._generate_learning_path(skill_lower)
        }
        
        return resources
    
    def _generate_course_links(self, skill: str) -> List[Dict]:
        """Generate course platform links."""
        skill_query = quote_plus(skill)
        
        courses = [
            {
                'platform': 'Coursera',
                'url': f"{LEARNING_PLATFORMS['coursera']}{skill_query}",
                'description': 'University-backed courses with certificates',
                'pros': 'Structured, high quality, certificates',
                'pricing': 'Free to audit, $49-99/month for certificate'
            },
            {
                'platform': 'Udemy',
                'url': f"{LEARNING_PLATFORMS['udemy']}{skill_query}",
                'description': 'Practical, project-based courses',
                'pros': 'Affordable, lifetime access, frequent sales',
                'pricing': '$10-200 per course (often on sale)'
            },
            {
                'platform': 'edX',
                'url': f"{LEARNING_PLATFORMS['edx']}{skill_query}",
                'description': 'Professional certificates from top universities',
                'pros': 'Academic rigor, flexible schedules',
                'pricing': 'Free to audit, $50-300 for certificate'
            },
            {
                'platform': 'Pluralsight',
                'url': f"{LEARNING_PLATFORMS['pluralsight']}{skill_query}",
                'description': 'Technology skills platform',
                'pros': 'Comprehensive, skill assessments, paths',
                'pricing': '$29/month or $299/year'
            },
            {
                'platform': 'YouTube',
                'url': f"{LEARNING_PLATFORMS['youtube']}{skill_query} tutorial",
                'description': 'Free video tutorials',
                'pros': 'Free, diverse content, quick learning',
                'pricing': 'Free'
            }
        ]
        
        return courses
    
    def _generate_doc_links(self, skill: str) -> List[Dict]:
        """Generate official documentation links."""
        docs = []
        
        if skill in DOCUMENTATION_SITES:
            docs.append({
                'name': f'Official {skill.title()} Documentation',
                'url': DOCUMENTATION_SITES[skill],
                'type': 'Official Docs',
                'recommended': True
            })
        
        # Generic documentation resources
        docs.extend([
            {
                'name': f'{skill.title()} on MDN',
                'url': f'https://developer.mozilla.org/en-US/search?q={quote_plus(skill)}',
                'type': 'Reference',
                'recommended': skill in ['javascript', 'html', 'css', 'web']
            },
            {
                'name': f'{skill.title()} on DevDocs',
                'url': f'https://devdocs.io/{skill}',
                'type': 'Multi-doc aggregator',
                'recommended': True
            }
        ])
        
        return [d for d in docs if d.get('recommended', False)]
    
    def _generate_practice_links(self, skill: str) -> List[Dict]:
        """Generate practice platform links."""
        practice_platforms = []
        
        # Coding practice
        if skill in ['python', 'java', 'javascript', 'sql', 'algorithms']:
            practice_platforms.extend([
                {
                    'name': 'LeetCode',
                    'url': f'https://leetcode.com/problemset/?search={quote_plus(skill)}',
                    'type': 'Coding Challenges',
                    'difficulty': 'Beginner to Advanced'
                },
                {
                    'name': 'HackerRank',
                    'url': f'https://www.hackerrank.com/domains/{skill}',
                    'type': 'Skills Certification',
                    'difficulty': 'All Levels'
                }
            ])
        
        # Data Science
        if skill in ['machine learning', 'data science', 'python']:
            practice_platforms.extend([
                {
                    'name': 'Kaggle',
                    'url': f'https://www.kaggle.com/search?q={quote_plus(skill)}',
                    'type': 'Competitions & Datasets',
                    'difficulty': 'Intermediate to Advanced'
                },
                {
                    'name': 'DataCamp',
                    'url': f'https://www.datacamp.com/search?q={quote_plus(skill)}',
                    'type': 'Interactive Learning',
                    'difficulty': 'Beginner to Advanced'
                }
            ])
        
        # Web Development
        if skill in ['html', 'css', 'javascript', 'react']:
            practice_platforms.append({
                'name': 'FreeCodeCamp',
                'url': f"{LEARNING_PLATFORMS['freecodecamp']}{quote_plus(skill)}",
                'type': 'Interactive Challenges',
                'difficulty': 'Beginner to Intermediate'
            })
        
        # Cloud Platforms
        if skill in ['aws', 'azure', 'gcp']:
            practice_platforms.append({
                'name': f'{skill.upper()} Free Tier',
                'url': f'https://aws.amazon.com/free/' if skill == 'aws' else f'https://azure.microsoft.com/en-us/free/' if skill == 'azure' else 'https://cloud.google.com/free',
                'type': 'Hands-on Practice',
                'difficulty': 'All Levels'
            })
        
        return practice_platforms
    
    def _generate_learning_path(self, skill: str) -> List[Dict]:
        """Generate a week-by-week learning path."""
        metadata = self.skill_metadata.get(skill, {})
        weeks = metadata.get('learning_time_weeks', 4)
        prerequisites = metadata.get('prerequisites', [])
        key_concepts = metadata.get('key_concepts', [])
        
        path = []
        
        # Prerequisites week
        if prerequisites:
            path.append({
                'week': 0,
                'phase': 'Prerequisites',
                'focus': f'Review: {", ".join(prerequisites[:2])}',
                'goals': [f'Understand {p} basics' for p in prerequisites[:2]],
                'time_commitment': '3-5 hours/week'
            })
        
        # Learning phases
        phases_per_concept = max(1, weeks // max(len(key_concepts), 1))
        
        for i, concept in enumerate(key_concepts):
            week_num = (i * phases_per_concept) + 1
            path.append({
                'week': week_num,
                'phase': f'Phase {i+1}',
                'focus': concept.title(),
                'goals': [
                    f'Understand {concept}',
                    f'Complete 2-3 exercises on {concept}',
                    'Build a small project'
                ],
                'time_commitment': '5-8 hours/week'
            })
        
        # Final project
        path.append({
            'week': weeks,
            'phase': 'Final Project',
            'focus': 'Build a comprehensive project',
            'goals': [
                'Apply all learned concepts',
                'Deploy and document',
                'Add to portfolio'
            ],
            'time_commitment': '10+ hours'
        })
        
        return path
    
    def _format_learning_time(self, weeks: int) -> str:
        """Format learning time in human-readable format."""
        if weeks <= 4:
            return f'{weeks} weeks (1 month)'
        elif weeks <= 12:
            months = weeks // 4
            return f'{weeks} weeks ({months} months)'
        else:
            months = weeks // 4
            return f'{weeks} weeks ({months}+ months)'
    
    def create_personalized_roadmap(self, missing_skills: List[str],
                                   career_focus: str = 'data_scientist') -> Dict:
        """
        Create a personalized learning roadmap.
        
        Args:
            missing_skills: List of skills to learn
            career_focus: Career path focus
            
        Returns:
            Comprehensive learning roadmap
        """
        logger.info(f"Generating personalized roadmap for {len(missing_skills)} skills...")
        
        roadmap = {
            'career_focus': career_focus,
            'total_skills': len(missing_skills),
            'timeline': {},
            'priority_levels': {
                'critical': [],
                'high': [],
                'medium': []
            },
            'detailed_resources': []
        }
        
        # Categorize by priority
        for i, skill in enumerate(missing_skills):
            resources = self.generate_learning_resources(skill)
            
            if i < 3:
                priority = 'critical'
                resources['priority'] = 'CRITICAL - Learn First'
            elif i < 6:
                priority = 'high'
                resources['priority'] = 'HIGH - Learn Next'
            else:
                priority = 'medium'
                resources['priority'] = 'MEDIUM - Nice to Have'
            
            roadmap['priority_levels'][priority].append(skill)
            roadmap['detailed_resources'].append(resources)
        
        # Generate timeline
        roadmap['timeline'] = self._generate_timeline(missing_skills[:6])  # Top 6 skills
        
        # Calculate total time
        total_weeks = sum(
            self.skill_metadata.get(skill.lower(), {}).get('learning_time_weeks', 4)
            for skill in missing_skills[:6]
        )
        roadmap['total_estimated_time'] = self._format_learning_time(total_weeks)
        
        logger.info(f"✓ Roadmap created: {roadmap['total_estimated_time']} total learning time")
        
        return roadmap
    
    def _generate_timeline(self, skills: List[str]) -> Dict:
        """Generate a month-by-month learning timeline."""
        timeline = {}
        current_week = 0
        
        for skill in skills:
            skill_lower = skill.lower()
            metadata = self.skill_metadata.get(skill_lower, {})
            weeks = metadata.get('learning_time_weeks', 4)
            
            start_month = (current_week // 4) + 1
            end_month = ((current_week + weeks) // 4) + 1
            
            month_key = f"Month {start_month}" if start_month == end_month else f"Months {start_month}-{end_month}"
            
            if month_key not in timeline:
                timeline[month_key] = []
            
            timeline[month_key].append({
                'skill': skill,
                'duration': f'{weeks} weeks',
                'intensity': 'High' if weeks > 6 else 'Medium'
            })
            
            current_week += weeks
        
        return timeline