import os
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, temperature=0.5, max_tokens=5000):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.geminiModel = "gemini-2.5-flash"

    # --------------------------------------------------
    # MODULE 1 → DATA GENERATION
    # --------------------------------------------------

    def generate_json(self, prompt: str) -> dict:
        response = self.client.models.generate_content(
            model=self.geminiModel,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )

        print("\n" + "=" * 80)
        print("RAW GEMINI RESPONSE")
        print("=" * 80)

        if response:
            print(response)
        else:
            print("response is EMPTY")

        print("=" * 80 + "\n")

        if response.parsed:
            return response.parsed

        text = response.candidates[0].content.parts[0].text

        try:
            return text
        except Exception:
            raise ValueError(f"Invalid JSON returned by LLM:\n{text}")
        
    # --------------------------------------------------
    # MODULE 2 → NORMAL TEXT GENERATION
    # --------------------------------------------------

    def generate(self, prompt: str):
        response = self.client.models.generate_content(
            model=self.geminiModel,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )

        return response.candidates[0].content.parts[0].text

    # --------------------------------------------------
    # MODULE 2 → STREAMING (CHAT)
    # --------------------------------------------------

    def generate_stream(self, prompt: str):
        stream = self.client.models.generate_content_stream(
            model=self.geminiModel,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )

        for chunk in stream:
            if chunk.candidates:
                parts = chunk.candidates[0].content.parts

                if parts and hasattr(parts[0], "text"):
                    yield parts[0].text
