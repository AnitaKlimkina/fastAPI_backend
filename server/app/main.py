import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select
from db.database import engine, AsyncSessionLocal
from api import users, tweets, media
from core.exceptions import register_exception_handlers
from db.models import Users, Base

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            existing = await session.execute(
                select(Users.id_user).where(Users.api_key == "api_key"))
            if existing.scalar_one_or_none() is None:
                session.add(Users(name="user", api_key="api_key"))

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(media.router)

