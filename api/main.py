from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.auth_routes import router as auth_router


app = FastAPI(
    title="QueryPilot",
    description="Production NL-to-SQL agent with schema RAG, self-correction, and fine-tuning",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "querypilot"}
