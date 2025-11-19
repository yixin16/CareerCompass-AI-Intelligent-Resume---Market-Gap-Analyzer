"""
Skill Categories
Comprehensive skill taxonomy with 100+ technical and soft skills
"""

SKILL_CATEGORIES = {
    'programming': {
        'skills': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go',
            'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',
            'sql', 'c', 'perl', 'shell scripting', 'bash', 'powershell'
        ],
        'aliases': {'js': 'javascript', 'ts': 'typescript', 'py': 'python'}
    },
    'ml_ai': {
        'skills': [
            'machine learning', 'deep learning', 'nlp', 'natural language processing',
            'computer vision', 'neural networks', 'tensorflow', 'pytorch', 'keras',
            'scikit-learn', 'xgboost', 'lightgbm', 'transformers', 'bert', 'gpt',
            'llm', 'large language model', 'cnn', 'rnn', 'lstm', 'reinforcement learning',
            'generative ai', 'stable diffusion', 'huggingface', 'langchain', 'opencv'
        ],
        'aliases': {'ml': 'machine learning', 'dl': 'deep learning', 'cv': 'computer vision'}
    },
    'data': {
        'skills': [
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'cassandra',
            'elasticsearch', 'spark', 'apache spark', 'hadoop', 'kafka', 'airflow',
            'etl', 'data warehouse', 'bigquery', 'snowflake', 'redshift', 'pandas',
            'numpy', 'data analysis', 'data visualization', 'tableau', 'power bi',
            'looker', 'dbt', 'presto', 'hive', 'data engineering', 'data modeling'
        ],
        'aliases': {'postgres': 'postgresql', 'mongo': 'mongodb'}
    },
    'cloud_devops': {
        'skills': [
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins',
            'ci/cd', 'terraform', 'ansible', 'devops', 'lambda', 'ec2', 's3',
            'cloudformation', 'azure devops', 'github actions', 'gitlab ci', 'argocd',
            'helm', 'istio', 'prometheus', 'grafana', 'elk stack', 'datadog'
        ],
        'aliases': {'k8s': 'kubernetes', 'aws lambda': 'lambda'}
    },
    'web_mobile': {
        'skills': [
            'react', 'angular', 'vue', 'svelte', 'node.js', 'nodejs', 'django',
            'flask', 'fastapi', 'spring boot', 'express', 'nextjs', 'nuxt', 'gatsby',
            'rest api', 'graphql', 'grpc', 'html', 'css', 'sass', 'tailwind',
            'responsive design', 'react native', 'flutter', 'swift', 'kotlin',
            'ios', 'android', 'mobile development', 'pwa'
        ],
        'aliases': {'node': 'node.js', 'react.js': 'react', 'vue.js': 'vue'}
    },
    'tools_platforms': {
        'skills': [
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
            'jupyter', 'vs code', 'intellij', 'pycharm', 'linux', 'unix', 'bash',
            'vim', 'agile', 'scrum', 'kanban', 'postman', 'swagger', 'figma'
        ],
        'aliases': {}
    },
    'soft_skills': {
        'skills': [
            'leadership', 'team management', 'communication', 'problem solving',
            'project management', 'stakeholder management', 'mentoring', 'collaboration',
            'strategic thinking', 'cross-functional', 'presentation', 'technical writing',
            'coaching', 'conflict resolution', 'time management', 'critical thinking'
        ],
        'aliases': {}
    },
    'specialized': {
        'skills': [
            'blockchain', 'web3', 'smart contracts', 'solidity', 'cryptocurrency',
            'cybersecurity', 'penetration testing', 'siem', 'soc', 'iot', 'edge computing',
            '5g', 'quantum computing', 'robotics', 'embedded systems', 'microservices',
            'event-driven', 'distributed systems', 'high availability', 'scalability'
        ],
        'aliases': {}
    }
}