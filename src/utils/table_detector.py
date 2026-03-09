import re

def detect_table_name(prompt: str, schema: dict) -> str:
    prompt = prompt.lower()

    if not schema:
        return "generated_data"

    table_names = list(schema.keys())

    for table in table_names:

        singular = table[:-1] if table.endswith("s") else table

        if table in prompt or singular in prompt:
            return table

    return table_names[0]