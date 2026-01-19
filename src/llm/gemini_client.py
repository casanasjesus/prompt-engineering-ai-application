import os
from google import genai
from google.genai import types
import json

class GeminiClient:
    def __init__(self, temperature=0.5, max_tokens=1024):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_json(self, prompt: str) -> dict:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                response_mime_type="application/json",
            ),
        )

        # Intentar parsed
        if response.parsed:
            return response.parsed

        # Fallback a texto
        text = response.text

        try:
            return json.loads(text)
        except Exception:
            raise ValueError(f"Invalid JSON returned by LLM:\n{text}")
