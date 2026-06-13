from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import engine, session
from db.models import Users, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    async with session:
        async with session.begin():
            session.add(Users(name="u1", api_key="1"))
            await session.commit()

app = FastAPI(lifespan=lifespan)


async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with session:
        yield session


@app.get("/")
async def hello_world(db: AsyncSession = Depends(get_db)):
    new_user = Users(name="u1", api_key="1")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "ok"}
