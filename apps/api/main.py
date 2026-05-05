from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.db.session import async_engine
from app.routes import health, schema_route, chat, sql_route, tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    await async_engine.dispose()


app = FastAPI(
    title="HR ChatBI API",
    description="HR ChatBI — natural language → SQL + results with PII masking",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.include_router(tools.router)
