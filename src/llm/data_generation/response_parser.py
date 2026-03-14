import json
import re

def parse_llm_response(response):
    """
    Parser ultra-robusto para respuestas Gemini:
    - Ignora comillas triples
    - Ignora markdown ```json
    - Ignora texto antes/después
    - Extrae el primer JSON válido
    """
    
    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        raise ValueError(f"Invalid LLM response type: {type(response)}")

    text = response.strip()
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    match = re.search(r"\{[\s\S]*\}", text)

    if not match:
        raise ValueError(
            "No JSON object found in LLM response.\n"
            f"RAW RESPONSE:\n{text}"
        )

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON structure: {e}\n"
            f"EXTRACTED JSON:\n{json_text}"
        )