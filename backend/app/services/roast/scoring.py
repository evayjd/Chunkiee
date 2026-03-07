import json
from app.services.roast.llm import call_llm
from app.services.roast.prompts import SCORE_PROMPT


def generate_scores(persona_json: dict) -> dict:
    """
    根据 persona 生成娱乐性雷达图分数
    """

    prompt = SCORE_PROMPT.format(
        persona_json=json.dumps(persona_json, ensure_ascii=False, indent=2)
    )

    response = call_llm(prompt)

    try:
        result = json.loads(response)
    except Exception:
        # fallback
        result = {
            "scores": {
                "taste": 50,
                "mainstream_index": 50,
                "pretentious_level": 50,
                "nostalgia_bias": 50,
                "genre_loyalty": 50,
                "emotional_damage": 50
            },
            "diagnosis_rate": 88.8
        }

    return result