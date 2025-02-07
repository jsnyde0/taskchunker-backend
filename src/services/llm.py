import os
from typing import Optional

from openai import AsyncOpenAI


async def get_llm_response(message: str) -> Optional[str]:
    """Get a structured response from the LLM model."""
    try:
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        system_prompt = """The user wants to determine the next action to take.
        Provide exactly 3 options for a specific, actionable next step using the
        Getting Things Done (GTD) methodology.
        Format your response as a JSON object with the following structure:
        {
            "next_actions": [
                { "description": "First specific, actionable step" },
                { "description": "Second specific, actionable step" },
                { "description": "Third specific, actionable step" }
            ]
        }"""

        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        return None
