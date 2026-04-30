from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health, schema_route, chat, sql_route

app = FastAPI(
    title="AI Business Growth Assistant API",
    description="ChatBI API — natural language → SQL + results",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(schema_route.router)
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(sql_route.router, prefix="/sql", tags=["sql"])
