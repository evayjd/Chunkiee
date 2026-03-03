import re
import unicodedata
from typing import Dict, List

class TextCleaner:
    """
    输入: parser 输出结构
    输出: 清洗后的相同结构
    """

    def __init__(self):
        # 中文字符
        self.cjk_re = re.compile(r'[\u4e00-\u9fa5]')

        # 中文句末标点
        self.cn_punc = ("。", "！", "？", "”", "；", "）", "：", "》")

        # 英文句末标点
        self.en_punc = (".", "!", "?", "\"", ";", ")", ":")

    # ========= 基础工具 =========

    def _is_chinese(self, char: str) -> bool:
        return bool(self.cjk_re.search(char))

    def normalize_unicode(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        return "".join(c for c in text if c.isprintable() or c in "\n\r\t")

    def remove_extra_blank_lines(self, text: str) -> str:
        return re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()

    # ========= 中英混排修复 =========

    def clean_mixed_spacing(self, text: str) -> str:
        # 1. 去除汉字之间的空格
        text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)

        # 2. 汉字与英文/数字之间加空格
        text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fa5])', r'\1 \2', text)

        # 3. 处理英文断词连字符
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        return text

    # ========= 智能断行合并 =========

    def smart_merge_lines(self, text: str) -> str:
        lines = text.split("\n")
        merged = []
        buffer = ""

        for line in lines:
            stripped = line.strip()

            if not stripped:
                if buffer:
                    merged.append(buffer)
                    buffer = ""
                continue

            if buffer:
                if not buffer.endswith(self.cn_punc + self.en_punc):

                    # 中文直接拼接
                    if self._is_chinese(buffer[-1]) or self._is_chinese(stripped[0]):
                        buffer += stripped
                    else:
                        buffer += " " + stripped
                else:
                    merged.append(buffer)
                    buffer = stripped
            else:
                buffer = stripped

        if buffer:
            merged.append(buffer)

        return "\n\n".join(merged)

    # ========= 单页清洗 =========

    def clean_page(self, text: str) -> str:
        text = self.normalize_unicode(text)
        text = self.smart_merge_lines(text)
        text = self.clean_mixed_spacing(text)
        text = self.remove_extra_blank_lines(text)
        return text

    # ========= 文档级入口 =========

    def clean_document(self, parsed_doc: Dict) -> Dict:
        """
        输入结构:
        {
            "text": str,
            "pages": [
                {"page": int, "content": str}
            ]
        }

        输出结构相同
        """

        cleaned_pages = []
        full_text = []

        for page in parsed_doc["pages"]:
            cleaned_text = self.clean_page(page["content"])

            cleaned_pages.append({
                "page": page["page"],
                "content": cleaned_text
            })

            full_text.append(cleaned_text)

        return {
            "text": "\n\n".join(full_text),
            "pages": cleaned_pages
        }