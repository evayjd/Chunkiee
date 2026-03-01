import re
import unicodedata
from typing import Dict, List
import fitz
from collections import Counter

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)

#去多余空格
def remove_extra_spaces(text: str) -> str:
    text=re.sub(r"[ \t]+", " ", text)
    text=re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()

#合并pdf中被强制断行的句子（行尾不是句号，下一行不是大写开头）
def merge_broken_lines(text: str) -> str:
    lines=text.split("\n")
    merged=[]
    buffer=""
    
    for line in lines:
        stripped=line.strip()
        if not stripped:
            if buffer:
                merged.append(buffer)
                buffer=""
            continue
        
        if buffer:
            if not buffer.endswith(".", "?", "!", ":", ";"):
                buffer+=" "+stripped
            else:
                merged.append(buffer)
                buffer=stripped
                
        else:
            buffer=stripped
            
        if buffer:
            merged.append(buffer)
            
        return "\n\n".join(merged)
    
    


