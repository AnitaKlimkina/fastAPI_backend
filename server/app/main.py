from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, List
import logging

from fastapi import FastAPI, Depends, Header, HTTPException, Request, status
from fastapi.responses import  JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.database import engine, AsyncSessionLocal
from app.db.models import Users, Base, Tweets
from app.db.schemas import AboutUserResponse

logger = logging.getLogger(__name__)

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


@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": "HTTPException",
            "error_message": str(exc.detail),
        }
    )

@app.exception_handler(RequestValidationError)
async def request_exc_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "result": False,
            "error_type": "ValidationError",
            "error_message": str(exc.errors()),
        }
    )

@app.exception_handler(Exception)
async def general_axc_handler(request:Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "result": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )


async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_by_api_key(api_key: str = Header(..., alias="api-key"), db: AsyncSession = Depends(get_db)):
    id_user = await db.execute(select(Users.id_user).where(Users.api_key == api_key))
    user = id_user.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


@app.get("/api/about")
async def get_info(id_user: int = Depends(get_user_by_api_key), db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(Users.name).where(Users.id_user == id_user))
    res = user.scalars().all()
    return res


@app.post("/api/tweets/{api_key}")
async def post_new_tweet(
        api_key: str,
        api_tweet_data: str,
        tweet_media_ids: List[int],
        db: AsyncSession = Depends(get_db)
    ):
    """
    Endpoint send new tweet and return its id
    """
    id_user = await get_user_by_api_key(api_key)
    if not id_user:
        return {"result": False, "error_type": "ValidationError", "error_message": "User is not found"}
    try:
        new_tweet = Tweets(id_author=id_user, content=api_tweet_data)
        db.add(new_tweet)
        await db.commit()
        await db.refresh(new_tweet)
        return {"result": True, "tweet_id": new_tweet.id_tweet}
    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.post("/api/medias")
async def save_media(db: AsyncSession = Depends(get_db)):
    """
    Endpoint save medias from the tweet
    """
    try:
        pass
    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.delete("/api/tweets/<id>")
async def delete_tweet_by_id(id_tweet: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint delete the tweet by its id
    """
    try:
        a = 1

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.post("/api/tweets/<id>/likes")
async def add_to_tweet_like(id_tweet: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint add like to the tweet by id
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.delete("/api/tweets/<id>/likes")
async def delete_like_from_tweet(id_tweet: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint delete like from the tweet by id
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.post("/api/users/<id>/follow")
async def user_follow_user_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint let user follows other user by his id
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.delete("/api/users/<id>/follow")
async def cancel_follow_user_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint cancel follow other user by his id
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.get("/api/tweets/{api_key}")
async def get_all_tweets(api_key: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint return all tweets for user in json
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}



@app.get("/api/users/me", response_model=AboutUserResponse)
async def get_info_about_me(api_key: str = Header(..., alias="api-key"), db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about me
    """
    user = await db.execute(
        select(Users)
        .options(
            selectinload(Users.followers),
            selectinload(Users.following),
        )
        .where(Users.api_key == api_key))
    res = user.scalar_one_or_none()
    if res is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AboutUserResponse(result=True, user=res)



@app.get("/api/users/{id}", response_model=AboutUserResponse)
async def get_info_about_user(
        id: int,
        # api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about user by his id
    """
    user = await db.execute(
        select(Users)
        .options(
            selectinload(Users.followers),
            selectinload(Users.following),
        )
        .where(Users.id_user == id))
    res = user.scalar_one_or_none()
    if res is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AboutUserResponse(result=True, user=res)
