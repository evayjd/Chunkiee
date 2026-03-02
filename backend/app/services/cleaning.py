import re
import unicodedata
import fitz  
from collections import Counter
from typing import List, Set

class PDFTextCleaner:
    def __init__(self):
        # 匹配中文字符
        self.cjk_re = re.compile(r'[\u4e00-\u9fa5]')
        # 中文结束标点
        self.cn_punc = ("。", "！", "？", "”", "；", "）", "：", "》")
        # 英文结束标点
        self.en_punc = (".", "!", "?", "\"", ";", ")", ":")

    def _is_chinese(self, char: str) -> bool:
        """判断单个字符是否为中文"""
        return bool(self.cjk_re.search(char))

    def normalize_unicode(self, text: str) -> str:
        """Unicode 标准化并处理非打印字符"""
        text = unicodedata.normalize("NFKC", text)
        # 去除非打印字符（保留换行和缩进）
        return "".join(c for c in text if c.isprintable() or c in "\n\r\t")

    def detect_repeated_elements(self, doc: fitz.Document, threshold: float = 0.8) -> Set[str]:
        """
        启发式识别页眉页脚：
        统计所有页面顶部和底部出现的行，如果出现频率超过 threshold，则判定为干扰项。
        """
        line_counts = Counter()
        total_pages = len(doc)
        if total_pages < 3: return set() # 总页数太少不执行此逻辑

        for page in doc:
            lines = [l.strip() for l in page.get_text().split('\n') if l.strip()]
            if not lines: continue
            # 记录每页的前 2 行和后 2 行
            headers_footers = lines[:2] + lines[-2:]
            for item in headers_footers:
                line_counts[item] += 1
        
        return {text for text, count in line_counts.items() if count >= total_pages * threshold}

    def clean_mixed_spacing(self, text: str) -> str:
        """修复中英混排中的空格问题"""
        # 1. 去除汉字间的空格
        text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)
        # 2. 汉字与英文/数字之间增加空格
        text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z0-9])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fa5])', r'\1 \2', text)
        # 3. 处理英文连字符 
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        return text

    def smart_merge_lines(self, text: str) -> str:
        """智能合并断行：区分中文和英文逻辑"""
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
                # 如果 buffer 结尾不是句号等结束符
                if not buffer.endswith(self.cn_punc + self.en_punc):
                    # 判断合并方式：如果涉及中文，直接贴合；纯英文则加空格
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

    def process_pdf(self, input_path: str, output_path: str = None):
        """核心处理流程"""
        doc = fitz.open(input_path)
        common_elements = self.detect_repeated_elements(doc)
        
        final_content = []
        
        for page_num, page in enumerate(doc):
            # 获取页面原始文本
            raw_text = page.get_text()
            lines = raw_text.split('\n')
            
            # 过滤页眉页脚
            filtered_lines = [l for l in lines if l.strip() not in common_elements]
            page_text = "\n".join(filtered_lines)
            
            # 执行清洗逻辑
            text = self.normalize_unicode(page_text)
            text = self.smart_merge_lines(text)
            text = self.clean_mixed_spacing(text)
            
            # 标记页码 
            page_marker = f"\n\n--- [Page {page_num + 1}] ---\n\n"
            final_content.append(page_marker + text)

        full_text = "".join(final_content)
        
        # 最后去除多余的空行
        full_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", full_text).strip()

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"处理完成！已保存至: {output_path}")
        
        return full_text
