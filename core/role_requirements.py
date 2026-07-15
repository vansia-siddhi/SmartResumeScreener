# ============================================
# Role Requirements - Company Specific
# ============================================

ROLE_REQUIREMENTS = {
    'wordpress_developer': {
        'name': 'WordPress Developer',
        'required_skills': [
            'php', 'wordpress', 'woocommerce', 'elementor', 'custom theme', 'plugin development',
            'html', 'css', 'javascript', 'jquery', 'mysql', 'rest api', 'git',
            'acf', 'custom fields', 'wp-cli', 'child theme', 'responsive design'
        ],
        'nice_to_have': [
            'docker', 'linux', 'devops', 'aws', 'cloud', 'react', 'vue.js'
        ],
        'min_experience': 2,
        'education': ['B.Tech', 'BCA', 'MCA', 'B.Sc', 'M.Sc'],
        'certifications': ['WordPress Certification', 'WooCommerce Certification'],
        'weightage': {
            'skills': 40,
            'experience': 25,
            'education': 20,
            'certifications': 15
        }
    },
    'shopify_developer': {
        'name': 'Shopify Developer',
        'required_skills': [
            'shopify', 'liquid', 'react', 'vue', 'graphql', 'shopify api', 'theme customization',
            'app development', 'html', 'css', 'javascript', 'jquery', 'git', 'rest api'
        ],
        'nice_to_have': [
            'shopify plus', 'headless commerce', 'hydrogen', 'next.js', 'node.js'
        ],
        'min_experience': 2,
        'education': ['B.Tech', 'BCA', 'MCA', 'B.Sc', 'M.Sc'],
        'certifications': ['Shopify Certification', 'Shopify Partner'],
        'weightage': {
            'skills': 40,
            'experience': 25,
            'education': 20,
            'certifications': 15
        }
    },
    'business_development_engineer': {
        'name': 'Business Development Engineer',
        'required_skills': [
            'sales', 'business development', 'lead generation', 'client relationship', 'negotiation',
            'communication', 'presentation', 'crm', 'salesforce', 'market research', 'strategy',
            'account management', 'cold calling', 'email marketing', 'proposal writing'
        ],
        'nice_to_have': [
            'lead generation', 'marketing', 'digital marketing', 'seo', 'analytics'
        ],
        'min_experience': 2,
        'education': ['B.Tech', 'MBA', 'BBA', 'B.Com', 'M.Com'],
        'certifications': ['Sales Certification', 'CRM Certification'],
        'weightage': {
            'skills': 35,
            'experience': 30,
            'education': 20,
            'certifications': 15
        }
    },
    'dotnet_developer': {
        'name': '.Net Developer',
        'required_skills': [
            'c#', 'asp.net', '.net core', 'mvc', 'web api', 'entity framework', 'sql server',
            'azure', 'aws', 'git', 'docker', 'microservices', 'rest api', 'linq', 'html', 'css', 'javascript'
        ],
        'nice_to_have': [
            'kubernetes', 'ci/cd', 'terraform', 'react', 'angular', 'blazor'
        ],
        'min_experience': 2,
        'education': ['B.Tech', 'MCA', 'M.Sc'],
        'certifications': ['Microsoft Certified', 'Azure Developer'],
        'weightage': {
            'skills': 40,
            'experience': 25,
            'education': 20,
            'certifications': 15
        }
    },
    'python_ai_developer': {
        'name': 'Python/AI Developer',
        'required_skills': [
            'python', 'django', 'flask', 'machine learning', 'deep learning', 'nlp',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'rest api',
            'git', 'docker', 'aws', 'azure', 'matplotlib', 'seaborn', 'jupyter'
        ],
        'nice_to_have': [
            'computer vision', 'reinforcement learning', 'transformers', 'langchain', 'openai', 'kubernetes'
        ],
        'min_experience': 2,
        'education': ['B.Tech', 'M.Tech', 'Ph.D', 'MCA', 'M.Sc'],
        'certifications': ['AI/ML Certification', 'Google Cloud ML', 'AWS ML'],
        'weightage': {
            'skills': 40,
            'experience': 25,
            'education': 20,
            'certifications': 15
        }
    }
}

def get_all_roles():
    """Get all role names"""
    return [role['name'] for role in ROLE_REQUIREMENTS.values()]

def get_role_by_name(role_name):
    """Get role requirements by name"""
    for key, role in ROLE_REQUIREMENTS.items():
        if role['name'].lower() == role_name.lower():
            return role
    return None
