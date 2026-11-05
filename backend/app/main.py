from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.documents import router as documents_router
from app.routers.ollama import router as ollama_router

app = FastAPI(title="DocuMind AI API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ollama_router)
app.include_router(documents_router)


@app.get("/")
def read_root():
    return {"message": "DocuMind AI API"}
