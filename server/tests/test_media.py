import io

def test_save_media(client):
    resp = client.post("/api/medias", headers={"api-key": "test_api_1"})
    # 1. Готовим файл в памяти
    file_content = b"fake image content"
    file = ("test.jpg", io.BytesIO(file_content), "image/jpeg")

    # 2. Отправляем
    response = client.post(
        "/api/medias",
        headers={"api-key": "test_api_1"},
        files={"file": file},  # ← files= для UploadFile
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)


    # 3. Проверяем ответ
    assert response.status_code == 200
    body = response.json()
    assert body["result"] is True
    assert "media_id" in body
    media_id = body["media_id"]