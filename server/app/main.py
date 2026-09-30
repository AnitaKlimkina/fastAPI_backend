from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select
from app.db.database import engine, AsyncSessionLocal
from app.api import users, tweets, media
from app.core.exceptions import register_exception_handlers
from app.db.models import Users, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    async with AsyncSessionLocal() as session:
        async with session.begin():
            existing = await session.execute(
                select(Users.id_user).where(Users.api_key == "test_api"))
            if existing.scalar_one_or_none() is None:
                session.add(Users(name="test_user", api_key="test_api"))
                await session.commit()

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(media.router)

