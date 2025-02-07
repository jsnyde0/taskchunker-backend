from fastapi import FastAPI

app = FastAPI(title="TaskChunker API")


@app.get("/api/v1/hello")
async def hello():
    return {"message": "Hello, TaskChunker!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
