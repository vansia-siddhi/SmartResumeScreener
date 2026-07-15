# Smart Resume Screener

## Overview
An AI-powered resume screening system that analyzes resumes, scores candidates, and matches them to job descriptions.

## Features
- 📄 Resume parsing (PDF, DOCX, TXT)
- 🎯 Skill extraction and matching
- 📊 Candidate scoring
- 📈 Job description analysis
- 📄 PDF reports

## Installation

```bash
# Clone repository
git clone <your-repo>
cd SmartResumeScreener

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Run application
python app.py
