def detect_prompt_injection(text):

    forbidden = [
        "ignore previous instructions",
        "system prompt",
        "drop table",
        "delete database",
        "reveal prompt"
    ]

    text = text.lower()

    for word in forbidden:
        if word in text:
            return True

    return False