import os

from .pdf import PDFParser
from .html import HTMLParser
from .markdown import MarkdownParser
from .docx import DOCXParser
from .txt import TXTParser


class ParserFactory:

    @staticmethod
    def get_parser(file_path: str):

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return PDFParser()

        elif ext in [".html", ".htm"]:
            return HTMLParser()

        elif ext in [".md", ".markdown"]:
            return MarkdownParser()

        elif ext == ".docx":
            return DOCXParser()

        elif ext == ".txt":
            return TXTParser()

        else:
            raise ValueError(f"Unsupported file type: {ext}")