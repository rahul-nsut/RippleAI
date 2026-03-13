import os
import requests
from typing import Dict, Any, List


from app.config import settings

class OpenRouterLLMClient:
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Confluence AI Suggestions"
        }

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generic chat call.
        Returns parsed JSON response from LLM (not string).
        """

        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=90
        )

        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            return self._safe_json_parse(content)
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse LLM JSON output: {e}\nRaw output:\n{content}"
            )

    @staticmethod
    def _safe_json_parse(text: str) -> Dict[str, Any]:
        """
        Strict JSON parsing.
        LLM must return JSON only.
        """
        import json

        text = text.strip()

        # Defensive: remove accidental markdown fences
        if text.startswith("```"):
            text = text.strip("`")
            text = text[text.find("{"): text.rfind("}") + 1]

        return json.loads(text)
