# ============================================
# Skill Extractor - Extract Skills from Resume
# ============================================

import re
import logging

logger = logging.getLogger(__name__)

class SkillExtractor:
    """Extract skills from resume text"""

    def __init__(self):
        self.skill_categories = {
            'Programming Languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'php', 'typescript', 'scala', 'perl', 'r', 'matlab',
                'sql', 'html', 'css', 'bash', 'shell', 'powershell'
            ],
            'Frameworks & Libraries': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js',
                'express', 'jquery', 'bootstrap', 'tailwind', 'tensorflow', 'pytorch',
                'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn'
            ],
            'Databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'oracle', 'sql server', 'mariadb', 'dynamodb', 'firebase', 'sqlite'
            ],
            'Cloud & DevOps': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
                'github', 'gitlab', 'terraform', 'ansible', 'prometheus', 'grafana',
                'linux', 'nginx', 'apache', 'ci/cd', 'devops'
            ],
            'Data Science & AI': [
                'machine learning', 'deep learning', 'nlp', 'computer vision',
                'data analysis', 'data visualization', 'statistics', 'probability',
                'linear algebra', 'calculus', 'optimization', 'reinforcement learning'
            ],
            'Soft Skills': [
                'leadership', 'communication', 'problem solving', 'teamwork',
                'project management', 'agile', 'scrum', 'critical thinking',
                'time management', 'adaptability', 'creativity', 'emotional intelligence'
            ]
        }

    def extract(self, text):
        """Extract skills from text"""
        results = {
            'all_skills': [],
            'categorized': {},
            'total_skills': 0
        }

        text_lower = text.lower()
        found_skills = set()

        for category, skills in self.skill_categories.items():
            category_skills = []
            for skill in skills:
                # Check for exact match or with variations
                if self._skill_exists(skill, text_lower):
                    category_skills.append(skill.title())
                    found_skills.add(skill.title())
            if category_skills:
                results['categorized'][category] = category_skills

        results['all_skills'] = sorted(list(found_skills))
        results['total_skills'] = len(found_skills)

        return results

    def _skill_exists(self, skill, text):
        """Check if skill exists in text"""
        # Check exact match
        if skill in text:
            return True

        # Check with word boundaries
        patterns = [
            r'\b' + re.escape(skill) + r'\b',
            r'\b' + re.escape(skill) + r'[\s,]',
            r'[\s,.]' + re.escape(skill) + r'\b'
        ]

        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def extract_keywords(self, text):
        """Extract keywords (simplified)"""
        # Get common technical terms
        technical_terms = [
            'developer', 'engineer', 'architect', 'analyst', 'manager',
            'design', 'development', 'testing', 'deployment', 'integration',
            'performance', 'security', 'scalability', 'reliability', 'maintenance'
        ]

        found = []
        text_lower = text.lower()
        for term in technical_terms:
            if term in text_lower:
                found.append(term)

        return found
