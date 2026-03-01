from .pdf import parse_pdf
from .markdown import parse_markdown
from .html import parse_html
import os


def parse_document(file_path: str):

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path)

    elif ext in [".md", ".markdown"]:
        return parse_markdown(file_path)

    elif ext in [".html", ".htm"]:
        return parse_html(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")