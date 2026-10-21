def test_post_new_tweet(client):
    """Тестирование успешной публикации твита"""
    data = "It's test tweet data :)"
    resp = client.post("/api/tweets", headers={"api-key": "test_api_1"},
                       json={"tweet_data": data})
    assert resp.status_code == 200
    assert resp.json()["tweet_id"] == 1


def test_post_new_tweet_with_wrong_api_key(client):
    """Тестирование неудачной публикации твита с неправильным api-key"""
    data = "It's test tweet data :)"
    resp = client.post("/api/tweets", headers={"api-key": "wrong-api-key"},
                       json={"tweet_data": data})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


def test_like_tweet(client):
    """Тестирование успешного добавления лайка твита"""
    resp = client.post("/api/tweets/1/likes",
                       headers={"api-key": "test_api_1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True


def test_like_tweet_with_wrong_api_key(client):
    """Тестирование неудачного добавления лайка твита с неправильным api-key"""
    resp = client.post("/api/tweets/1/likes",
                       headers={"api-key": "wrong-api-key"})
    assert resp.status_code == 401
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Invalid API key"


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


def test_unlike_tweet(client):
    """Тестирование успешного удаления лайка твита"""
    resp = client.delete("/api/tweets/1/likes",
                         headers={"api-key": "test_api_1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True


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


def test_delete_not_self_tweet(client):
    """Тестирование неудачного удаления не своего твита"""

    data = "It's test tweet data :)"
    resp_new_tweet = client.post("/api/tweets",
                                 headers={"api-key": "test_api_2"},
                                 json={"tweet_data": data})

    resp = client.delete("/api/tweets/2", headers={"api-key": "test_api_1"})
    assert resp.status_code == 404
    assert resp.json()["result"] == False
    assert resp.json()["error_type"] == "HTTPException"
    assert resp.json()["error_message"] == "Tweet not found"


def test_delete_tweet(client):
    """Тестирование успешного удаления своего твита"""
    resp = client.delete("/api/tweets/1", headers={"api-key": "test_api_1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True
