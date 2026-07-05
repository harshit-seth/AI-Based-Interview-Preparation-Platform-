import json
from urllib import request as urllib_request

import anthropic

from backend.config import settings


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.gemini_model = settings.GEMINI_MODEL
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.claude_model = settings.CLAUDE_MODEL
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY

    def _gemini_request(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
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

    def _claude_request(self, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        msg = client.messages.create(
            model=self.claude_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        mt = max_tokens or settings.MAX_TOKENS
        tmp = temperature or settings.TEMPERATURE
        if self.provider == "claude":
            return self._claude_request(system_prompt, user_prompt, mt, tmp)
        return self._gemini_request(system_prompt, user_prompt, mt, tmp)

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
