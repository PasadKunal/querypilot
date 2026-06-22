from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.routes.auth_routes import router as auth_router
from api.routes.connection_routes import router as connection_router
from api.routes.query_routes import router as query_router
from api.routes.upload_routes import router as upload_router

app = FastAPI(
    title="QueryPilot",
    description="Production NL-to-SQL agent with schema RAG, self-correction, and fine-tuning",
    version="0.1.0",
)

_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(query_router)
app.include_router(upload_router)
app.include_router(connection_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "querypilot"}
