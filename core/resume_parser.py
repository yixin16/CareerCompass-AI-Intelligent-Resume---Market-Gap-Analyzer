"""
Resume Parser
Extracts raw text from PDF, DOCX, and TXT files
"""

import re
from pathlib import Path
from typing import Optional
from utils.logger import logger
from config import RESUME_DIR

# Import libraries with error handling
try:
    from pdfminer.high_level import extract_text as extract_pdf_text
except ImportError:
    extract_pdf_text = None

try:
    import docx
except ImportError:
    docx = None


class ResumeParser:
    """Parses resume files into raw text."""

    @staticmethod
    def find_resume() -> Optional[Path]:
        """
        Find the first available resume in the sample_data directory.
        
        Returns:
            Path object of the resume or None
        """
        if not RESUME_DIR.exists():
            logger.error(f"Resume directory not found: {RESUME_DIR}")
            return None

        # Look for common document extensions
        supported_extensions = ['*.pdf', '*.docx', '*.doc', '*.txt']
        
        for ext in supported_extensions:
            files = list(RESUME_DIR.glob(ext))
            if files:
                # Return the first file found
                return files[0]
        
        return None

    @staticmethod
    def extract_text(file_path: Path) -> str:
        """
        Extract text from a resume file based on extension.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Cleaned raw text string
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return ""

        suffix = file_path.suffix.lower()
        logger.info(f"Parsing resume: {file_path.name}")

        try:
            text = ""
            if suffix == '.pdf':
                text = ResumeParser._parse_pdf(file_path)
            elif suffix == '.docx':
                text = ResumeParser._parse_docx(file_path)
            elif suffix == '.txt':
                text = ResumeParser._parse_txt(file_path)
            else:
                logger.error(f"Unsupported file format: {suffix}")
                return ""

            return ResumeParser._clean_text(text)

        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return ""

    @staticmethod
    def _parse_pdf(file_path: Path) -> str:
        """Parse PDF file."""
        if extract_pdf_text is None:
            raise ImportError("pdfminer.six is not installed. Run: pip install pdfminer.six")
        
        return extract_pdf_text(file_path)

    @staticmethod
    def _parse_docx(file_path: Path) -> str:
        """Parse Word (DOCX) file."""
        if docx is None:
            raise ImportError("python-docx is not installed. Run: pip install python-docx")
        
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

    @staticmethod
    def _parse_txt(file_path: Path) -> str:
        """Parse text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text (remove excess whitespace)."""
        if not text:
            return ""
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove null characters
        text = text.replace('\x00', '')
        
        return text.strip()