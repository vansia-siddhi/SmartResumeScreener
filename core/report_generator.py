# ============================================
# Report Generator - PDF Generation
# ============================================

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate PDF reports"""

    def export_pdf(self, report_data, filepath):
        """Export report as PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                alignment=TA_CENTER,
                spaceAfter=30,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph('Resume Screening Report', title_style))
            story.append(Spacer(1, 10))

            # Metadata
            meta_style = ParagraphStyle(
                'MetaStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#7f8c8d'),
                alignment=TA_CENTER,
                spaceAfter=20
            )

            filename = report_data.get('filename', 'Unknown')
            candidate_name = report_data.get('parsed_data', {}).get('name', 'Unknown')
            timestamp = report_data.get('timestamp', datetime.now().isoformat())

            story.append(Paragraph(f'<b>Candidate:</b> {candidate_name}', meta_style))
            story.append(Paragraph(f'<b>Resume:</b> {filename}', meta_style))
            story.append(Paragraph(f'<b>Generated:</b> {timestamp}', meta_style))
            story.append(Spacer(1, 20))

            # Score
            match_results = report_data.get('match_results', {})
            score = match_results.get('overall_score', 0)
            score_color = '#27ae60' if score >= 80 else '#f39c12' if score >= 60 else '#e74c3c'

            score_style = ParagraphStyle(
                'ScoreStyle',
                parent=styles['Heading1'],
                fontSize=48,
                textColor=colors.HexColor(score_color),
                alignment=TA_CENTER,
                spaceAfter=5,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f'{score}%', score_style))

            score_label_style = ParagraphStyle(
                'ScoreLabelStyle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#34495e'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            story.append(Paragraph('Match Score', score_label_style))
            story.append(Spacer(1, 10))

            # Recommendation
            recommendation = match_results.get('recommendation', '')
            if recommendation:
                story.append(Paragraph(recommendation, styles['Normal']))
                story.append(Spacer(1, 20))

            # Candidate Info
            parsed_data = report_data.get('parsed_data', {})
            story.append(Paragraph('Candidate Information', styles['Heading2']))
            story.append(Spacer(1, 10))

            info_data = [
                ['Name', parsed_data.get('name', 'Unknown')],
                ['Email', parsed_data.get('email', 'N/A')],
                ['Phone', parsed_data.get('phone', 'N/A')],
                ['Word Count', str(parsed_data.get('word_count', 0))],
            ]

            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))

            # Skills
            skills = report_data.get('skills', {})
            if skills:
                story.append(Paragraph('Skills', styles['Heading2']))
                story.append(Spacer(1, 10))

                all_skills = skills.get('all_skills', [])
                if all_skills:
                    skills_text = ', '.join(all_skills[:20])
                    story.append(Paragraph(skills_text, styles['Normal']))
                story.append(Spacer(1, 20))

            # Skills Match
            match = match_results.get('skills_match', [])
            missing = match_results.get('skills_missing', [])

            if match or missing:
                story.append(Paragraph('Skill Analysis', styles['Heading2']))
                story.append(Spacer(1, 10))

                if match:
                    story.append(Paragraph('<b>Matched Skills:</b> ' + ', '.join(match[:10]), styles['Normal']))
                if missing:
                    story.append(Paragraph('<b>Missing Skills:</b> ' + ', '.join(missing[:10]), styles['Normal']))
                story.append(Spacer(1, 20))

            # Insights
            insights = report_data.get('insights', {})

            if insights.get('strengths'):
                story.append(Paragraph('Strengths', styles['Heading2']))
                story.append(Spacer(1, 10))
                for strength in insights['strengths']:
                    story.append(Paragraph(f'• {strength}', styles['Normal']))
                story.append(Spacer(1, 10))

            if insights.get('weaknesses'):
                story.append(Paragraph('Areas for Improvement', styles['Heading2']))
                story.append(Spacer(1, 10))
                for weakness in insights['weaknesses']:
                    story.append(Paragraph(f'• {weakness}', styles['Normal']))
                story.append(Spacer(1, 10))

            if insights.get('recommendations'):
                story.append(Paragraph('Recommendations', styles['Heading2']))
                story.append(Spacer(1, 10))
                for rec in insights['recommendations']:
                    story.append(Paragraph(f'• {rec.get("message", "")}', styles['Normal']))

            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            raise
