import re
from .base import BaseParser


class MarkdownParser(BaseParser):

    def _strip_md(self, text: str) -> str:
        text = re.sub(r"#+", "", text)#去标题
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)#去代码块
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)#去链接
        return text

    def parse(self, file_path: str):

        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()

        clean = self._strip_md(raw)

        return {
            "text": clean,
            "pages": [
                {
                    "page": 1,
                    "content": clean
                }
            ]
        }