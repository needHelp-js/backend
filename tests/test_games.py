from fastapi import status
from pony.orm import db_session

from app.models import Player, Game


def test_getGames_success(client, data):

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "g1", "playerCount": 1},
        {"id": 5, "name": "g5", "playerCount": 4},
    ]


def test_getGames_no_games(client):

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == []
