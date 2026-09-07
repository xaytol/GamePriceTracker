def test_root_endpoint(client):
    """Просто проверяем, что приложение запускается и отвечает"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GamePriceTracker API is running"}