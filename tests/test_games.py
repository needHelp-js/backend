from app.games.endpoints import manager
from fastapi import status
from pony.orm import db_session
from app.models import Player, Game


def test_getDice_nonExistentGame(client, dataTirarDado):
    response = client.get("/games/5/dice/1")
    assert response.status_code == 404
    assert response.json() == {"Error": "Partida no existente"}


def test_getDice_nonExistentPlayer(client, dataTirarDado):
    response = client.get("/games/1/dice/6")
    assert response.status_code == 404
    assert response.json() == {"Error": "Jugador no existente"}


def test_getDice_incorrectTurn(client, dataTirarDado):
    response = client.get("/games/1/dice/2")
    assert response.status_code == 403
    assert response.json() == {"Error": "No es el turno del jugador"}


def test_getDice_success(client, dataTirarDado):

    manager.createGameConnection(1)

    with client.websocket_connect("/games/1/ws/1") as websocket:
        response = client.get("/games/1/dice/1")
        assert response.status_code == 204
        ans = websocket.receive_json()["payload"]
        assert ans == 1 or ans == 2 or ans == 3 or ans == 4 or ans == 5 or ans == 6


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
