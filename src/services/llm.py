import os
from typing import Optional

from openai import AsyncOpenAI


async def get_llm_response(message: str) -> Optional[str]:
    """Get a response from the LLM model."""
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": message}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return None
