import json
from app.services.roast.llm import call_llm
from app.services.roast.prompts import ROAST_PROMPT


def write_roast(persona_json: dict, user_data: dict) -> str:
    """
    生成最终 roast 文案
    """

    prompt = ROAST_PROMPT.format(
        persona_json=json.dumps(persona_json, ensure_ascii=False, indent=2),
        user_data=json.dumps(user_data, ensure_ascii=False, indent=2)
    )

    response = call_llm(prompt)

    return response.strip()