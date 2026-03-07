import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"


def call_llm(prompt: str) -> str:

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    r = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    r.raise_for_status()

    data = r.json()

    return data.get("response", "").strip()