# TaskChunker Backend

A FastAPI service that helps break down projects into actionable next steps using AI.

## Prerequisites

- uv
- Docker (for Redis)
- OpenAI API key

## Setup

1. Clone the repository
2. Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL_NAME=gpt-3.5-turbo  # or your preferred model
```

## Development

### 1. Start Redis
```bash
# Start Redis container (for the first time
docker run --name taskchunker-redis -p 6379:6379 -d redis

# Start Redis container again
docker start taskchunker-redis
```

### 2. Run the API
```bash
uv run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000/docs`

## Testing

```bash
# Run all tests (including LLM tests)
uv run pytest tests

# Run tests excluding LLM tests
uv run pytest -m "not llm" tests
```

## API Usage

1. Start a conversation by sending a POST request to `/api/v1/chat` with your project description
2. Get the conversation ID from the `x-conversation-id` response header
3. Include this ID in subsequent requests via the `x-conversation-id` header

Example request:
```json
POST /api/v1/chat
{
    "message": "I want to build a treehouse"
}
```

## Docker Commands Reference

```bash
# Stop Redis
docker stop taskchunker-redis

# Start Redis again
docker start taskchunker-redis

# Remove Redis container
docker rm taskchunker-redis
```
