import json
import re

def parse_llm_response(response):
    # Caso ideal
    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        raise ValueError("Invalid LLM response type")

    # EXTRAER BLOQUE JSON del texto
    match = re.search(r"\{[\s\S]*\}", response)

    if not match:
        raise ValueError("No JSON object found in LLM response")

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON structure: {e}\nRaw JSON:\n{json_text}")
