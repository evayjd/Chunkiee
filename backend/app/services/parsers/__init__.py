import os
from .pdf import PDFParser
from .markdown import MarkdownParser
from .html import HTMLParser
from .docx import DOCXParser
from .txt import TXTParser

def parse_document(file_path: str):
    """
    根据文件后缀名，自动选择对应的 Parser 类进行解析
    """
    # 获取文件后缀（转为小写）
    ext = os.path.splitext(file_path)[1].lower()

    # 1. 处理 PDF
    if ext == ".pdf":
        # 实例化类 PDFParser()，然后调用它的 parse 方法
        return PDFParser().parse(file_path)

    # 2. 处理 Markdown
    elif ext in [".md", ".markdown"]:
        return MarkdownParser().parse(file_path)

    # 3. 处理 HTML
    elif ext in [".html", ".htm"]:
        return HTMLParser().parse(file_path)

    # 4. 处理 Word
    elif ext == ".docx":
        return DocxParser().parse(file_path)

    # 5. 处理 纯文本
    elif ext == ".txt":
        return TxtParser().parse(file_path)

    else:
        raise ValueError(f"暂时不支持的文件类型: {ext}")