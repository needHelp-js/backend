from app.models import Game, Player
from fastapi import status
from pony.orm import db_session


def test_getGames_success(client, dataListGames):

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "g1", "playerCount": 1},
        {"id": 5, "name": "g5", "playerCount": 4},
    ]


def test_getGames_game_with_no_players(client, dataGameNoPlayers):
    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "g1", "playerCount": 0}]


def test_getGames_no_games(client):

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == []


def test_createGame_success(client):
    gameName = "Game test"
    hostNickname = "test_host_nickname"

    response = client.post(
        "/games", json={"gameName": gameName, "hostNickname": hostNickname}
    )

    assert response.status_code == status.HTTP_201_CREATED
    with db_session:
        game = Game.get(name=gameName)
        player = Player.get(nickname=hostNickname)

        playerCount = len(game.players)
        assert playerCount == 1

    assert response.json() == {"idPartida": game.id, "idHost": player.id}


def test_createGame_failure_game_already_exists(client):
    gameName = "Game test"
    hostNickname = "test_host_nickname"

    with db_session:
        player = Player(nickname=hostNickname, turnOrder=0)
        Game(name=gameName, host=player)

    response = client.post(
        "/games", json={"gameName": gameName, "hostNickname": hostNickname}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Error" in response.json()
