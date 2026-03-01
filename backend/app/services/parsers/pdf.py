import fitz
from .base import BaseParser

class PDFParser(BaseParser):

    def parse(self, file_path: str):

        doc = fitz.open(file_path)

        full_text = []
        pages = []

        for page_index, page in enumerate(doc):
            text = page.get_text("text")

            pages.append({
                "page": page_index + 1,
                "content": text
            })

            full_text.append(text)

        return {
            "text": "\n".join(full_text),
            "pages": pages
        }