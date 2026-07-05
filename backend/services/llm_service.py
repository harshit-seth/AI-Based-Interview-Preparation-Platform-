import json
from urllib import request as urllib_request

from backend.config import settings


class LLMService:
    def __init__(self):
        self.model = settings.GEMINI_MODEL
        self.api_key = settings.GEMINI_API_KEY

    def _gemini_request(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }
        req = urllib_request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        resp = urllib_request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        return self._gemini_request(
            system_prompt,
            user_prompt,
            max_tokens or settings.MAX_TOKENS,
            temperature or settings.TEMPERATURE,
        )

    async def generate_with_context(
        self,
        system_prompt: str,
        user_prompt: str,
        context: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        augmented = f"Context:\n{context}\n\nQuestion:\n{user_prompt}"
        return await self.generate(system_prompt, augmented, max_tokens, temperature)


llm_service = LLMService()
