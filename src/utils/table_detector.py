import re

def detect_table_name(prompt: str) -> str:
    """
    Detect table name from prompt.
    Examples:
    'generate employees data' -> employees
    'create departments records' -> departments
    'generate companies' -> companies
    """

    prompt = prompt.lower()

    patterns = [
        r"generate\s+(\w+)",
        r"create\s+(\w+)",
        r"make\s+(\w+)",
        r"build\s+(\w+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt)
        if match:
            return match.group(1)

    return "generated_data"