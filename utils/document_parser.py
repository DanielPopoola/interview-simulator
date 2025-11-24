from pathlib import Path
from app.exceptions import DocumentParsingError


class DocumentParser:
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise DocumentParsingError(f"File not found: {file_path}")

        extension = path.suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise DocumentParsingError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
        
        try:
            if extension == '.pdf':
                text = cls._extract_from_pdf(file_path)
            elif extension == '.docx':
                text = cls._extract_from_docx(file_path)
            elif extension == '.txt':
                text = cls._extract_from_txt(file_path)
            else:
                raise DocumentParsingError(f"No parser for {extension}")
            
            return cls._clean_text(text)
        
        except DocumentParsingError:
            raise
        except Exception as e:
            raise DocumentParsingError(f"Failed to parse document: {str(e)}")
        

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        import pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages:
                    raise DocumentParsingError("PDF file is empty or corrupted")
                
                text_parts = [page.extract_text() for page in pdf.pages if page.extract_text()]
            
            full_text = '\n'.join(text_parts)

            if not full_text.strip():
                raise DocumentParsingError("No text content could be extracted from the PDF")
            
            return full_text
        except Exception as e:
            raise DocumentParsingError(f"Failed to read PDF with pdfplumber: {e}")

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        from docx import Document
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            full_text = '\n'.join(paragraphs)

            if not full_text.strip():
                raise DocumentParsingError("No text content found in DOCX")
            
            return full_text

        except Exception as e:
            raise DocumentParsingError(f"Invalid DOCX file: {e}")
        
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if not text.strip():
                raise DocumentParsingError("Text file is empty")
            
            return text
        
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                return text
            except Exception as e:
                raise DocumentParsingError(f"Failed to read text file: {e}")
            
    @staticmethod
    def _clean_text(text: str) -> str:
        text = ' '.join(text.split())
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]        
        return '\n'.join(lines)