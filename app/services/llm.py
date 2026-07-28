import httpx
import json
from app.core.config import settings

class LLMService:
    def __init__(self, model_name: str = "meta-llama/llama-3.3-70b-instruct:free"):
        self.model_name = model_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "sk-or-v1-your-key-here":
            if "Developer" in system_prompt:
                return "```python\ndef calculate_sum(a, b):\n    return a + b\n```"
            return "Plan: Implement calculate_sum function taking two parameters and returning their sum."

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

llm_service = LLMService()
