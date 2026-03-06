import os

from .base import BaseParser


class TXTParser(BaseParser):

    def parse(self, file_path: str):

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        blocks = []

        paragraphs = text.split("\n")

        for p in paragraphs:

            p = p.strip()

            if not p:
                continue

            blocks.append({
                "type": "paragraph",
                "content": p,
                "metadata": {}
            })

        return {
            "doc_id": os.path.basename(file_path),
            "text": text,
            "blocks": blocks,
            "metadata": {
                "source": file_path
            }
        }