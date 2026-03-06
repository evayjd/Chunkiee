from docx import Document
import os

from .base import BaseParser


class DOCXParser(BaseParser):

    def parse(self, file_path: str):

        doc = Document(file_path)

        blocks = []
        full_text = []

        for para in doc.paragraphs:

            text = para.text.strip()

            if not text:
                continue

            style = para.style.name.lower()

            if "heading" in style:
                block_type = "title"
                level = 1
            else:
                block_type = "paragraph"
                level = None

            blocks.append({
                "type": block_type,
                "content": text,
                "metadata": {
                    "level": level
                }
            })

            full_text.append(text)

        return {
            "doc_id": os.path.basename(file_path),
            "text": "\n".join(full_text),
            "blocks": blocks,
            "metadata": {
                "source": file_path
            }
        }