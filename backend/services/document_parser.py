import io
import re
from typing import Dict, List, Tuple, Any

class DocumentParser:
    """
    Extracts structured text from PDF/DOCX documents while strictly
    preserving page numbering and metadata for downstream citations.
    """
    
    @staticmethod
    def parse_pdf(file_bytes: bytes) -> Tuple[Dict[int, str], int]:
        """
        Parses a PDF file from bytes, returning a mapping of {page_number: text} and total pages.
        """
        pages_dict: Dict[int, str] = {}
        total_pages = 0
        
        # Method 1: PyMuPDF (fitz)
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            total_pages = len(doc)
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                pages_dict[page_num + 1] = text.strip()
            if pages_dict:
                return pages_dict, total_pages
        except Exception as e:
            pass
            
        # Method 2: pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                total_pages = len(pdf.pages)
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages_dict[idx + 1] = text.strip()
            if pages_dict:
                return pages_dict, total_pages
        except Exception as e:
            pass

        # Method 3: pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_dict[idx + 1] = text.strip()
            return pages_dict, total_pages
        except Exception as e:
            pass

        # Fallback raw decode
        raw_text = file_bytes.decode("utf-8", errors="ignore")
        return {1: raw_text}, 1

    @staticmethod
    def parse_docx(file_bytes: bytes) -> Tuple[Dict[int, str], int]:
        """
        Parses a DOCX file from bytes.
        """
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        full_text.append(row_text)
                        
            # Estimate pages based on 300 words per page
            combined = "\n\n".join(full_text)
            chunks = DocumentParser._split_into_pseudo_pages(combined, words_per_page=350)
            return {i + 1: chunk for i, chunk in enumerate(chunks)}, len(chunks)
        except Exception:
            # Fallback raw extraction from zip xml if docx package is unavailable
            raw = file_bytes.decode("utf-8", errors="ignore")
            clean_text = re.sub(r"<[^>]+>", " ", raw)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()
            chunks = DocumentParser._split_into_pseudo_pages(clean_text, words_per_page=350)
            return {i + 1: c for i, c in enumerate(chunks)}, max(1, len(chunks))

    @staticmethod
    def _split_into_pseudo_pages(text: str, words_per_page: int = 350) -> List[str]:
        words = text.split()
        if not words:
            return [""]
        pages = []
        for i in range(0, len(words), words_per_page):
            pages.append(" ".join(words[i:i + words_per_page]))
        return pages
