import json
from app.services.roast.llm import call_llm
from app.services.roast.prompts import TAG_PROMPT
def generate_tags(persona_json: dict) -> list:

    prompt = TAG_PROMPT.format(
        persona_json=json.dumps(persona_json, ensure_ascii=False, indent=2)
    )

    response = call_llm(prompt)

    try:
        result = json.loads(response)
        return result.get("tags", [])
    except Exception:
        return ["失败"]