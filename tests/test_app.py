from unittest.mock import patch

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Steam Live Players" in response.text
    assert "게임별 비교" in response.data.decode("utf-8")


@patch("app.get_players", side_effect=[100, 200, 300])
def test_players_api(mock_players):
    response = client.get("/api/players")
    assert response.status_code == 200
    assert [game["players"] for game in response.json["games"]] == [100, 200, 300]


def test_unknown_game():
    response = client.get("/api/players?games=unknown")
    assert response.status_code == 400
    assert "알 수 없는 게임" in response.json["error"]
