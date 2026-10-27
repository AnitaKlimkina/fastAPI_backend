import pytest
from sqlalchemy import select

from db.models import Tweets, Likes


@pytest.mark.asyncio
async def test_post_new_tweet(client, db_session):
    """Тестирование успешной публикации твита"""
    data = "It's test tweet data :)"
    resp = client.post("/api/tweets", headers={"api-key": "test_api_1"},
                       json={"tweet_data": data})
    assert resp.status_code == 200

    tweet_id = resp.json()["tweet_id"]

    result = await db_session.execute(
        select(Tweets).where(Tweets.id_tweet == tweet_id)
    )
    tweet = result.scalar_one_or_none()

    assert tweet is not None
    assert tweet.content == data


@pytest.mark.asyncio
async def test_post_new_tweet_with_media(client, db_session):
    """Создание твита с медиа → Media.id_tweet обновлён."""
    import io
    from db.models import Media

    # 1. Загружаем медиа
    file = ("test.jpg", io.BytesIO(b"fake image content"), "image/jpeg")
    media_resp = client.post(
        "/api/medias",
        headers={"api-key": "test_api_1"},
        files={"file": file},
    )
    assert media_resp.status_code == 200
    media_id = media_resp.json()["media_id"]

    # 2. Создаём твит с медиа
    tweet_resp = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
        json={"tweet_data": "tweet with media", "tweet_media_ids": [media_id]},
    )
    assert tweet_resp.status_code == 200
    tweet_id = tweet_resp.json()["tweet_id"]

    # 3. Проверяем, что Media.id_tweet обновился
    result = await db_session.execute(
        select(Media).where(Media.id_media == media_id)
    )
    media = result.scalar_one_or_none()

    assert media is not None
    assert media.id_tweet == tweet_id


def test_post_new_tweet_with_wrong_api_key(client):
    """Тестирование неудачной публикации твита с неправильным api-key"""
    data = "It's test tweet data :)"
    resp = client.post("/api/tweets", headers={"api-key": "wrong-api-key"},
                       json={"tweet_data": data})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


@pytest.mark.asyncio
async def test_post_new_tweet_db_error(client, monkeypatch):
    """Ошибка при создании твита → 500"""
    from sqlalchemy.ext.asyncio import AsyncSession

    async def _broken_create_tweet(*args, **kwargs):
        raise Exception("DB is down")

    monkeypatch.setattr(AsyncSession, "commit", _broken_create_tweet)

    response = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
        json={"tweet_data": "test", "tweet_media_ids": []},
    )

    assert response.status_code == 500
    body = response.json()
    assert body["result"] is False
    assert body["error_type"] == "HTTPException"
    assert "DB is down" in body["error_message"]


@pytest.mark.asyncio
async def test_like_tweet(client, db_session):
    """Тестирование успешного добавления лайка твита"""
    resp = client.post("/api/tweets/1/likes",
                       headers={"api-key": "test_api_1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True

    res = await db_session.execute(select(Likes).where(Likes.id_tweet == 1))
    like = res.scalar_one_or_none()
    assert like is not None
    assert like.id_user == 1


def test_like_tweet_with_wrong_api_key(client):
    """Тестирование неудачного добавления лайка твита с неправильным api-key"""
    resp = client.post("/api/tweets/1/likes",
                       headers={"api-key": "wrong-api-key"})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


def test_like_tweet_with_wrong_id_tweet(client):
    """Тестирование неудачного добавления лайка твиту с неправильным id"""
    resp = client.post("/api/tweets/1000/likes",
                       headers={"api-key": "test_api_1"})
    assert resp.status_code == 404
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Tweet is not exist"


def test_like_post_with_text_id(client):
    """Тестирование неудачного добавления лайка твита с id в виде текста"""
    resp = client.post("/api/tweets/sdf/likes",
                       headers={"api-key": "test_api_1"})
    assert resp.status_code == 422
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "ValidationError"


def test_unlike_tweet_with_wrong_api_key(client):
    """Тестирование неудачного удаления лайка твита с неправильным api-key"""
    resp = client.delete("/api/tweets/1/likes",
                         headers={"api-key": "wrong-api-key"})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


def test_unlike_post_with_text_id(client):
    """Тестирование неудачного удаления лайка твита с id в виде текста"""
    resp = client.delete("/api/tweets/sdf/likes",
                         headers={"api-key": "test_api_1"})
    assert resp.status_code == 422
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "ValidationError"


def test_unlike_tweet_with_wrong_id_tweet(client):
    """Тестирование неудачного удаления лайка с твита с неправильным id"""
    resp = client.delete("/api/tweets/1000/likes",
                       headers={"api-key": "test_api_1"})
    assert resp.status_code == 404
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Like not found"


def test_unlike_tweet(client):
    """Тестирование успешного удаления лайка твита"""
    resp = client.delete("/api/tweets/1/likes",
                         headers={"api-key": "test_api_1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True


def test_get_all_tweets(client):
    """Тестирование успешного вывода твитов юзера"""
    exam = [
        {"id": 3,
         "content": "It\'s test tweet data :)",
         "attachments": [] ,
         "author": {"id": 2, "name" : "test_user_2"},
         "likes": []
         }
    ]

    data = "It's test tweet data :)"
    req = client.post("/api/tweets", headers={"api-key": "test_api_2"},
                       json={"tweet_data": data})

    resp = client.get("/api/tweets",
                       headers={"api-key": "test_api_2"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True
    assert resp.json()["tweets"] == exam


def test_get_all_tweets_with_wrong_api_key(client):
    """Тестирование неудачного вывода твитов юзера с неправильным api-key"""
    resp = client.get("/api/tweets",
                         headers={"api-key": "wrong-api-key"})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


@pytest.mark.asyncio
async def test_get_all_tweets_with_following(client, db_session):
    """Лента включает твиты подписок."""
    from db.models import Users
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # 1. Подписываем test_api_1 на test_api_2
    result = await db_session.execute(
        select(Users).where(Users.api_key == "test_api_1")
    )
    user1 = result.scalar_one_or_none()

    result = await db_session.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.api_key == "test_api_2")
    )
    user2 = result.scalar_one_or_none()

    # user1.following.append(user2) — но user1 не загружен с following
    # Загружаем user1 с following
    result = await db_session.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.api_key == "test_api_1")
    )
    user1 = result.scalar_one_or_none()
    user1.following.append(user2)
    await db_session.commit()

    # 2. Создаём твит от test_api_2
    response = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_2"},
        json={"tweet_data": "tweet from user2", "tweet_media_ids": []},
    )
    tweet_id = response.json()["tweet_id"]

    # 3. Лента test_api_1 должна включать твит test_api_2
    response = client.get(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
    )
    assert response.status_code == 200
    tweets = response.json()["tweets"]

    tweet_ids = [tweet["id"] for tweet in tweets]
    assert tweet_id in tweet_ids


def test_get_all_tweets_with_media(client):
    """Лента возвращает attachments для твита с медиа."""
    import io

    # 1. Загружаем медиа
    file = ("test.jpg", io.BytesIO(b"fake image content"), "image/jpeg")
    media_resp = client.post(
        "/api/medias",
        headers={"api-key": "test_api_1"},
        files={"file": file},
    )
    assert media_resp.status_code == 200
    media_id = media_resp.json()["media_id"]

    # 2. Создаём твит с медиа
    tweet_resp = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
        json={"tweet_data": "tweet with media", "tweet_media_ids": [media_id]},
    )
    tweet_id = tweet_resp.json()["tweet_id"]

    # 3. Лента возвращает attachments
    response = client.get(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
    )
    tweets = response.json()["tweets"]
    tweet = next(t for t in tweets if t["id"] == tweet_id)

    assert len(tweet["attachments"]) == 1
    assert tweet["attachments"][0].startswith("/uploads/")


def test_get_all_tweets_with_likes(client):
    """Лента возвращает likes для твита с лайками."""
    # 1. Создаём твит от test_api_1
    tweet_resp = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
        json={"tweet_data": "tweet with likes", "tweet_media_ids": []},
    )
    tweet_id = tweet_resp.json()["tweet_id"]

    # 2. Ставим лайк от test_api_2
    client.post(
        f"/api/tweets/{tweet_id}/likes",
        headers={"api-key": "test_api_2"},
    )

    # 3. Лента возвращает likes
    response = client.get(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
    )
    tweets = response.json()["tweets"]
    tweet = next(t for t in tweets if t["id"] == tweet_id)

    assert len(tweet["likes"]) == 1
    assert tweet["likes"][0]["name"] == "test_user_2"


def test_get_all_tweets_sorted_desc(client):
    """Лента сортирует твиты по id_tweet desc (новые сверху)."""
    # Создаём 2 твита
    resp1 = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
        json={"tweet_data": "first tweet", "tweet_media_ids": []},
    )
    id1 = resp1.json()["tweet_id"]

    resp2 = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
        json={"tweet_data": "second tweet", "tweet_media_ids": []},
    )
    id2 = resp2.json()["tweet_id"]

    # Лента
    response = client.get(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
    )
    tweets = response.json()["tweets"]
    tweet_ids = [t["id"] for t in tweets]

    # Новый (id2) должен быть первым
    assert tweet_ids.index(id2) < tweet_ids.index(id1)


@pytest.mark.asyncio
async def test_get_all_tweets_isolated(client, db_session):
    """Лента не включает твиты тех, на кого не подписан."""
    from db.models import Users
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # Убеждаемся, что test_api_1 не подписан на test_api_2
    result = await db_session.execute(
        select(Users)
        .options(selectinload(Users.following))
        .where(Users.api_key == "test_api_1")
    )
    user1 = result.scalar_one_or_none()

    result = await db_session.execute(
        select(Users).where(Users.api_key == "test_api_2")
    )
    user2 = result.scalar_one_or_none()

    if user2 in user1.following:
        user1.following.remove(user2)
        await db_session.commit()

    resp = client.post(
        "/api/tweets",
        headers={"api-key": "test_api_2"},
        json={"tweet_data": "tweet from user2", "tweet_media_ids": []},
    )
    tweet_id = resp.json()["tweet_id"]

    # 2. Лента test_api_1 (не подписан на test_api_2)
    response = client.get(
        "/api/tweets",
        headers={"api-key": "test_api_1"},
    )
    tweets = response.json()["tweets"]
    tweet_ids = [t["id"] for t in tweets]

    assert tweet_id not in tweet_ids


def test_delete_post_with_text_id(client):
    """Тестирование неудачного удаления поста с id в виде текста"""
    resp = client.delete("/api/tweets/sfs", headers={"api-key": "test_api_1"})
    assert resp.status_code == 422
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "ValidationError"


def test_delete_tweet_with_wrong_api_key(client):
    """Тестирование неудачного удаления твита с неправильным api-key"""
    resp = client.delete("/api/tweets/1", headers={"api-key": "wrong-api-key"})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


def test_delete_unreal_tweet(client):
    """Тестирование неудачного удаления несуществующего твита"""
    resp = client.delete("/api/tweets/1001", headers={"api-key": "test_api_1"})
    assert resp.status_code == 404
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Tweet not found"


def test_delete_not_self_tweet(client):
    """Тестирование неудачного удаления не своего твита"""
    resp = client.delete("/api/tweets/2", headers={"api-key": "test_api_2"})
    assert resp.status_code == 404
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Tweet not found"


def test_delete_tweet(client):
    """Тестирование успешного удаления своего твита"""
    resp = client.delete("/api/tweets/1", headers={"api-key": "test_api_1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True
