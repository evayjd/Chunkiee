import re
import uuid
from typing import Dict, List, Tuple


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 800,
        overlap: int = 120
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

        # 识别标题
        self.heading_re = re.compile(
            r"^(#{1,6}\s+.*|[0-9]+\.\s+.*|[0-9]+\.[0-9]+\s+.*)",
            re.MULTILINE
        )

        # 句子切分
        self.sentence_re = re.compile(r'(?<=[.!?。！？])\s+')

        # code block
        self.codeblock_re = re.compile(r"```.*?```", re.DOTALL)

        # markdown table
        self.table_line_re = re.compile(r"\|.*\|")

    # code block helpers

    def _extract_code_blocks(self, text: str):
        blocks = []
        for m in self.codeblock_re.finditer(text):
            blocks.append((m.start(), m.end()))
        return blocks

    def _is_inside_block(self, index, blocks):
        for s, e in blocks:
            if s <= index < e:
                return True
        return False


    # section split

    def split_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        返回:
        [(section_title, section_text)]
        """

        headings = list(self.heading_re.finditer(text))

        if not headings:
            return [("root", text)]

        sections = []

        for i, h in enumerate(headings):

            title = h.group().strip()
            start = h.end()

            if i + 1 < len(headings):
                end = headings[i + 1].start()
            else:
                end = len(text)

            content = text[start:end].strip()

            sections.append((title, content))

        return sections



    # paragraph split

    def split_paragraphs(self, text: str):

        paras = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paras if p.strip()]



    # sentence split


    def split_sentences(self, text: str):

        sents = re.split(self.sentence_re, text)
        return [s.strip() for s in sents if s.strip()]


 # chunk builder


    def build_chunks(self, units: List[str]) -> List[str]:

        chunks = []
        current = ""

        for u in units:

            if len(current) + len(u) < self.chunk_size:
                current += " " + u
            else:

                if current:
                    chunks.append(current.strip())

                # fallback: very long unit
                if len(u) > self.chunk_size:
                    parts = self.recursive_split(u)
                    chunks.extend(parts)
                    current = ""
                else:
                    current = u

        if current:
            chunks.append(current.strip())

        return chunks




    def recursive_split(self, text: str) -> List[str]:

        chunks = []
        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start = end - self.overlap

        return chunks


#page chuking

    def chunk_page(
        self,
        page_text: str,
        doc_id: str,
        page_number: int
    ) -> List[Dict]:

        sections = self.split_sections(page_text)

        page_chunks = []
        chunk_index = 0

        for section_title, sec_text in sections:

            paragraphs = self.split_paragraphs(sec_text)

            units = []

            for p in paragraphs:

                if len(p) > self.chunk_size:
                    sentences = self.split_sentences(p)
                    units.extend(sentences)
                else:
                    units.append(p)

            chunks = self.build_chunks(units)

            for c in chunks:

                page_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "doc_id": doc_id,
                    "page": page_number,
                    "section": section_title,  # 新增 metadata
                    "chunk_index": chunk_index,
                    "text": c.strip()
                })

                chunk_index += 1

        return page_chunks

#文档chuking

    def chunk_document(
        self,
        cleaned_doc: Dict,
        doc_id: str
    ) -> List[Dict]:

        all_chunks = []

        for page in cleaned_doc["pages"]:

            page_chunks = self.chunk_page(
                page_text=page["content"],
                doc_id=doc_id,
                page_number=page["page"]
            )

            all_chunks.extend(page_chunks)

        return all_chunks