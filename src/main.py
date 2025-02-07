from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.services.llm import get_llm_response

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


@app.post("/api/v1/chat", response_model=MessageResponse)
async def chat_with_llm(request: MessageRequest):
    """Send a message to the LLM and get a response."""
    response = await get_llm_response(request.message)
    if response is None:
        raise HTTPException(status_code=500, detail="Failed to get LLM response")
    try:
        return MessageResponse.model_validate_json(response)
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
