import httpx
from typing import Dict, Any

from .config import LLM_BASE_URL, OPENROUTER_API_KEY

def call_llm(messages: list[Dict[str, str]], model: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"}
    }

    with httpx.Client(timeout=120) as client:
        response = client.post(
            f"{LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
