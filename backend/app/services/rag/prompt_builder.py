from typing import Dict

class PromptBuilder:
    def __init__(self):

        self.system_prompt = """
You are an AI assistant that answers questions using provided context.

Rules:
1. Use ONLY the provided context to answer the question.
2. If the answer is not in the context, say you don't know.
3. Cite sources using [number] from the context.
4. Be concise and accurate.
"""

    def build_prompt(
        self,
        question: str,
        context_data: Dict
    ) -> Dict:

        context = context_data.get("context", "")

        user_prompt = f"""
Context:
{context}

Question:
{question}

Answer:
"""

        return {
            "system": self.system_prompt.strip(),
            "user": user_prompt.strip()
        }


# singleton
_prompt_builder = PromptBuilder()


def build_prompt(
    question: str,
    context_data: Dict
) -> Dict:
    """
    对外接口
    """

    return _prompt_builder.build_prompt(
        question,
        context_data
    )