from bs4 import BeautifulSoup
from .base import BaseParser


class HTMLParser(BaseParser):

    def parse(self, file_path: str):

        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()

        soup = BeautifulSoup(raw, "lxml")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        return {
            "text": text,
            "pages": [
                {
                    "page": 1,
                    "content": text
                }
            ]
        }