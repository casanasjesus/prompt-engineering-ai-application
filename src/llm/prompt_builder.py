import json

def build_generation_prompt(schema, user_prompt, rows_per_table=10):
    return f"""
You are a data generator.

Generate synthetic data that strictly follows this database schema:
{json.dumps(schema, indent=2)}

User instructions:
{user_prompt}

Rules:
- Output MUST be valid JSON
- Keys MUST be table names
- Each table MUST contain exactly {rows_per_table} rows
- Respect column types and foreign keys
- Do NOT include explanations
- Do NOT include markdown
- Output JSON ONLY
"""
