import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api.search import router as search_router
from app.api.data import router as data_router
from app.api.stock import router as stock_router
from app.api.industry import router as industry_router
from app.api.settings_api import router as settings_router
from app.api.ai import router as ai_router
from app.api.watchlist import router as watchlist_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Finance Analysis API", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(data_router)
app.include_router(stock_router)
app.include_router(industry_router)
app.include_router(settings_router)
app.include_router(ai_router)
app.include_router(watchlist_router)


@app.get("/")
async def root():
    return {"message": "Finance Analysis API"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
