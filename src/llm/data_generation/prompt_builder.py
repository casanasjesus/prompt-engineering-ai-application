import json

def build_generation_prompt(schema, user_prompt, rows_per_table=10):
    return f"""
You are a system that ONLY outputs raw JSON.

If you output anything other than JSON, the response will be rejected.

Database schema:
{json.dumps(schema, indent=2)}

User request:
{user_prompt}

RULES (MANDATORY):
- Output MUST start with {{ and end with }}
- Do NOT add any text before or after JSON
- Do NOT explain anything
- Do NOT wrap in markdown
- JSON must be syntactically valid

OUTPUT FORMAT:
{{
  "data": [
    {{
      "id": 1,
      "name": "example"
    }}
  ]
}}
"""
