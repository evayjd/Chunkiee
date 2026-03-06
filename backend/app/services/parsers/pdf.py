import fitz
import os
from typing import Dict

from .base import BaseParser


class PDFParser(BaseParser):

    def parse(self, file_path: str) -> Dict:

        doc = fitz.open(file_path)

        blocks = []
        full_text = []

        for page_index, page in enumerate(doc):

            text = page.get_text()
            full_text.append(text)

            paragraphs = text.split("\n")

            for p in paragraphs:

                p = p.strip()

                if not p:
                    continue

                blocks.append({
                    "type": "paragraph",
                    "content": p,
                    "metadata": {
                        "page": page_index + 1
                    }
                })

        return {
            "doc_id": os.path.basename(file_path),
            "text": "\n".join(full_text),
            "blocks": blocks,
            "metadata": {
                "source": file_path
            }
        }