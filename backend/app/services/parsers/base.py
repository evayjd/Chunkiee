from abc import ABC, abstractmethod
from typing import Dict, List


class BaseParser(ABC):
    """
    所有 Parser 必须实现 parse()
    """

    @abstractmethod
    def parse(self, file_path: str) -> Dict:
        """
        返回统一结构:
        {
            "text": str,
            "pages": List[dict]
        }
        """
        pass