import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import uuid

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log') if os.path.exists('logs') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

for directory in ['uploads', 'reports', 'data', 'logs']:
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create directory {directory}: {str(e)}")

try:
    from core.resume_engine import ResumeEngine
    from core.resume_parser import ResumeParser
    from core.skill_extractor import SkillExtractor
    from core.job_matcher import JobMatcher
    from core.report_generator import ReportGenerator

    logger.info("SUCCESS: Core modules imported successfully")
except ImportError as e:
    logger.error(f"ERROR: Failed to import core modules: {str(e)}")
    sys.exit(1)

resume_engine = ResumeEngine()
resume_parser = ResumeParser()
skill_extractor = SkillExtractor()
job_matcher = JobMatcher()
report_generator = ReportGenerator()

# ============================================
# Routes
# ============================================

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/analyze')
def analyze():
    try:
        return render_template('analyze.html')
    except Exception as e:
        logger.error(f"Error rendering analyze page: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/report/<report_id>')
def view_report(report_id):
    try:
        return render_template('report.html', report_id=report_id)
    except Exception as e:
        logger.error(f"Error rendering report page: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'development')
    })

# ============================================
# API Endpoints
# ============================================

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """Analyze uploaded resume"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get form data
        job_title = request.form.get('job_title', '')
        job_description = request.form.get('job_description', '')
        role_key = request.form.get('role', 'auto')

        # Save file
        file_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + str(uuid.uuid4())[:8]
        filename = file.filename
        filepath = os.path.join('uploads', f'{file_id}_{filename}')
        file.save(filepath)

        logger.info(f"Processing resume: {filename}")

        # Parse resume
        parsed_data = resume_parser.parse(filepath)

        if not parsed_data or not parsed_data.get('text'):
            return jsonify({'error': 'Could not extract text from resume'}), 400

        # Extract skills
        skills = skill_extractor.extract(parsed_data['text'])

        # Match with job description
        if role_key == 'auto':
            match_results = job_matcher.match_all_roles(parsed_data['text'], skills)
        else:
            match_results = [job_matcher.match_for_role(parsed_data['text'], role_key, skills)]

        # Generate insights
        insights = resume_engine.generate_insights(parsed_data, skills, match_results)

        # Prepare results
        results = {
            'file_id': file_id,
            'filename': filename,
            'filepath': filepath,
            'job_title': job_title,
            'job_description': job_description,
            'selected_role': role_key,
            'parsed_data': parsed_data,
            'skills': skills,
            'match_results': match_results,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }

        # Save report
        report_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        try:
            report_path = f'reports/resume_{report_id}.json'
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save report: {str(e)}")

        return jsonify({
            'success': True,
            'report_id': report_id,
            'results': results
        })

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def list_reports():
    """List all reports"""
    try:
        reports = []
        if os.path.exists('reports'):
            for filename in os.listdir('reports'):
                if filename.startswith('resume_') and filename.endswith('.json'):
                    filepath = os.path.join('reports', filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            report_id = filename.replace('resume_', '').replace('.json', '')

                            # Get file name (original uploaded file name)
                            file_name = data.get('filename', 'Unknown')

                            # Get candidate name (if extracted)
                            parsed = data.get('parsed_data', {})
                            candidate_name = parsed.get('name', '')

                            # Get match results
                            match_results = data.get('match_results', [])
                            best_score = 0
                            best_role = 'N/A'
                            matched_skills = 0

                            if match_results:
                                best_match = max(match_results, key=lambda x: x.get('overall_score', 0))
                                best_score = best_match.get('overall_score', 0)
                                best_role = best_match.get('role_name', 'N/A')
                                matched_skills = len(best_match.get('skills_match', []))

                            reports.append({
                                'id': report_id,
                                'name': file_name,  # Original file name
                                'candidate_name': candidate_name,  # Extracted name (might be empty)
                                'score': best_score,
                                'role': best_role,
                                'skills_matched': matched_skills,
                                'timestamp': data.get('timestamp', '')
                            })
                    except Exception as e:
                        logger.warning(f"Error reading report {filename}: {str(e)}")
                        continue

        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({'reports': reports})

    except Exception as e:
        logger.error(f"Reports list error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report"""
    try:
        report_path = f'reports/resume_{report_id}.json'
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404

        with open(report_path, 'r') as f:
            report_data = json.load(f)

        return jsonify(report_data)

    except Exception as e:
        logger.error(f"Report fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-pdf/<report_id>', methods=['GET'])
def export_pdf(report_id):
    """Export report as PDF"""
    try:
        report_path = f'reports/resume_{report_id}.json'
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404

        with open(report_path, 'r') as f:
            report_data = json.load(f)

        pdf_path = f'reports/resume_{report_id}.pdf'
        report_generator.export_pdf(report_data, pdf_path)

        if os.path.exists(pdf_path):
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f'resume_screening_{report_id}.pdf'
            )
        else:
            return jsonify({'error': 'PDF generation failed'}), 500

    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# Main
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"""
    ========================================
    Smart Resume Screener
    ========================================
    Running on: http://localhost:{port}
    Version: 1.0.0
    Status: Ready
    ========================================
    """)

    app.run(debug=debug, host='0.0.0.0', port=port)
