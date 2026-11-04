from fastapi import FastAPI

from app.routers.ollama import router as ollama_router

app = FastAPI()

# Register routers
app.include_router(ollama_router)


@app.get("/")
def read_root():
    return {"message": "DocuMind AI API"}
