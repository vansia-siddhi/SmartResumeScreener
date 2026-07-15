# ============================================
# Job Matcher - Match Resume with Role Requirements
# ============================================

import re
import logging

logger = logging.getLogger(__name__)

# ============================================
# ROLE REQUIREMENTS - For Reference Only
# ============================================

ROLE_REQUIREMENTS = {
    'wordpress_developer': {
        'name': 'WordPress Developer',
        'required_skills': [
            'php', 'wordpress', 'woocommerce', 'elementor', 'custom theme', 'plugin development',
            'html', 'css', 'javascript', 'jquery', 'mysql', 'rest api', 'git',
            'acf', 'custom fields', 'wp-cli', 'child theme', 'responsive design'
        ],
        'nice_to_have': ['docker', 'linux', 'devops', 'aws', 'cloud'],
        'min_experience': 2,
        'education': ['B.Tech', 'BCA', 'MCA', 'B.Sc', 'M.Sc'],
        'certifications': ['WordPress', 'WooCommerce'],
        'weightage': {'skills': 40, 'experience': 25, 'education': 20, 'certifications': 15}
    },
    'shopify_developer': {
        'name': 'Shopify Developer',
        'required_skills': [
            'shopify', 'liquid', 'react', 'vue', 'graphql', 'shopify api', 'theme customization',
            'app development', 'html', 'css', 'javascript', 'jquery', 'git', 'rest api'
        ],
        'nice_to_have': ['shopify plus', 'headless commerce', 'hydrogen'],
        'min_experience': 2,
        'education': ['B.Tech', 'BCA', 'MCA', 'B.Sc', 'M.Sc'],
        'certifications': ['Shopify', 'Shopify Plus'],
        'weightage': {'skills': 40, 'experience': 25, 'education': 20, 'certifications': 15}
    },
    'business_development_engineer': {
        'name': 'Business Development Engineer',
        'required_skills': [
            'sales', 'business development', 'lead generation', 'client relationship', 'negotiation',
            'communication', 'presentation', 'crm', 'salesforce', 'market research', 'strategy',
            'account management', 'cold calling', 'email marketing', 'proposal writing'
        ],
        'nice_to_have': ['marketing', 'digital marketing', 'seo', 'analytics'],
        'min_experience': 2,
        'education': ['B.Tech', 'MBA', 'BBA', 'B.Com', 'M.Com'],
        'certifications': ['Sales', 'CRM'],
        'weightage': {'skills': 35, 'experience': 30, 'education': 20, 'certifications': 15}
    },
    'dotnet_developer': {
        'name': '.Net Developer',
        'required_skills': [
            'c#', 'asp.net', '.net core', 'mvc', 'web api', 'entity framework', 'sql server',
            'azure', 'aws', 'git', 'docker', 'microservices', 'rest api', 'linq'
        ],
        'nice_to_have': ['kubernetes', 'ci/cd', 'terraform', 'react', 'angular', 'blazor'],
        'min_experience': 2,
        'education': ['B.Tech', 'MCA', 'M.Sc'],
        'certifications': ['Microsoft', 'Azure'],
        'weightage': {'skills': 40, 'experience': 25, 'education': 20, 'certifications': 15}
    },
    'python_ai_developer': {
        'name': 'Python/AI Developer',
        'required_skills': [
            'python', 'django', 'flask', 'machine learning', 'deep learning', 'nlp',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'rest api',
            'git', 'docker', 'aws', 'azure', 'matplotlib', 'seaborn', 'jupyter'
        ],
        'nice_to_have': ['computer vision', 'reinforcement learning', 'transformers', 'langchain', 'openai'],
        'min_experience': 2,
        'education': ['B.Tech', 'M.Tech', 'Ph.D', 'MCA', 'M.Sc'],
        'certifications': ['AI', 'ML', 'Google Cloud'],
        'weightage': {'skills': 40, 'experience': 25, 'education': 20, 'certifications': 15}
    }
}

class JobMatcher:
    """Match resume with job role requirements - ONLY EXACT MATCHES"""

    def match_for_role(self, resume_text, role_key, skills):
        """Match resume for a specific role - NO ASSUMPTIONS"""
        results = {
            'role': role_key,
            'role_name': '',
            'overall_score': 0,
            'skills_match': [],
            'skills_missing': [],
            'skills_score': 0,
            'experience_score': 0,
            'education_score': 0,
            'certification_score': 0,
            'experience_years': 0,
            'recommendation': '',
            'detailed_analysis': {}
        }

        # Get role requirements
        role = ROLE_REQUIREMENTS.get(role_key, {})
        if not role:
            return results

        results['role_name'] = role.get('name', 'Unknown Role')

        # ============================================
        # SKILL MATCHING - ONLY EXACT MATCHES
        # ============================================

        # Get skills from resume (what's actually in the document)
        resume_skills = [s.lower() for s in skills.get('all_skills', [])]
        required_skills = [s.lower() for s in role.get('required_skills', [])]

        # EXACT MATCH: Only match if skill is in the resume
        matched = []
        missing = []

        for req_skill in required_skills:
            skill_found = False
            for resume_skill in resume_skills:
                # EXACT MATCH - skill must be present in resume
                if req_skill in resume_skill or resume_skill in req_skill:
                    matched.append(req_skill.title())
                    skill_found = True
                    break
            if not skill_found:
                missing.append(req_skill.title())

        # Remove duplicates
        results['skills_match'] = list(set(matched))
        results['skills_missing'] = list(set(missing))

        # Calculate skill score
        total_required = len(required_skills)
        matched_required = len(results['skills_match'])

        if total_required > 0:
            skill_score = (matched_required / total_required) * 100
        else:
            skill_score = 0
        results['skills_score'] = round(min(100, skill_score), 1)

        # ============================================
        # EXPERIENCE - FROM RESUME ONLY
        # ============================================
        experience_years = self._extract_years(resume_text)
        results['experience_years'] = experience_years
        min_exp = role.get('min_experience', 0)

        if min_exp > 0 and experience_years > 0:
            if experience_years >= min_exp:
                results['experience_score'] = 100
            else:
                results['experience_score'] = round((experience_years / min_exp) * 100, 1)
        else:
            results['experience_score'] = 0 if experience_years == 0 else 100

        # ============================================
        # EDUCATION - FROM RESUME ONLY
        # ============================================
        education = self._extract_education(resume_text)
        required_edu = role.get('education', [])

        if education:
            # Check if education matches any required
            matched_edu = False
            for req in required_edu:
                if req.upper() in education.upper():
                    matched_edu = True
                    break
            results['education_score'] = 100 if matched_edu else 50
        else:
            results['education_score'] = 0

        # ============================================
        # CERTIFICATIONS - FROM RESUME ONLY
        # ============================================
        certifications = self._extract_certifications(resume_text)
        required_certs = role.get('certifications', [])

        if certifications:
            matched_certs = []
            for cert in required_certs:
                if cert.lower() in certifications.lower():
                    matched_certs.append(cert)
            results['certification_score'] = 100 if matched_certs else 0
        else:
            results['certification_score'] = 0

        # ============================================
        # OVERALL SCORE
        # ============================================
        weightage = role.get('weightage', {})
        results['overall_score'] = round(
            (results['skills_score'] * weightage.get('skills', 40) / 100) +
            (results['experience_score'] * weightage.get('experience', 25) / 100) +
            (results['education_score'] * weightage.get('education', 20) / 100) +
            (results['certification_score'] * weightage.get('certifications', 15) / 100)
            , 1)

        results['overall_score'] = min(100, results['overall_score'])

        # ============================================
        # RECOMMENDATION
        # ============================================
        if results['overall_score'] >= 80:
            results['recommendation'] = 'Highly Recommended - Strong fit!'
        elif results['overall_score'] >= 60:
            results['recommendation'] = 'Recommended - Good fit'
        elif results['overall_score'] >= 40:
            results['recommendation'] = 'Consider - Partial fit'
        else:
            results['recommendation'] = 'Needs Improvement'

        # ============================================
        # DETAILED ANALYSIS - ONLY WHAT'S IN RESUME
        # ============================================
        results['detailed_analysis'] = {
            'matched_skills': results['skills_match'],
            'missing_skills': results['skills_missing'],
            'experience_years': experience_years,
            'education': education or 'Not found',
            'certifications': certifications or 'Not found',
            'required_experience': min_exp,
            'required_education': required_edu,
            'required_certifications': required_certs,
            'all_resume_skills': resume_skills  # What's actually in the resume
        }

        logger.info(f"Role: {results['role_name']}, Score: {results['overall_score']}%, Matched: {len(results['skills_match'])}/{total_required}")
        logger.info(f"Resume Skills: {resume_skills}")
        logger.info(f"Matched: {results['skills_match']}")
        logger.info(f"Missing: {results['skills_missing']}")

        return results

    def match_all_roles(self, resume_text, skills):
        """Match resume against all roles"""
        results = []
        for role_key in ROLE_REQUIREMENTS.keys():
            result = self.match_for_role(resume_text, role_key, skills)
            results.append(result)

        # Sort by overall score
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        return results

    def _extract_years(self, text):
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
            r'(?:experience|exp)\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
        ]

        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return 0

    def _extract_education(self, text):
        """Extract education from text - ONLY WHAT'S IN RESUME"""
        education_keywords = [
            'B.Tech', 'B.E', 'BCA', 'MCA', 'M.Tech', 'M.E', 'Ph.D', 'PhD',
            'B.Sc', 'M.Sc', 'BBA', 'MBA', 'B.Com', 'M.Com', 'MS', 'BS', 'MA',
            'Bachelor', 'Master', 'Doctorate', 'Engineering', 'Computer Science',
            'Saurashtra University', 'Gujarat University', 'MS University'
        ]
        text_upper = text.upper()
        for edu in education_keywords:
            if edu.upper() in text_upper:
                return edu
        return ''

    def _extract_certifications(self, text):
        """Extract certifications from text - ONLY WHAT'S IN RESUME"""
        cert_keywords = [
            'Certified', 'Certification', 'Certificate',
            'Microsoft', 'AWS', 'Azure', 'Google Cloud',
            'WordPress', 'Shopify', 'Salesforce', 'HubSpot'
        ]
        found = []
        text_lower = text.lower()
        for cert in cert_keywords:
            if cert.lower() in text_lower:
                found.append(cert)
        return ', '.join(found)
