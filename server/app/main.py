from contextlib import asynccontextmanager
import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, Depends, Header, HTTPException, Request, status, File, UploadFile, Query
from fastapi.responses import  JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.database import engine, AsyncSessionLocal, get_db
from app.db.models import Users, Base, Tweets, Media, Likes, followers
from app.db.schemas import (
    BaseResponse,
    AboutUserResponse,
    MediaResponse,
    TweetResponse,
    AllTweetsResponse,
    TweetItemResponse,
    TweetLikeResponse,
    TweetAuthorResponse,
    TweetCreate,
    LikeCreate
)

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

# async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
#     async with AsyncSessionLocal() as session:
#         yield session

async def get_user_by_api_key(api_key: str = Header(..., alias="api-key"), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Users.id_user).where(Users.api_key == api_key))
    user_id = res.scalar_one_or_none()

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user_id

@app.post("/api/tweets", response_model=TweetResponse)
async def post_new_tweet(
        data: TweetCreate,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint send new tweet and return its id
    """

    try:
        new_tweet = Tweets(id_author=id_user, content=data.tweet_data)
        db.add(new_tweet)
        await db.commit()
        await db.refresh(new_tweet)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred, when tweet-data was wrote in DB: {e}")

    if data.tweet_media_ids:
        await db.execute(
            update(Media)
            .where(Media.id_media.in_(data.tweet_media_ids))
            .values(id_tweet=new_tweet.id_tweet)
        )
        await db.commit()

    return TweetResponse(result=True, tweet_id=new_tweet.id_tweet)


@app.post("/api/medias", response_model=MediaResponse)
async def save_media(
        file: UploadFile=File(...),
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint save medias from the tweet
    """
    if file is None:
        raise HTTPException(status_code=400, detail="File is required")

    extension = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / unique_name

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File not saved: {e}")

    new_media = Media(path=f"/uploads/{unique_name}")
    db.add(new_media)
    await db.commit()
    await db.refresh(new_media)

    return MediaResponse(result=True, media_id=new_media.id_media)


@app.delete("/api/tweets/{id}", response_model=BaseResponse)
async def delete_tweet_by_id(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint delete the tweet by its id
    """
    res = await db.execute(
        select(Tweets)
        .where(Tweets.id_author==id_user, Tweets.id_tweet==id)
    )
    deleted_tweet = res.scalar_one_or_none()
    if deleted_tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")
    await db.delete(deleted_tweet)
    await db.commit()

    return BaseResponse(result=True)


@app.post("/api/tweets/{id}/likes", response_model=BaseResponse)
async def add_to_tweet_like(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint add like to the tweet by id
    """
    res = await db.execute(select(Tweets).where(Tweets.id_tweet==id))
    tweet = res.scalar_one_or_none()
    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet is not exist")
    new_like = Likes(id_user=id_user, id_tweet=id)
    db.add(new_like)
    await db.commit()

    return BaseResponse(result=True)


@app.delete("/api/tweets/{id}/likes", response_model=BaseResponse)
async def delete_like_from_tweet(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint delete like from the tweet by id
    """
    result = await db.execute(
        select(Likes).where(Likes.id_user == id_user, Likes.id_tweet == id)
    )
    like = result.scalar_one_or_none()
    if like is None:
        raise HTTPException(status_code=404, detail="Like not found")

    await db.delete(like)
    await db.commit()

    return BaseResponse(result=True)


@app.post("/api/users/{id}/follow", response_model=BaseResponse)
async def user_follow_user_by_id(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint let user follows other user by his id
    """
    if id_user == id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    res = await db.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.id_user==id_user)
    )
    cur_user = res.scalar_one_or_none()

    res = await db.execute(
        select(Users)
        .where (Users.id_user==id)
    )
    followed_user = res.scalar_one_or_none()
    if followed_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if followed_user in cur_user.following:
        raise HTTPException(status_code=400, detail="Already following")

    cur_user.following.append(followed_user)
    await db.commit()

    return BaseResponse(result=True)


@app.delete("/api/users/{id}/follow", response_model=BaseResponse)
async def cancel_follow_user_by_id(
        id: int,
        id_user: int = Depends(get_user_by_api_key),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint cancel follow other user by his id
    """
    res = await db.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.id_user == id_user)
    )
    cur_user = res.scalar_one_or_none()

    res = await db.execute(
        select(Users)
        .where(Users.id_user==id)
    )
    followed_user = res.scalar_one_or_none()
    if followed_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if followed_user not in cur_user.following:
        raise HTTPException(status_code=404, detail="Follow not found")

    cur_user.following.remove(followed_user)
    await db.commit()

    return BaseResponse(result=True)


@app.get("/api/tweets", response_model=AllTweetsResponse)
async def get_all_tweets(
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint return all tweets for user in json
    """
    user_res = await db.execute(
        select(Users).options(
            selectinload(Users.following)
        ).where(Users.api_key==api_key)
    )
    cur_user = user_res.scalar_one_or_none()
    if cur_user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    authors_id = [u.id_user for u in cur_user.following]
    authors_id.append(cur_user.id_user)

    res = await db.execute(
        select(Tweets).options(
            selectinload(Tweets.authors),
            selectinload(Tweets.media),
            selectinload(Tweets.likes).selectinload(Likes.users)
        )
        .where(Tweets.id_author.in_(authors_id))
        .order_by(Tweets.id_tweet.desc())
    )

    tweets = res.scalars().all()

    tweets_resp = []
    for tweet in tweets:
        attachment = [m.path for m in tweet.media]
        author = TweetAuthorResponse.model_validate(tweet.authors)
        likes = [
            TweetLikeResponse.model_validate(like.users) for like in tweet.likes
        ]

        tweets_resp.append(
            TweetItemResponse(id=tweet.id_tweet,
                              content=tweet.content,
                              attachments=attachment,
                              author=author,
                              likes=likes)
        )

    return AllTweetsResponse(result=True, tweets=tweets_resp)


@app.get("/api/users/me", response_model=AboutUserResponse)
async def get_info_about_me(
        api_key: str = Header(..., alias="api-key"),
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about me
    """
    res = await db.execute(
        select(Users)
        .options(
            selectinload(Users.followers),
            selectinload(Users.following),
        )
        .where(Users.api_key == api_key))
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AboutUserResponse(result=True, user=user)


@app.get("/api/users/{id}", response_model=AboutUserResponse)
async def get_info_about_user(
        id: int,
        db: AsyncSession = Depends(get_db)):
    """
    Endpoint give all info about user by his id
    """
    res = await db.execute(
        select(Users)
        .options(
            selectinload(Users.followers),
            selectinload(Users.following),
        )
        .where(Users.id_user == id))
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return AboutUserResponse(result=True, user=user)
