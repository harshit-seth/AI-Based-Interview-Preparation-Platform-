from anthropic import AsyncAnthropic

from backend.config import settings


class LLMService:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        response = await self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=max_tokens or settings.MAX_TOKENS,
            temperature=temperature or settings.TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    async def generate_with_context(
        self,
        system_prompt: str,
        user_prompt: str,
        context: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        augmented_prompt = f"""Context:
{context}

Question:
{user_prompt}"""
        return await self.generate(system_prompt, augmented_prompt, max_tokens, temperature)


llm_service = LLMService()
