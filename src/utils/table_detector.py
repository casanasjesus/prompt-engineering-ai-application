import re

def detect_table_name(prompt: str, schema) -> str:
    prompt = prompt.lower()

    if not schema:
        return "generated_data"

    # CASE 1: JSON schema (dict)
    if isinstance(schema, dict):
        table_names = list(schema.keys())

    # CASE 2: SQL schema (str)
    elif isinstance(schema, str):
        matches = re.findall(r'create\s+table\s+(\w+)', schema, re.IGNORECASE)

        if not matches:
            return "generated_data"

        table_names = matches

    else:
        return "generated_data"

    for table in table_names:
        singular = table[:-1] if table.endswith("s") else table

        if table.lower() in prompt or singular.lower() in prompt:
            return table

    return table_names[0]