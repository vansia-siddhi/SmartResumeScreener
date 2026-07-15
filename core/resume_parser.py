# ============================================
# Resume Parser - Extract Text from Resumes
# ============================================

import os
import re
import logging
import PyPDF2
import docx
import pdfplumber
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ResumeParser:
    """Parse various resume formats"""

    def parse(self, filepath):
        """Parse resume based on file extension"""
        results = {
            'text': '',
            'name': '',
            'email': '',
            'phone': '',
            'word_count': 0,
            'filename': os.path.basename(filepath),
            'file_type': '',
            'pages': 0
        }

        file_ext = os.path.splitext(filepath)[1].lower()

        try:
            if file_ext == '.pdf':
                results['file_type'] = 'PDF'
                text, pages = self._parse_pdf(filepath)
                results['text'] = text
                results['pages'] = pages
            elif file_ext in ['.docx', '.doc']:
                results['file_type'] = 'DOCX'
                text = self._parse_docx(filepath)
                results['text'] = text
                results['pages'] = 1
            elif file_ext in ['.txt', '.md']:
                results['file_type'] = 'TXT'
                text = self._parse_text(filepath)
                results['text'] = text
                results['pages'] = 1
            else:
                text = self._parse_text(filepath)
                results['text'] = text
                results['file_type'] = 'Text'
                results['pages'] = 1

            # Clean text
            results['text'] = self._clean_text(results['text'])

            # Extract name, email, phone - IMPROVED
            results['name'] = self._extract_name_improved(results['text'])
            results['email'] = self._extract_email(results['text'])
            results['phone'] = self._extract_phone(results['text'])

            # Count words
            results['word_count'] = len(re.findall(r'\b\w+\b', results['text']))

        except Exception as e:
            logger.error(f"Resume parse error: {str(e)}")
            results['text'] = f"Error parsing resume: {str(e)}"

        return results

    def _parse_pdf(self, filepath):
        """Parse PDF file"""
        text = ""
        pages = 0

        try:
            with pdfplumber.open(filepath) as pdf:
                pages = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except:
            try:
                with open(filepath, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    pages = len(pdf_reader.pages)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as e:
                logger.error(f"PDF fallback error: {str(e)}")
                raise

        return text.strip(), pages

    def _parse_docx(self, filepath):
        """Parse DOCX file"""
        try:
            doc = docx.Document(filepath)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n".join(text)
        except Exception as e:
            logger.error(f"DOCX parse error: {str(e)}")
            raise

    def _parse_text(self, filepath):
        """Parse TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()

    def _clean_text(self, text):
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[^\w\s.,!?;:\-\n@]', '', text)
        return text.strip()

    def _extract_name_improved(self, text):
        """Extract name from text - IMPROVED"""
        if not text:
            return 'Unknown'

        lines = text.split('\n')

        # ============================================
        # METHOD 1: Look for common name patterns in first 5 lines
        # ============================================
        name_patterns = [
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',  # "John Doe" or "John Michael Doe"
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+)$',  # "John Michael Doe"
            r'^([A-Z][a-z]+\.?\s+[A-Z][a-z]+)$',  # "John M. Doe"
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$',  # 2-4 words all capitalized
        ]

        # Check first 10 lines for name
        for i in range(min(10, len(lines))):
            line = lines[i].strip()
            if not line:
                continue

            # Skip lines that are too short or too long
            if len(line) < 3 or len(line) > 50:
                continue

            # Skip lines with common resume headers
            skip_patterns = [
                r'^resume$', r'^curriculum vitae$', r'^cv$', r'^profile$',
                r'^contact$', r'^summary$', r'^objective$', r'^education$',
                r'^experience$', r'^skills$', r'^work$', r'^projects$'
            ]
            for skip in skip_patterns:
                if re.match(skip, line, re.IGNORECASE):
                    break
            else:
                # Check if line matches name pattern
                for pattern in name_patterns:
                    match = re.match(pattern, line)
                    if match:
                        return match.group(1)

        # ============================================
        # METHOD 2: Look for "Name:" label
        # ============================================
        name_label_match = re.search(r'Name\s*[:：]\s*([^\n]+)', text, re.IGNORECASE)
        if name_label_match:
            name = name_label_match.group(1).strip()
            if len(name) > 2 and len(name) < 50:
                return name

        # ============================================
        # METHOD 3: Look for name in the first line
        # ============================================
        first_line = lines[0].strip() if lines else ''
        if first_line and len(first_line) < 50:
            # Check if it looks like a name
            if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', first_line):
                return first_line

        # ============================================
        # METHOD 4: Look for LinkedIn or "Web Developer" pattern
        # ============================================
        # Sometimes name is like "Neha Khorasiya Web Developer"
        name_match = re.search(r'^([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:Web|Software|Developer|Engineer)', text, re.MULTILINE)
        if name_match:
            return name_match.group(1)

        return 'Unknown'

    def _extract_email(self, text):
        """Extract email from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return emails[0] if emails else ''

    def _extract_phone(self, text):
        """Extract phone from text"""
        patterns = [
            r'\+\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10}',
        ]
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return ''
