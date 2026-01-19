import json

def parse_llm_response(response):
    if isinstance(response, dict):
        return response

    if isinstance(response, str):
        return json.loads(response)

    raise ValueError("Invalid LLM response format")
