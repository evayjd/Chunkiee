from app.services.roast.llm import call_llm
from app.services.roast.prompts import PERSONA_PROMPT


def generate_persona(user_data):

    prompt = PERSONA_PROMPT.format(
        USER_DATA=user_data
    )

    response = call_llm(prompt)

    return response