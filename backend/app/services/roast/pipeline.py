from app.services.roast.persona import generate_persona
from app.services.roast.scoring import generate_scores
from app.services.roast.tags import generate_tags
from app.services.roast.roast_writer import write_roast


def roast_pipeline(user_data):

    persona = generate_persona(user_data)

    scores = generate_scores(persona)

    tags = generate_tags(persona)

    roast_text = write_roast(persona, user_data)

    return {
        "persona": persona,
        "scores": scores,
        "tags": tags,
        "roast": roast_text
    }