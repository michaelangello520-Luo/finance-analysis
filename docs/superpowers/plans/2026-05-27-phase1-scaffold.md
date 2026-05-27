# Phase 1: 基础骨架 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建前后端项目骨架，数据库建表，实现搜索 API 和前端页面框架，跑通前后端联调。

**Architecture:** FastAPI 后端 + React/TypeScript 前端，前后端分离开发。后端通过 SQLAlchemy 2.0 异步访问 SQLite。前端用 Vite 构建，Ant Design 5 做 UI，React Router v7 做路由。

**Tech Stack:** Python 3.10, FastAPI, SQLAlchemy 2.0, aiosqlite, Pydantic v2, React 18, TypeScript, Vite, Ant Design 5, React Router v7

**Environment:** Python at `D:/python310/python.exe`, Node v22.20.0, npm 10.9.3

---

## File Structure

```
finance-analysis/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry, CORS, lifespan
│   │   ├── config.py                  # Settings from .env via pydantic-settings
│   │   ├── database.py                # Async engine, session, Base
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── stock.py               # Stock model
│   │   │   ├── industry.py            # Industry model + IndustryRelation + StockIndustry
│   │   │   ├── financial_data.py      # FinancialData model
│   │   │   ├── research_report.py     # ResearchReport model
│   │   │   └── watchlist.py           # Watchlist model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── stock.py               # Stock Pydantic schemas
│   │   │   ├── industry.py            # Industry Pydantic schemas
│   │   │   └── search.py              # Search result schema
│   │   └── api/
│   │       ├── __init__.py
│   │       └── search.py              # GET /api/search router
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Shared fixtures (async client, test DB)
│   │   ├── test_main.py               # Root and health endpoint tests
│   │   ├── test_models.py             # Model creation and relation tests
│   │   └── test_search.py             # Search API tests
│   ├── requirements.txt
│   ├── .env                           # API keys (gitignored)
│   └── .env.example                   # Template for .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Root component with router
│   │   ├── main.tsx                   # Entry point
│   │   ├── vite-env.d.ts
│   │   ├── pages/
│   │   │   ├── HomePage.tsx           # Search + watchlist cards
│   │   │   ├── StockDetailPage.tsx    # Placeholder
│   │   │   ├── IndustryDetailPage.tsx # Placeholder
│   │   │   └── WatchlistPage.tsx      # Placeholder
│   │   ├── components/
│   │   │   └── SearchBar.tsx          # Search input with debounced API call
│   │   └── services/
│   │       └── api.ts                 # Axios instance + API functions
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── data/                              # SQLite DB files (gitignored)
├── .gitignore                         # Updated
└── docs/
```

---

### Task 1: Backend - Initialize Python project

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/.env.example`
- Create: `backend/.env`

- [ ] **Step 1: Create requirements.txt**

```txt
fastapi==0.115.13
uvicorn[standard]==0.34.2
sqlalchemy[asyncio]==2.0.41
aiosqlite==0.21.0
pydantic==2.11.4
pydantic-settings==2.9.1
httpx==0.28.1
pytest==8.4.1
pytest-asyncio==1.0.0
```

- [ ] **Step 2: Install dependencies**

Run: `cd backend && D:/python310/python.exe -m pip install -r requirements.txt`
Expected: All packages install successfully

- [ ] **Step 3: Create app/__init__.py**

Empty file.

- [ ] **Step 4: Create .env.example**

```env
# East Money MiaoXiang API
EM_API_KEY=your_api_key_here

# DeepSeek LLM API (Phase 3)
DEEPSEEK_API_KEY=your_api_key_here

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/finance.db
```

- [ ] **Step 5: Create .env (copy from example, fill real key)**

```env
EM_API_KEY=em_GRWToSSJlcLwpLD4er4PvXc6GWfNsrng
DEEPSEEK_API_KEY=
DATABASE_URL=sqlite+aiosqlite:///./data/finance.db
```

- [ ] **Step 6: Update root .gitignore**

Add to existing `.gitignore`:

```
# Backend
backend/.env
backend/__pycache__/
backend/**/__pycache__/
backend/*.egg-info/

# Data
data/
```

- [ ] **Step 7: Commit**

```bash
git add backend/ .gitignore
git commit -m "feat: initialize backend Python project with dependencies"
```

---

### Task 2: Backend - Database models

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/stock.py`
- Create: `backend/app/models/industry.py`
- Create: `backend/app/models/financial_data.py`
- Create: `backend/app/models/research_report.py`
- Create: `backend/app/models/watchlist.py`

- [ ] **Step 1: Write failing test for database initialization**

Create `backend/tests/__init__.py` (empty) and `backend/tests/conftest.py`:

```python
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base
from app.main import app


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    from app.database import get_db

    async def override_get_db():
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
```

Create `backend/tests/test_models.py`:

```python
import pytest
from sqlalchemy import select

from app.models.stock import Stock
from app.models.industry import Industry


@pytest.mark.asyncio
async def test_create_stock(db_session):
    stock = Stock(code="000001", name="平安银行")
    db_session.add(stock)
    await db_session.commit()
    await db_session.refresh(stock)
    assert stock.id is not None
    assert stock.code == "000001"
    assert stock.name == "平安银行"


@pytest.mark.asyncio
async def test_create_industry(db_session):
    industry = Industry(name="机器人", sector="高端装备")
    db_session.add(industry)
    await db_session.commit()
    await db_session.refresh(industry)
    assert industry.id is not None
    assert industry.name == "机器人"


@pytest.mark.asyncio
async def test_stock_industry_relation(db_session):
    industry = Industry(name="机器人", sector="高端装备")
    db_session.add(industry)
    await db_session.flush()

    stock = Stock(code="002747", name="埃斯顿", industry_id=industry.id)
    db_session.add(stock)
    await db_session.commit()
    await db_session.refresh(stock)
    assert stock.industry_id == industry.id
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && D:/python310/python.exe -m pytest tests/test_models.py -v`
Expected: FAIL — modules not found

- [ ] **Step 3: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/finance.db"
    em_api_key: str = ""
    deepseek_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 4: Create database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
```

- [ ] **Step 5: Create models/__init__.py**

```python
from app.models.stock import Stock
from app.models.industry import Industry, IndustryRelation, StockIndustry
from app.models.financial_data import FinancialData
from app.models.research_report import ResearchReport
from app.models.watchlist import Watchlist

__all__ = [
    "Stock",
    "Industry",
    "IndustryRelation",
    "StockIndustry",
    "FinancialData",
    "ResearchReport",
    "Watchlist",
]
```

- [ ] **Step 6: Create models/stock.py**

```python
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    industry_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("industries.id"), nullable=True)

    industry = relationship("Industry", back_populates="stocks")
    financial_data = relationship("FinancialData", back_populates="stock", lazy="selectin")
    reports = relationship("ResearchReport", back_populates="stock", lazy="selectin")
```

- [ ] **Step 7: Create models/industry.py**

```python
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Industry(Base):
    __tablename__ = "industries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    sector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    stocks = relationship("Stock", back_populates="industry")
    reports = relationship("ResearchReport", back_populates="industry", lazy="selectin")
    upstream_relations = relationship(
        "IndustryRelation",
        foreign_keys="IndustryRelation.from_industry_id",
        back_populates="from_industry",
        lazy="selectin",
    )
    downstream_relations = relationship(
        "IndustryRelation",
        foreign_keys="IndustryRelation.to_industry_id",
        back_populates="to_industry",
        lazy="selectin",
    )


class IndustryRelation(Base):
    __tablename__ = "industry_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_industry_id: Mapped[int] = mapped_column(Integer, ForeignKey("industries.id"), nullable=False)
    to_industry_id: Mapped[int] = mapped_column(Integer, ForeignKey("industries.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    from_industry = relationship("Industry", foreign_keys=[from_industry_id], back_populates="upstream_relations")
    to_industry = relationship("Industry", foreign_keys=[to_industry_id], back_populates="downstream_relations")


class StockIndustry(Base):
    __tablename__ = "stock_industry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey("stocks.id"), nullable=False)
    industry_id: Mapped[int] = mapped_column(Integer, ForeignKey("industries.id"), nullable=False)
```

- [ ] **Step 8: Create models/financial_data.py**

```python
from sqlalchemy import String, Integer, Float, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FinancialData(Base):
    __tablename__ = "financial_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(10), nullable=False)
    revenue: Mapped[float | None] = mapped_column(BigInteger, nullable=True)
    net_profit: Mapped[float | None] = mapped_column(BigInteger, nullable=True)
    roe: Mapped[float | None] = mapped_column(Float, nullable=True)
    pe: Mapped[float | None] = mapped_column(Float, nullable=True)
    pb: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    eps: Mapped[float | None] = mapped_column(Float, nullable=True)

    stock = relationship("Stock", back_populates="financial_data")
```

- [ ] **Step 9: Create models/research_report.py**

```python
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("stocks.id"), nullable=True)
    industry_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("industries.id"), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    institution: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rating: Mapped[str | None] = mapped_column(String(50), nullable=True)
    report_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="reports")
    industry = relationship("Industry", back_populates="reports")
```

- [ ] **Step 10: Create models/watchlist.py**

```python
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database import Base


class Watchlist(Base):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 11: Run tests to verify they pass**

Run: `cd backend && D:/python310/python.exe -m pytest tests/test_models.py -v`
Expected: All 3 tests PASS

- [ ] **Step 12: Commit**

```bash
git add backend/
git commit -m "feat: add database config and all SQLAlchemy models"
```

---

### Task 3: Backend - FastAPI app entry with CORS

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`

- [ ] **Step 1: Write test for root endpoint**

Create `backend/tests/test_main.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && D:/python310/python.exe -m pytest tests/test_main.py -v`
Expected: FAIL — app module not found

- [ ] **Step 3: Create api/__init__.py**

Empty file.

- [ ] **Step 4: Create main.py**

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Finance Analysis API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Finance Analysis API"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && D:/python310/python.exe -m pytest tests/test_main.py -v`
Expected: Both tests PASS

- [ ] **Step 6: Start server manually to verify**

Run: `cd backend && D:/python310/python.exe -m uvicorn app.main:app --reload --port 8000`

Open browser at `http://localhost:8000/docs` to verify Swagger UI loads. Then stop the server.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add FastAPI app with CORS, lifespan DB init, health endpoint"
```

---

### Task 4: Backend - Search API

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/stock.py`
- Create: `backend/app/schemas/industry.py`
- Create: `backend/app/schemas/search.py`
- Create: `backend/app/api/search.py`

- [ ] **Step 1: Write failing test for search API**

Create `backend/tests/test_search.py`:

```python
import pytest

from app.models.stock import Stock
from app.models.industry import Industry


@pytest.mark.asyncio
async def test_search_returns_matching_stocks(client, db_session):
    db_session.add(Stock(code="000001", name="平安银行"))
    db_session.add(Stock(code="600036", name="招商银行"))
    await db_session.commit()

    response = await client.get("/api/search?q=银行")
    assert response.status_code == 200
    data = response.json()
    assert len(data["stocks"]) == 2
    assert data["stocks"][0]["code"] == "000001"


@pytest.mark.asyncio
async def test_search_returns_matching_industries(client, db_session):
    db_session.add(Industry(name="机器人", sector="高端装备"))
    db_session.add(Industry(name="新能源", sector="电力设备"))
    await db_session.commit()

    response = await client.get("/api/search?q=机器")
    assert response.status_code == 200
    data = response.json()
    assert len(data["industries"]) == 1
    assert data["industries"][0]["name"] == "机器人"


@pytest.mark.asyncio
async def test_search_empty_query_returns_empty(client):
    response = await client.get("/api/search?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["stocks"] == []
    assert data["industries"] == []


@pytest.mark.asyncio
async def test_search_stock_by_code(client, db_session):
    db_session.add(Stock(code="000001", name="平安银行"))
    await db_session.commit()

    response = await client.get("/api/search?q=000001")
    assert response.status_code == 200
    data = response.json()
    assert len(data["stocks"]) == 1
    assert data["stocks"][0]["code"] == "000001"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && D:/python310/python.exe -m pytest tests/test_search.py -v`
Expected: FAIL — router not mounted

- [ ] **Step 3: Create schemas/__init__.py**

Empty file.

- [ ] **Step 4: Create schemas/stock.py**

```python
from pydantic import BaseModel


class StockBase(BaseModel):
    code: str
    name: str


class StockListItem(StockBase):
    id: int
    industry_id: int | None = None

    model_config = {"from_attributes": True}
```

- [ ] **Step 5: Create schemas/industry.py**

```python
from pydantic import BaseModel


class IndustryBase(BaseModel):
    name: str
    sector: str | None = None


class IndustryListItem(IndustryBase):
    id: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 6: Create schemas/search.py**

```python
from pydantic import BaseModel

from app.schemas.stock import StockListItem
from app.schemas.industry import IndustryListItem


class SearchResult(BaseModel):
    stocks: list[StockListItem] = []
    industries: list[IndustryListItem] = []
```

- [ ] **Step 7: Create api/search.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stock import Stock
from app.models.industry import Industry
from app.schemas.search import SearchResult
from app.schemas.stock import StockListItem
from app.schemas.industry import IndustryListItem

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResult)
async def search(q: str = Query(default="", max_length=50), db: AsyncSession = Depends(get_db)):
    if not q.strip():
        return SearchResult()

    like_pattern = f"%{q}%"

    stock_stmt = select(Stock).where(
        or_(Stock.name.like(like_pattern), Stock.code.like(like_pattern))
    ).limit(10)
    stock_result = await db.execute(stock_stmt)
    stocks = [StockListItem.model_validate(s) for s in stock_result.scalars().all()]

    industry_stmt = select(Industry).where(Industry.name.like(like_pattern)).limit(10)
    industry_result = await db.execute(industry_stmt)
    industries = [IndustryListItem.model_validate(i) for i in industry_result.scalars().all()]

    return SearchResult(stocks=stocks, industries=industries)
```

- [ ] **Step 8: Mount router in main.py**

Replace entire `backend/app/main.py`:

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api.search import router as search_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Finance Analysis API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/")
async def root():
    return {"message": "Finance Analysis API"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 9: Run all tests**

Run: `cd backend && D:/python310/python.exe -m pytest tests/ -v`
Expected: All tests PASS (test_main + test_models + test_search)

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: add search API with stock/industry fuzzy matching"
```

---

### Task 5: Frontend - Initialize React + TypeScript + Vite

**Files:**
- Create: `frontend/` (via Vite scaffold)

- [ ] **Step 1: Create Vite project**

Run: `cd "D:/coding/finance analysis" && npm create vite@latest frontend -- --template react-ts`

- [ ] **Step 2: Install dependencies**

Run: `cd frontend && npm install && npm install antd @ant-design/icons react-router axios`

- [ ] **Step 3: Update vite.config.ts with API proxy**

Replace `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Verify dev server starts**

Run: `cd frontend && npm run dev`
Expected: Server starts at `http://localhost:5173`, default Vite page shows. Stop the server.

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: initialize React+TypeScript+Vite frontend with Ant Design"
```

---

### Task 6: Frontend - API service layer

**Files:**
- Create: `frontend/src/services/api.ts`

- [ ] **Step 1: Create API service**

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export interface StockItem {
  id: number;
  code: string;
  name: string;
  industry_id: number | null;
}

export interface IndustryItem {
  id: number;
  name: string;
  sector: string | null;
}

export interface SearchResult {
  stocks: StockItem[];
  industries: IndustryItem[];
}

export async function searchStock(query: string): Promise<SearchResult> {
  const { data } = await api.get<SearchResult>('/search', { params: { q: query } });
  return data;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/services/
git commit -m "feat: add frontend API service layer with search function"
```

---

### Task 7: Frontend - SearchBar component

**Files:**
- Create: `frontend/src/components/SearchBar.tsx`

- [ ] **Step 1: Create SearchBar component**

```tsx
import { useState } from 'react';
import { Input, AutoComplete } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router';
import { searchStock, type StockItem, type IndustryItem } from '../services/api';

interface SearchOption {
  value: string;
  label: React.ReactNode;
  type: 'stock' | 'industry';
  id: number | string;
}

export default function SearchBar() {
  const [options, setOptions] = useState<SearchOption[]>([]);
  const navigate = useNavigate();

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setOptions([]);
      return;
    }
    try {
      const result = await searchStock(query);
      const stockOpts: SearchOption[] = result.stocks.map((s: StockItem) => ({
        value: `${s.name} (${s.code})`,
        label: (
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{s.name}</span>
            <span style={{ color: '#999' }}>{s.code} · 个股</span>
          </div>
        ),
        type: 'stock',
        id: s.code,
      }));
      const industryOpts: SearchOption[] = result.industries.map((i: IndustryItem) => ({
        value: i.name,
        label: (
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{i.name}</span>
            <span style={{ color: '#999' }}>{i.sector || ''} · 行业</span>
          </div>
        ),
        type: 'industry',
        id: i.id,
      }));
      setOptions([...stockOpts, ...industryOpts]);
    } catch {
      setOptions([]);
    }
  };

  const handleSelect = (value: string, option: SearchOption) => {
    if (option.type === 'stock') {
      navigate(`/stock/${option.id}`);
    } else {
      navigate(`/industry/${option.id}`);
    }
  };

  return (
    <AutoComplete
      style={{ width: '100%', maxWidth: 600 }}
      options={options}
      onSearch={handleSearch}
      onSelect={handleSelect as any}
    >
      <Input.Search
        size="large"
        placeholder="输入股票名称/代码 或 行业名称"
        prefix={<SearchOutlined />}
        enterButton="搜索"
      />
    </AutoComplete>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add SearchBar component with fuzzy search and navigation"
```

---

### Task 8: Frontend - Page routing and layout

**Files:**
- Replace: `frontend/src/App.tsx`
- Replace: `frontend/src/main.tsx`
- Create: `frontend/src/pages/HomePage.tsx`
- Create: `frontend/src/pages/StockDetailPage.tsx`
- Create: `frontend/src/pages/IndustryDetailPage.tsx`
- Create: `frontend/src/pages/WatchlistPage.tsx`

- [ ] **Step 1: Create HomePage**

`frontend/src/pages/HomePage.tsx`:

```tsx
import { Typography, Layout } from 'antd';
import SearchBar from '../components/SearchBar';

const { Title, Paragraph } = Typography;
const { Content } = Layout;

export default function HomePage() {
  return (
    <Content style={{ padding: '80px 24px', maxWidth: 800, margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>
        A 股长期投资看板
      </Title>
      <Paragraph style={{ textAlign: 'center', color: '#666', marginBottom: 40 }}>
        输入股票或行业，获取 AI 研报分析与产业链洞察
      </Paragraph>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <SearchBar />
      </div>
    </Content>
  );
}
```

- [ ] **Step 2: Create placeholder pages**

`frontend/src/pages/StockDetailPage.tsx`:

```tsx
import { useParams } from 'react-router';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function StockDetailPage() {
  const { code } = useParams<{ code: string }>();
  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>个股详情: {code}</Title>
      <Paragraph>Phase 4 实现</Paragraph>
    </div>
  );
}
```

`frontend/src/pages/IndustryDetailPage.tsx`:

```tsx
import { useParams } from 'react-router';
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function IndustryDetailPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>行业详情: {id}</Title>
      <Paragraph>Phase 4 实现</Paragraph>
    </div>
  );
}
```

`frontend/src/pages/WatchlistPage.tsx`:

```tsx
import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function WatchlistPage() {
  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>关注列表</Title>
      <Paragraph>Phase 5 实现</Paragraph>
    </div>
  );
}
```

- [ ] **Step 3: Update App.tsx with layout and routing**

Replace `frontend/src/App.tsx`:

```tsx
import { createBrowserRouter, RouterProvider, Outlet, Link } from 'react-router';
import { Layout, Menu } from 'antd';
import HomePage from './pages/HomePage';
import StockDetailPage from './pages/StockDetailPage';
import IndustryDetailPage from './pages/IndustryDetailPage';
import WatchlistPage from './pages/WatchlistPage';

const { Header, Content, Footer } = Layout;

function AppLayout() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <Link to="/" style={{ color: '#fff', fontSize: 18, fontWeight: 'bold', marginRight: 40, textDecoration: 'none' }}>
          Finance Analysis
        </Link>
        <Menu
          theme="dark"
          mode="horizontal"
          items={[
            { key: 'home', label: <Link to="/">首页</Link> },
            { key: 'watchlist', label: <Link to="/watchlist">关注列表</Link> },
          ]}
        />
      </Header>
      <Content>
        <Outlet />
      </Content>
      <Footer style={{ textAlign: 'center' }}>A 股长期投资看板 2026</Footer>
    </Layout>
  );
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'stock/:code', element: <StockDetailPage /> },
      { path: 'industry/:id', element: <IndustryDetailPage /> },
      { path: 'watchlist', element: <WatchlistPage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
```

- [ ] **Step 4: Update main.tsx**

Replace `frontend/src/main.tsx`:

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

- [ ] **Step 5: Clean up Vite default files**

Delete: `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/assets/` folder

- [ ] **Step 6: Verify frontend starts and routes work**

Run: `cd frontend && npm run dev`
Expected: `http://localhost:5173` shows home page with search bar. Navigation to `/watchlist` shows placeholder.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add page routing, layout, search bar, and placeholder pages"
```

---

### Task 9: End-to-end integration test

- [ ] **Step 1: Start backend**

Run: `cd backend && D:/python310/python.exe -m uvicorn app.main:app --reload --port 8000`

- [ ] **Step 2: Start frontend (new terminal)**

Run: `cd frontend && npm run dev`

- [ ] **Step 3: Verify in browser**

1. Open `http://localhost:5173` — should show search page
2. Type a query — should get empty results (no data yet, but no errors)
3. Click "关注列表" — should show placeholder
4. Open `http://localhost:8000/docs` — should show Swagger UI with `/api/search` and `/api/health`
5. Call `GET /api/health` — should return `{"status": "ok"}`

- [ ] **Step 4: Run all backend tests**

Run: `cd backend && D:/python310/python.exe -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Final commit and push**

```bash
git add -A
git commit -m "feat: complete Phase 1 scaffold - frontend + backend + search API + routing"
git push origin main
```

---

## Summary

| Task | What it builds | Key files |
|------|---------------|-----------|
| 1 | Backend project init | `requirements.txt`, `.env`, `config.py` |
| 2 | Database models (7 tables) | `models/*.py`, `database.py` |
| 3 | FastAPI app + CORS | `main.py` |
| 4 | Search API | `api/search.py`, `schemas/*.py` |
| 5 | Frontend project init | Vite + React + TS + Ant Design |
| 6 | API service layer | `services/api.ts` |
| 7 | SearchBar component | `components/SearchBar.tsx` |
| 8 | Page routing + layout | `App.tsx`, `pages/*.tsx` |
| 9 | E2E integration test + push | Verify all together |
