def test_get_user_with_wrong_id(client):
    """Тестирование не получения юзера с несуществующим id"""
    response = client.get("/api/users/7", headers={"api-key": "test_api_1"})
    assert response.status_code == 404
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "User not found"


def test_get_user_with_text_id(client):
    """Тестирование не получения юзера с id в виде текста"""
    response = client.get("/api/users/kbjb", headers={"api-key": "test_api_1"})
    assert response.status_code == 422
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "ValidationError"


def test_get_user_with_right_id(client):
    """Тестирование получения юзера с существующим id"""
    response = client.get("/api/users/1", headers={"api-key": "test_api_1"})
    user_dict = {
        "id": 1,
        "name": "test_user_1",
        "followers": [],
        "following": []
    }
    assert response.status_code == 200
    assert response.json()["result"] == True
    assert response.json()["user"] == user_dict


def test_get_info_about_me_with_wrong_api_key(client):
    """Тестирование получения инфо обо мне с ложным api-key"""
    response = client.get("/api/users/me",
                          headers={"api-key": "wrong_api_key"})
    assert response.status_code == 401
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Invalid API key"


def test_get_info_about_me_with_right_api_key(client):
    """Тестирование получения инфо обо мне с правильным api-key"""
    response = client.get("/api/users/me", headers={"api-key": "test_api_1"})
    user_dict = {
        "id": 1,
        "name": "test_user_1",
        "followers": [],
        "following": []
    }
    assert response.status_code == 200
    assert response.json()["result"] == True
    assert response.json()["user"] == user_dict


def test_get_info_about_me_with_none_api_key(client):
    """Тестирование получения инфо обо мне с пустым api-key"""
    response = client.get("/api/users/me", headers={"api-key": ""})
    assert response.status_code == 401
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "API key is necceccary"



def test_get_info_about_me_without_api_key(client):
    """Тестирование получения инфо обо мне без api-key"""
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "API key is necceccary"

def test_follow_for_right_user(client):
    """Тестирование успешной подписки на существующего юзера"""
    response = client.post("/api/users/2/follow",
                           headers={"api-key": "test_api_1"})
    assert response.status_code == 200
    assert response.json()["result"] == True


def test_follow_for_yourself(client):
    """Тестирование неудачной подписки на себя самого"""
    response = client.post("/api/users/1/follow",
                           headers={"api-key": "test_api_1"})
    assert response.status_code == 400
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Cannot follow yourself"


def test_follow_for_user_with_text_id(client):
    """Тестирование неудачной подписки на юзера с id в виде текста"""
    response = client.post("/api/users/sefe/follow", headers={"api-key": "test_api_1"})
    assert response.status_code == 422
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "ValidationError"


def test_follow_for_wrong_user(client):
    """Тестирование неудачной подписки на несуществующего юзера"""
    response = client.post("/api/users/200/follow",
                           headers={"api-key": "test_api_1"})
    assert response.status_code == 404
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "User not found"


def test_follow_for_already_followed_user(client):
    """Тестирование неудачной подписки на юзера, на которого уже подписаны"""
    response = client.post("/api/users/2/follow",
                           headers={"api-key": "test_api_1"})
    assert response.status_code == 400
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Already following"


def test_unfollow_for_wrong_user(client):
    """Тестирование неудачной отписки от несуществующего юзера"""
    response = client.delete("/api/users/200/follow",
                             headers={"api-key": "test_api_1"})
    assert response.status_code == 404
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "User not found"


def test_unfollow_for_user_with_text_id(client):
    """Тестирование неудачной отписки от юзера с id в виде текста"""
    response = client.delete("/api/users/sefe/follow", headers={"api-key": "test_api_1"})
    assert response.status_code == 422
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "ValidationError"


def test_unfollow_for_right_user(client):
    """Тестирование успешной отписки от существующего юзера"""
    response = client.delete("/api/users/2/follow",
                             headers={"api-key": "test_api_1"})
    assert response.status_code == 200
    assert response.json()["result"] == True


def test_unfollow_for_already_unfollowed_user(client):
    """Тестирование неудачной отписки от юзера, от которого уже отписались"""
    response = client.delete("/api/users/2/follow",
                             headers={"api-key": "test_api_1"})
    assert response.status_code == 404
    assert response.json()["result"] == False
    assert response.json()["error_type"] == "HTTPException"
    assert response.json()["error_message"] == "Follow not found"


def test_follow_appears_in_me(client):
    """После подписки following непустой."""
    client.post("/api/users/2/follow", headers={"api-key": "test_api_1"})
    response = client.get("/api/users/me", headers={"api-key": "test_api_1"})
    user = response.json()["user"]
    following_ids = [us["id"] for us in user["following"]]
    assert 2 in following_ids


def test_followers_appears_in_me(client):
    """После подписки другого пользователя followers непустой."""
    client.post("/api/users/1/follow", headers={"api-key": "test_api_2"})
    response = client.get("/api/users/me", headers={"api-key": "test_api_1"})
    user = response.json()["user"]
    followers_ids = [us["id"] for us in user["followers"]]
    assert 2 in followers_ids


def test_follow_without_api_key(client):
    response = client.post("/api/users/2/follow")
    assert response.status_code == 401
    assert response.json()["error_message"] == "API key is necceccary"


def test_unfollow_without_api_key(client):
    response = client.delete("/api/users/2/follow")
    assert response.status_code == 401