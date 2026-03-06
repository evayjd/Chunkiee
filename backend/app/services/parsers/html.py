from bs4 import BeautifulSoup
import os

from .base import BaseParser


class HTMLParser(BaseParser):

    def parse(self, file_path: str):

        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        blocks = []
        full_text = []

        for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):

            text = element.get_text(strip=True)

            if not text:
                continue

            if element.name.startswith("h"):
                level = int(element.name[1])
                block_type = "title"
            elif element.name == "li":
                block_type = "list"
                level = None
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