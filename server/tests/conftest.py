import sys
import os
import shutil
from pathlib import Path


TEST_UPLOADS_DIR = Path(__file__).parent / "test_uploads"

os.environ["UPLOAD_DIR"] = str(TEST_UPLOADS_DIR)
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.orm import configure_mappers
from sqlalchemy import select
from sqlalchemy.pool import StaticPool
from main import app
from db.database import get_db
from db.models import Base
from db import models

configure_mappers()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Создание таблиц в тестовой БД перед тестированием"""

    # ← Создаём папку для загрузок
    TEST_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        async with session.begin():
            for i in range(1, 3):
                existing = await session.execute(
                    select(models.Users.id_user).where(models.Users.api_key == f"test_api_{i}"))
                if existing.scalar_one_or_none() is None:
                    session.add(models.Users(name=f"test_user_{i}", api_key=f"test_api_{i}"))
    yield

    if TEST_UPLOADS_DIR.exists():
        shutil.rmtree(TEST_UPLOADS_DIR)
    await test_engine.dispose()


async def override_get_db():
    """Подменяет get_db на тестовую сессию"""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def client():
    """TestClient с подменённой БД"""
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def db_session():
    """Сессия к тестовой БД"""
    async with TestSessionLocal() as session:
        yield session
