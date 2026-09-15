from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, List

from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import engine, session
from app.db.models import Users, Base, Tweets

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


async def get_user_by_api_key(api_key: str = Header(..., alias="api-key"), db: AsyncSession = Depends(get_db)):
    id_user = await session.execute(select(Users.id_user).where(Users.api_key == api_key))
    user = id_user.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


@app.get("/api/about")
async def get_info(id_user: int = Depends(get_user_by_api_key), db: AsyncSession = Depends(get_db)):
    user = await session.execute(select(Users.name).where(Users.id_user == id_user))
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



@app.get("/api/users/me")
async def get_info_about_me(db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about me
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}


@app.get("/api/users/<id>")
async def get_info_about_me(id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about user by his id
    """
    try:
        pass

    except Exception as e:
        return {"result": False, "error_type": type(e), "error_message": e}
