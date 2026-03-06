from abc import ABC, abstractmethod
from typing import Dict


class BaseParser(ABC):
    """
    所有 Parser 必须实现 parse()
    """

    @abstractmethod
    def parse(self, file_path: str) -> Dict:
        """
        返回统一结构:
        {
            "doc_id": str,
            "text": str,
            "blocks": List[dict],
            "metadata": dict
        }
        """
        
        pass