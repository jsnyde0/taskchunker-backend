import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.services.llm import get_llm_response
from src.services.memory import (
    add_message,
    find_task_in_tree,
    get_history,
    get_task_tree,
    save_task_tree,
    start_conversation,
)

app = FastAPI(title="TaskChunker API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["x-conversation-id"],  # Expose our custom header
)


class MessageRequest(BaseModel):
    message: str


class NextAction(BaseModel):
    description: str


class MessageResponse(BaseModel):
    next_actions: List[NextAction]


# Task chunking models
class Task(BaseModel):
    id: str = Field(description="Unique identifier for the task")
    parent_id: Optional[str] = Field(
        None, description="ID of parent task, null if root"
    )
    title: str = Field(description="Short title/summary of the task")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskTree(BaseModel):
    task: Task
    subtasks: List["TaskTree"] = Field(default_factory=list)


# Required for recursive Pydantic model
TaskTree.model_rebuild()


class ChunkRequest(BaseModel):
    task_id: Optional[str] = Field(None, description="ID of task to break down further")
    title: Optional[str] = Field(None, description="Title for new task creation")


class ChunkResponse(BaseModel):
    tree: TaskTree


@app.post("/api/v1/chat", response_model=MessageResponse)
async def chat_with_llm(
    request: MessageRequest,
    conversation_id: Optional[str] = Header(
        None, description="Conversation ID for maintaining context"
    ),
):
    """Send a message to the LLM and get a response."""
    if not conversation_id:
        conv_id = start_conversation()
    else:
        conv_id = conversation_id

    add_message(conv_id, "user", request.message)
    history = get_history(conv_id)
    response = await get_llm_response(history)

    if response is None:
        raise HTTPException(status_code=500, detail="Failed to get LLM response")

    try:
        json_response = json.loads(response)
        response = MessageResponse.model_validate(json_response)
        headers = {"X-Conversation-ID": conv_id}
        return JSONResponse(content=response.model_dump(), headers=headers)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse LLM response: {str(e)}"
        ) from e


@app.post("/api/v1/chunk", response_model=ChunkResponse)
async def chunk_task(
    request: ChunkRequest,
    conversation_id: Optional[str] = Header(
        None, description="Conversation ID for maintaining context"
    ),
):
    """Break down a task into smaller, hierarchical subtasks."""
    if not conversation_id:
        conv_id = start_conversation()
    else:
        conv_id = conversation_id

    # Validate request
    if not request.task_id and not request.title:
        raise HTTPException(
            status_code=400, detail="Either task_id or title must be provided"
        )

    # Create or get root task
    if request.task_id:
        existing_tree = get_task_tree(conv_id)
        if not existing_tree:
            raise HTTPException(
                status_code=404,
                detail=f"No task tree found for conversation: {conv_id}",
            )

        task_node = find_task_in_tree(existing_tree["tree"], request.task_id)
        if not task_node:
            raise HTTPException(
                status_code=404, detail=f"Task not found: {request.task_id}"
            )

        root_task = Task.model_validate(task_node["task"])
    else:
        root_task = Task(
            id=str(uuid.uuid4()),
            title=request.title,
            created_at=datetime.utcnow(),
        )

    # Create the response using Pydantic models
    response = ChunkResponse(
        tree=TaskTree(
            task=root_task,
            subtasks=[
                TaskTree(
                    task=Task(
                        id=f"{root_task.id}-1",
                        parent_id=root_task.id,
                        title="Planning Phase",
                    )
                ),
                TaskTree(
                    task=Task(
                        id=f"{root_task.id}-2",
                        parent_id=root_task.id,
                        title="Initial Setup",
                    )
                ),
            ],
        )
    )

    # Convert to JSON-safe dict
    mock_response = response.model_dump(mode="json")

    # Save to Redis
    save_task_tree(conv_id, mock_response)

    headers = {"X-Conversation-ID": conv_id}
    return JSONResponse(content=mock_response, headers=headers)


@app.get("/")
async def hello_world():
    return {"message": "Hello, TaskChunker!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
