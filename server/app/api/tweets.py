from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Tweets, Likes, Media, Users
from db.schemas import (
    AllTweetsResponse,
    TweetCreate,
    BaseResponse,
    TweetResponse,
    TweetAuthorResponse,
    TweetLikeResponse,
    TweetItemResponse
)
from api.deps import get_user_by_api_key


router = APIRouter(prefix="/api/tweets", tags=["tweets"])

@router.post("", response_model=TweetResponse)
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


@router.delete("/{id}", response_model=BaseResponse)
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


@router.post("/{id}/likes", response_model=BaseResponse)
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


@router.delete("/{id}/likes", response_model=BaseResponse)
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


@router.get("", response_model=AllTweetsResponse)
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