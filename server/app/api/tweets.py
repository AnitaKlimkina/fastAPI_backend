from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header, status
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


# async def _create_tweet(
#     db: AsyncSession,
#     id_user: int,
#     tweet_content: str,
# ) -> Tweets:
#     """Создаёт твит и возвращает его."""
#     new_tweet = Tweets(id_author=id_user, content=tweet_content)
#     db.add(new_tweet)
#     await db.commit()
#     # await db.refresh(new_tweet)
#     return new_tweet


# @router.post("", response_model=TweetResponse)
# async def post_new_tweet(
#         tweet_data: TweetCreate,
#         id_user: Annotated[int, Depends(get_user_by_api_key)],
#         db: Annotated[AsyncSession, Depends(get_db)]):
#     """
#     Endpoint send new tweet and return its id
#     """
#
#     try:
#         new_tweet = await _create_tweet(
#             db, id_user, tweet_data.tweet_data
#         )
#     except Exception as exc:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error occurred, when tweet-data was wrote in DB: {exc}"
#         ) from exc
#
#     if tweet_data.tweet_media_ids:
#         await db.execute(
#             update(Media)
#             .where(Media.id_media.in_(tweet_data.tweet_media_ids))
#             .values(id_tweet=new_tweet.id_tweet)
#         )
#         await db.commit()
#
#     return TweetResponse(result=True, tweet_id=new_tweet.id_tweet)


@router.post("", response_model=TweetResponse)
async def post_new_tweet(
        tweet_data: TweetCreate,
        id_user: Annotated[int, Depends(get_user_by_api_key)],
        db: Annotated[AsyncSession, Depends(get_db)]):
    """Endpoint send new tweet and return its id."""
    try:  # noqa: WPS229
        new_tweet = Tweets(id_author=id_user, content=tweet_data.tweet_data)
        db.add(new_tweet)
        await db.commit()
        await db.refresh(new_tweet)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error occurred, when tweet-data was wrote in DB: {exc}"
        ) from exc

    if tweet_data.tweet_media_ids:
        await db.execute(
            update(Media)
            .where(Media.id_media.in_(tweet_data.tweet_media_ids))
            .values(id_tweet=new_tweet.id_tweet)
        )
        await db.commit()

    return TweetResponse(result=True, tweet_id=new_tweet.id_tweet)


@router.delete("/{id}", response_model=BaseResponse)
async def delete_tweet_by_id(
        id: int,
        id_user: Annotated[int, Depends(get_user_by_api_key)],
        db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Endpoint delete the tweet by its id
    """
    res = await db.execute(
        select(Tweets)
        .where(Tweets.id_author == id_user, Tweets.id_tweet == id)
    )
    deleted_tweet = res.scalar_one_or_none()
    if deleted_tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found")
    await db.delete(deleted_tweet)
    await db.commit()

    return BaseResponse(result=True)


@router.post("/{id}/likes", response_model=BaseResponse)
async def add_to_tweet_like(
        id: int,
        id_user: Annotated[int, Depends(get_user_by_api_key)],
        db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Endpoint add like to the tweet by id
    """
    tweet_query = select(Tweets).where(Tweets.id_tweet == id)
    res = await db.execute(tweet_query)
    tweet = res.scalar_one_or_none()
    if tweet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet is not exist")
    new_like = Likes(id_user=id_user, id_tweet=id)
    db.add(new_like)
    await db.commit()

    return BaseResponse(result=True)


@router.delete("/{id}/likes", response_model=BaseResponse)
async def delete_like_from_tweet(
        id: int,
        id_user: Annotated[int, Depends(get_user_by_api_key)],
        db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Endpoint delete like from the tweet by id
    """
    res = await db.execute(
        select(Likes).where(Likes.id_user == id_user, Likes.id_tweet == id)
    )
    like = res.scalar_one_or_none()
    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found")

    await db.delete(like)
    await db.commit()

    return BaseResponse(result=True)


@router.get("", response_model=AllTweetsResponse)
async def get_all_tweets(  # noqa: WPS210
        api_key: Annotated[str, Header(alias="api-key")],
        db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Endpoint return all tweets for user in json
    """
    user_res = await db.execute(
        select(Users).options(
            selectinload(Users.following)
        ).where(Users.api_key == api_key)
    )
    cur_user = user_res.scalar_one_or_none()
    if cur_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key")

    authors_id = [user.id_user for user in cur_user.following]
    authors_id.append(cur_user.id_user)

    tweets_query = (
        select(Tweets).options(
            selectinload(Tweets.authors),
            selectinload(Tweets.media),
            selectinload(Tweets.likes).selectinload(Likes.users)
        )
        .where(Tweets.id_author.in_(authors_id))
        .order_by(Tweets.id_tweet.desc())
    )
    res = await db.execute(tweets_query)

    tweets = res.scalars().all()

    tweets_resp = []
    for tweet in tweets:
        attachment = [media.path for media in tweet.media]
        author = TweetAuthorResponse.model_validate(tweet.authors)
        likes = [
            TweetLikeResponse.model_validate(like.users)
            for like in tweet.likes
        ]

        tweets_resp.append(
            TweetItemResponse(id=tweet.id_tweet,
                              content=tweet.content,
                              attachments=attachment,
                              author=author,
                              likes=likes)
        )

    return AllTweetsResponse(result=True, tweets=tweets_resp)
