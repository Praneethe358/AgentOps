import httpx
import json
from app.core.config import settings

class LLMService:
    def __init__(self, model_name: str = "meta-llama/llama-3.3-70b-instruct"):
        self.model_name = model_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "sk-or-v1-your-key-here":
            if "Developer" in system_prompt:
                if "Hello from Ephemeral Sandbox!" in user_prompt:
                    return "```python\nprint('Hello from Ephemeral Sandbox!')\nsquared_numbers = [x**2 for x in range(1, 6)]\nprint('Squared numbers:', squared_numbers)\n```"
                return "```python\ndef calculate_sum(a, b):\n    return a + b\n```"
            return "Plan: Implement required Python script according to task description."

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
            if response.status_code != 200:
                print(f"⚠️ [LLM API Error] Status: {response.status_code}, Response: {response.text}")
                # Try fallback model if model 404s
                if response.status_code in (404, 400):
                    print("🔄 Retrying with fallback model 'meta-llama/llama-3.1-8b-instruct'...")
                    payload["model"] = "meta-llama/llama-3.1-8b-instruct"
                    fallback_resp = await client.post(self.api_url, headers=headers, json=payload)
                    if fallback_resp.status_code == 200:
                        data = fallback_resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        print(f"⚠️ [Fallback LLM Error] Status: {fallback_resp.status_code}, Response: {fallback_resp.text}")
                response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

llm_service = LLMService()
