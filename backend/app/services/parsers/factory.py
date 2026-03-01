import os
from .pdf import PDFParser
from .markdown import MarkdownParser
from .html import HTMLParser


class ParserFactory:

    @staticmethod
    def create(file_path: str):

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return PDFParser()

        elif ext in [".md", ".markdown"]:
            return MarkdownParser()

        elif ext in [".html", ".htm"]:
            return HTMLParser()

        else:
            raise ValueError(f"Unsupported file type: {ext}")