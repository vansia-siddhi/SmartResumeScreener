# ============================================
# Resume Engine - Core Analysis Logic
# ============================================

import logging

logger = logging.getLogger(__name__)

class ResumeEngine:
    """Core resume analysis engine"""

    def generate_insights(self, parsed_data, skills, match_results):
        """Generate insights from resume analysis"""
        insights = {
            'summary': '',
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'quick_stats': {},
            'best_roles': []
        }

        text = parsed_data.get('text', '')
        word_count = parsed_data.get('word_count', 0)
        name = parsed_data.get('name', 'Unknown')
        email = parsed_data.get('email', '')
        phone = parsed_data.get('phone', '')

        # Quick stats
        insights['quick_stats'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'word_count': word_count,
            'total_skills': skills.get('total_skills', 0),
            'best_score': match_results[0]['overall_score'] if match_results else 0,
            'best_role': match_results[0]['role_name'] if match_results else 'N/A'
        }

        # Summary
        insights['summary'] = f"{name} has {word_count} words in resume with {skills.get('total_skills', 0)} skills identified."

        # Best roles
        insights['best_roles'] = [
            {
                'role': r['role_name'],
                'score': r['overall_score'],
                'recommendation': r['recommendation']
            }
            for r in match_results[:3]
        ]

        # Strengths
        if match_results and match_results[0]['overall_score'] > 70:
            insights['strengths'].append(f"Strong match for {match_results[0]['role_name']} ({match_results[0]['overall_score']}%)")
        if skills.get('total_skills', 0) > 10:
            insights['strengths'].append(f"Has {skills['total_skills']} diverse skills")
        if word_count > 300:
            insights['strengths'].append("Detailed resume with sufficient content")
        if match_results and match_results[0]['skills_match']:
            insights['strengths'].append(f"Matched {len(match_results[0]['skills_match'])} skills for {match_results[0]['role_name']}")

        # Weaknesses
        if match_results and match_results[0]['overall_score'] < 50:
            insights['weaknesses'].append(f"Low match for all roles. Consider improving resume.")
        if skills.get('total_skills', 0) < 5:
            insights['weaknesses'].append("Very few skills identified")
        if word_count < 100:
            insights['weaknesses'].append("Resume is too short")
        if match_results and match_results[0]['skills_missing']:
            insights['weaknesses'].append(f"Missing {len(match_results[0]['skills_missing'])} skills for {match_results[0]['role_name']}")

        # Recommendations
        if match_results and match_results[0]['skills_missing']:
            insights['recommendations'].append({
                'category': 'Skills',
                'priority': 'high',
                'message': f"Add these skills: {', '.join(match_results[0]['skills_missing'][:3])}"
            })

        if match_results and match_results[0]['overall_score'] < 60:
            insights['recommendations'].append({
                'category': 'Improvement',
                'priority': 'high',
                'message': f"Tailor your resume for {match_results[0]['role_name']} role"
            })

        return insights
