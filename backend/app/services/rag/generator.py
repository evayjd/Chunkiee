import requests
from typing import Dict


class Generator:
    """
    负责调用 Ollama LLM 生成最终回答
    """

    def __init__(
        self,
        model: str = "qwen2.5:3b",
        url: str = "http://localhost:11434/api/generate",
        timeout: int = 60
    ):
        """
        初始化生成器

        model: 使用的 Ollama 模型
        url: Ollama API 地址
        timeout: 请求超时时间
        """

        self.model = model
        self.url = url
        self.timeout = timeout

        # 为防止 prompt 过长导致模型拒绝
        self.max_prompt_chars = 12000

    def _build_prompt(self, prompt: Dict) -> str:
        """
        构建完整 prompt
        """

        system_prompt = prompt.get("system", "")
        user_prompt = prompt.get("user", "")

        full_prompt = f"""
System:
{system_prompt}

User:
{user_prompt}
"""

        # 如果 prompt 太长进行截断
        if len(full_prompt) > self.max_prompt_chars:
            full_prompt = full_prompt[-self.max_prompt_chars:]

        return full_prompt

    def generate(
        self,
        prompt: Dict,
        context_data: Dict
    ) -> Dict:
        """
        调用 Ollama 生成答案
        """

        full_prompt = self._build_prompt(prompt)

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9
            }
        }

        try:

            # 发送请求
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )

            # 检查 HTTP 状态
            response.raise_for_status()

            data = response.json()

            # Ollama 返回字段
            answer = data.get("response", "")

            if not answer:
                answer = "LLM returned empty response."

            answer = answer.strip()

        except Exception as e:

            # 打印错误，方便 debug
            print("LLM generation error:", str(e))

            answer = "Error: failed to generate answer."

        return {
            "answer": answer,
            "citations": context_data.get("citations", [])
        }


# 创建单例（避免重复初始化）
_generator = Generator()


def generate_answer(
    prompt: Dict,
    context_data: Dict
) -> Dict:
    """
    RAG 系统对外调用接口
    """

    return _generator.generate(
        prompt,
        context_data
    )