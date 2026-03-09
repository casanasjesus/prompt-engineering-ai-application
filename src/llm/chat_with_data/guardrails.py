def detect_prompt_injection(text):

    forbidden = [
        "ignore previous instructions",
        "system prompt",
        "reveal prompt",
        "drop table",
        "delete database"
    ]

    text = text.lower()

    for word in forbidden:
        if word in text:
            return True

    return False