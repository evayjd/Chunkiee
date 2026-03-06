import re
import unicodedata
from collections import Counter
from typing import Dict, List, Set


class TextCleaner:
    """
    通用多语言文本清洗器，支持中文、英文、法语。
    """

    def __init__(self, min_length: int = 5, symbol_threshold: float = 0.5):
        # 基础配置
        self.min_length = min_length #太短删掉
        self.symbol_threshold = symbol_threshold#符号占比太多删掉
        
        # 正则：匹配中文字符
        self.cjk_re = re.compile(r'[\u4e00-\u9fa5]')
        # 正则：典型的目录/页码点
        self.toc_pattern = re.compile(r"\.{3,}\s*\d+$")
        # 正则：西文重复空格
        self.multi_space_re = re.compile(r'[ ]{2,}')

    # ------------------------------------------------
    # 核心处理模块
    # ------------------------------------------------

    def normalize_unicode(self, text: str) -> str:
        """规范化 Unicode"""
        text = unicodedata.normalize("NFKC", text)
        return "".join(c for c in text if c.isprintable() or c in "\n\t")

    def clean_spacing(self, text: str) -> str:
        """
        混合语言空格清理。
        """
        # 1. 基础处理：统一将多个空格合并为一个
        text = self.multi_space_re.sub(' ', text)
        # 2. 如果包含中文，应用中西文混合排版逻辑
        if self.cjk_re.search(text):
            # 移除汉字之间的空格
            text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)
            # 在汉字与英数之间加空格
            text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z0-9])', r'\1 \2', text)
            text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fa5])', r'\1 \2', text)

        # 3. 英语法语标点基础修正
        # 此处不强制法语的特殊标点空格（如 : 前的空格），以保持文本原意。
        text = re.sub(r'\s+([,.!?;])', r'\1', text) 

        return text.strip()


    # 过滤与噪声检测
  

    def is_noise(self, text: str) -> bool:
        """
        检测噪声块。
        法语支持：\w 在 Unicode 模式下会自动包含 é, à, ç 等字符。
        """
        s = text.strip()
        if len(s) < self.min_length:
            return True
        if s.isdigit():
            return True

        # 符号占比检测
        symbols = re.findall(r'[^\w\s]', s, re.UNICODE)
        if len(s) > 0 and len(symbols) / len(s) > self.symbol_threshold:
            return True
            
        return False


    # 重复模式识别 


    def get_repeated_patterns(self, blocks: List[Dict]) -> Set[str]:
        """识别高频出现的模式，屏蔽数字干扰。"""
        pattern_counter = Counter()
        text_to_pattern = []

        for block in blocks:
            content = block["content"].strip()
            if not content: continue
            
            # 将数字屏蔽，法语中常见的 "Page 1", "Page 2" 会被统一识别
            pattern = re.sub(r'\d+', '[NUM]', content)
            pattern_counter[pattern] += 1
            text_to_pattern.append((content, pattern))

        threshold = max(3, len(blocks) // 20)
        repeated_pats = {p for p, c in pattern_counter.items() if c > threshold}
        return {content for content, pat in text_to_pattern if pat in repeated_pats}


    # 执行清理

    def clean_blocks(self, blocks: List[Dict]) -> List[Dict]:
        intermediate = []
        seen = set()

        for block in blocks:
            b = block.copy()
            # 顺序：标准化 -> 空格清理 -> 基础过滤
            txt = self.normalize_unicode(b["content"])
            txt = self.clean_spacing(txt)

            if not txt or self.is_noise(txt) or self.toc_pattern.search(txt):
                continue

            if txt in seen:
                continue
            
            seen.add(txt)
            b["content"] = txt
            intermediate.append(b)

        # 移除高频重复的页眉页脚
        repeated = self.get_repeated_patterns(intermediate)
        return [b for b in intermediate if b["content"] not in repeated]

    def clean_document(self, parsed_doc: Dict) -> Dict:
        cleaned = self.clean_blocks(parsed_doc.get("blocks", []))
        return {
            "doc_id": parsed_doc.get("doc_id"),
            "text": "\n\n".join(b["content"] for b in cleaned),
            "blocks": cleaned,
            "metadata": parsed_doc.get("metadata", {}).copy()
        }