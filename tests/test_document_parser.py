from exceptions import DocumentParsingError
from unittest.mock import patch, MagicMock
import pytest


from utils.document_parser import DocumentParser


@pytest.fixture
def fake_file_path(tmp_path):
    return tmp_path / "file.txt"


def test_file_not_found():
    with pytest.raises(DocumentParsingError, match="File not found"):
        DocumentParser.extract_text("non_existent_file.txt")


def test_unsupported_extension(tmp_path):
    file_path = tmp_path / "file.xyz"
    file_path.write_text("dummy content")
    
    with pytest.raises(DocumentParsingError, match="Unsupported file type"):
        DocumentParser.extract_text(str(file_path))


def test_extract_text_txt_success(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("This is some text content.")
    
    result = DocumentParser.extract_text(str(file_path))
    assert "This is some text content." in result

def test_extract_text_txt_empty(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("    \n   ")
    
    with pytest.raises(DocumentParsingError, match="Text file is empty"):
        DocumentParser.extract_text(str(file_path))


@patch("docx.Document")
def test_extract_text_docx_success(mock_docx_class, tmp_path):
    file_path = tmp_path / "file.docx"
    file_path.touch()
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="Paragraph 1"), MagicMock(text="Paragraph 2")]
    mock_docx_class.return_value = mock_doc
    
    result = DocumentParser.extract_text(str(file_path))
    assert "Paragraph 1" in result
    assert "Paragraph 2" in result

@patch("docx.Document")
def test_extract_text_docx_empty(mock_docx_class, tmp_path):
    file_path = tmp_path / "file.docx"
    file_path.touch()
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="   "), MagicMock(text="")]
    mock_docx_class.return_value = mock_doc
    
    with pytest.raises(DocumentParsingError, match="No text content found in DOCX"):
        DocumentParser.extract_text(str(file_path))

@patch("pdfplumber.open")
def test_extract_text_pdf_success(mock_pdfplumber_open, tmp_path):
    file_path = tmp_path / "file.pdf"
    file_path.touch()
    page_mock = MagicMock()
    page_mock.extract_text.return_value = "PDF content"
    pdf_mock = MagicMock()
    pdf_mock.pages = [page_mock]
    mock_pdfplumber_open.return_value.__enter__.return_value = pdf_mock
    
    result = DocumentParser.extract_text(str(file_path))
    assert "PDF content" in result

@patch("pdfplumber.open")
def test_extract_text_pdf_empty(mock_pdfplumber_open, tmp_path):
    file_path = tmp_path / "file.pdf"
    file_path.touch()
    pdf_mock = MagicMock()
    pdf_mock.pages = []
    mock_pdfplumber_open.return_value.__enter__.return_value = pdf_mock
    
    with pytest.raises(DocumentParsingError, match="PDF file is empty"):
        DocumentParser.extract_text(str(file_path))

    
def test_clean_text_removes_extra_spaces():
    dirty_text = "  This  is   a \n test\n\n text "
    cleaned = DocumentParser._clean_text(dirty_text)
    assert cleaned == "This is a test text"