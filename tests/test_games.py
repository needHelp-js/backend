from app.games.endpoints import manager
from app.games.events import BEGIN_GAME_EVENT, PLAYER_JOINED_EVENT
from app.models import Game, Player
from fastapi import status
from pony.orm import db_session


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


def test_beginGame_nonExistentGame(client, beginGameData):
    response = client.patch("/games/4/begin/6")
    assert response.status_code == 404
    assert response.json() == {"Error": "Partida no existente"}


def test_beginGame_nonExistentPlayer(client, beginGameData):
    response = client.patch("/games/1/begin/6")
    assert response.status_code == 404
    assert response.json() == {"Error": "Jugador no existente"}


def test_beginGame_notEnoughPlayers(client, beginGameData):
    response = client.patch("/games/3/begin/5")
    assert response.status_code == 403
    assert response.json() == {
        "Error": "La partida no tiene la cantidad de jugadores suficientes como para ser iniciada"
    }


def test_beginGame_playerIsNotHost(client, beginGameData):
    response = client.patch("/games/1/begin/2")
    assert response.status_code == 403
    assert response.json() == {"Error": "El jugador no es el host"}


def test_beginGame_gameAlreadyStarted(client, beginGameData):
    response = client.patch("/games/2/begin/3")
    assert response.status_code == 403
    assert response.json() == {"Error": "La partida ya empezó"}


def test_beginGame_successCase(client, beginGameData):

    manager.createGameConnection(1)

    with client.websocket_connect("games/1/ws/1") as websocket:
        response = client.patch("games/1/begin/1")
        assert response.status_code == 204
        ans = websocket.receive_json()["type"]
        assert ans == BEGIN_GAME_EVENT


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


def test_joinGame_success(client, dataGameNoPlayers):

    manager.createGameConnection(1)

    with client.websocket_connect("/games/1/ws/2") as websocket:
        response = client.patch("/games/1/join", json={"playerNickname": "p2"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"playerId": 2}

        data = websocket.receive_json()
        with db_session:
            player = Player.get(nickname="p2")
            assert data == {
                "type": PLAYER_JOINED_EVENT,
                "payload": {"playerId": player.id, "playerNickname": player.nickname},
            }


def test_joinGame_failure_gameDoesntExist(client):

    response = client.patch("/games/1/join", json={"playerNickname": "p2"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "Partida 1 no existe."}


def test_joinGame_failure_playerAlreadyInGame(client, dataListGames):

    response = client.patch("/games/1/join", json={"playerNickname": "p0"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "Jugador p0 ya se encuentra en la partida 1"}


def test_joinGame_failure_gameStarted(client, dataListGames):

    response = client.patch("/games/3/join", json={"playerNickname": "player_test"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "La partida 3 ya esta empezada."}


def test_joinGame_failure_gameIsFull(client, dataListGames):

    response = client.patch("/games/2/join", json={"playerNickname": "player_test"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "La partida 2 ya esta llena."}


def test_getGameDetails_success(client, dataListGames):

    response = client.get("/games/1", params={"playerId": 0})

    assert response.json() == {
        "id": 1,
        "name": "g1",
        "started": False,
        "currentTurn": 0,
        "players": [{"id": 0, "nickname": "p0", "turnOrder": None, "room": None}],
        "host": {"id": 0, "nickname": "p0", "turnOrder": None, "room": None},
    }


def test_getGameDetails_startedGame(client, dataListGames):

    with db_session:
        g1 = Game[1]
        g1.startGame()

    response = client.get("/games/1", params={"playerId": 0})

    assert response.json() == {
        "id": 1,
        "name": "g1",
        "started": True,
        "currentTurn": 1,
        "players": [{"id": 0, "nickname": "p0", "turnOrder": 1, "room": None}],
        "host": {"id": 0, "nickname": "p0", "turnOrder": 1, "room": None},
    }


def test_getGameDetails_multiplePlayers(client, dataTirarDado):

    response = client.get("/games/1", params={"playerId": 1})

    assert response.json() == {
        "id": 1,
        "name": "g1",
        "started": False,
        "currentTurn": 1,
        "players": [
            {"id": 1, "nickname": "p1", "turnOrder": 1, "room": None},
            {"id": 2, "nickname": "p2", "turnOrder": 2, "room": None},
        ],
        "host": {"id": 1, "nickname": "p1", "turnOrder": 1, "room": None},
    }


def test_sospechar_success(client, dataCards):

    manager.createGameConnection(1)

    with client.websocket_connect("/games/1/ws/1") as websocket:
        response = client.post(
            "/games/1/sospechar/1",
            json={"card1Name": "Conde", "card2Name": "Drácula"},
        )
        assert response.status_code == 204
        ans = websocket.receive_json()["payload"]
        assert ans == {
            "playerId": 1,
            "card1Name": "Conde",
            "card2Name": "Drácula",
            "roomId": None,
        }


def test_sospechar_card1NoExists(client, dataCards):

    response = client.post(
        "/games/1/sospechar/1",
        json={"card1Name": "Perro", "card2Name": "Condesa"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "La carta Perro no existe"}


def test_sospechar_card2NoExists(client, dataCards):

    response = client.post(
        "/games/1/sospechar/1",
        json={"card1Name": "Condesa", "card2Name": "Gato"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "La carta Gato no existe"}


def test_sospechar_twoVictimas(client, dataCards):

    response = client.post(
        "/games/1/sospechar/1",
        json={"card1Name": "Conde", "card2Name": "Condesa"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"Error": "Debes mandar una victima y un monstruo"}


def test_sospechar_noCurrentTurn(client, dataCards):

    response = client.post(
        "/games/1/sospechar/2",
        json={"card1Name": "Conde", "card2Name": "Condesa"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "No es el turno del jugador"}
