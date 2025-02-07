import json
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.services.llm import get_llm_response
from src.services.memory import add_message, get_history, start_conversation

app = FastAPI(title="TaskChunker API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class MessageRequest(BaseModel):
    message: str


class NextAction(BaseModel):
    description: str


class MessageResponse(BaseModel):
    next_actions: List[NextAction]
    conversation_id: str


@app.post("/api/v1/chat", response_model=MessageResponse)
async def chat_with_llm(
    request: MessageRequest,
    conversation_id: Optional[str] = Header(
        None, description="Conversation ID for maintaining context"
    ),
):
    """Send a message to the LLM and get a response."""
    # Initiate or continue an existing conversation.
    if not conversation_id:
        conv_id = start_conversation()
    else:
        conv_id = conversation_id

    # Append the user's message.
    add_message(conv_id, "user", request.message)

    # Build the full history to include previous context.
    history = get_history(conv_id)

    # Pass the full conversation history to the LLM.
    response = await get_llm_response(history)
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to get LLM response")

    try:
        # Parse the JSON response and add the conversation_id
        json_response = json.loads(response)
        json_response["conversation_id"] = conv_id

        return MessageResponse.model_validate(json_response)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse LLM response: {str(e)}"
        ) from e


@app.get("/")
async def hello_world():
    return {"message": "Hello, TaskChunker!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
