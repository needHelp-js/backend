from app.enums import MonstersNames, RoomsNames, VictimsNames
from app.games.endpoints import availablePositions, manager
from app.games.events import (
    BEGIN_GAME_EVENT,
    DEAL_CARDS_EVENT,
    PLAYER_JOINED_EVENT,
    PLAYER_REPLIED_EVENT,
    SUSPICION_FAILED_EVENT,
    SUSPICION_MADE_EVENT,
    SUSPICION_RESPONSE_EVENT,
    TURN_ENDED_EVENT,
    YOU_ARE_SUSPICIOUS_EVENT,
)
from app.models import Game, Player
from fastapi import status
from pony.orm import db_session
from pony.orm.core import flush

def test_createGame_success(client):
    gameName = "Game test"
    hostNickname = "test_host_nickname"

    with db_session:
        game = Game.get(name=gameName)
        assert game == None

    response = client.post(
        "/games", json={"gameName": gameName, "hostNickname": hostNickname}
    )

    assert response.status_code == status.HTTP_201_CREATED
    with db_session:
        game = Game.get(name=gameName)
        player = Player.get(nickname=hostNickname)
        
        playerCount = len(game.players)
        assert playerCount == 1
        assert game.password == ""

    assert response.json() == {"idPartida": game.id, "idHost": player.id}

def test_createGameWithPassword_success(client):
    gameName = "Game test"
    hostNickname = "test_host_nickname"
    password = "Password"

    with db_session:
        game = Game.get(name=gameName)
        assert game == None

    response = client.post(
        "/games", json={"gameName": gameName, "hostNickname": hostNickname, "password": password}
    )

    assert response.status_code == status.HTTP_201_CREATED
    with db_session:
        game = Game.get(name=gameName)
        player = Player.get(nickname=hostNickname)

        assert game.password == password
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
        {"id": 1, "name": "g1", "hasPassword": False, "playerCount": 1},
        {"id": 5, "name": "g5", "hasPassword": False, "playerCount": 4},
    ]

def test_getGamesWithPassword_success(client, dataPasswordGame):

    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "g1", "hasPassword": True, "playerCount": 1},
    ]


def test_getGames_game_with_no_players(client, dataGameNoPlayers):
    response = client.get("/games")

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "g1", "hasPassword": False, "playerCount": 0}]


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


def test_beginGame_success_PlayerCardsSent(client, beginGameData):

    manager.createGameConnection(1)

    with client.websocket_connect("games/1/ws/1") as p1ws, client.websocket_connect(
        "games/1/ws/2"
    ) as p2ws:
        response = client.patch("/games/1/begin/1")

        assert response.status_code == 204

        assert p1ws.receive_json()["type"] == BEGIN_GAME_EVENT

        assert p2ws.receive_json()["type"] == BEGIN_GAME_EVENT

        ans1 = p1ws.receive_json()
        assert ans1["type"] == DEAL_CARDS_EVENT

        ans2 = p2ws.receive_json()
        assert ans2["type"] == DEAL_CARDS_EVENT

        with db_session:
            p1Cards = [card.name for card in Player[1].cards]
            p2Cards = [card.name for card in Player[2].cards]

            assert ans1["payload"].sort() == p1Cards.sort()
            assert ans2["payload"].sort() == p2Cards.sort()


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


def test_availablePositions_wrongDiceNumber(client, dataBoard):
    response = client.get("/games/1/availablePositions/1", params={"diceNumber": -1})
    assert response.status_code == 400
    assert response.json() == {"Error": "Número del dado incorrecto"}
    response = client.get("/games/1/availablePositions/1", params={"diceNumber": 7})
    assert response.status_code == 400
    assert response.json() == {"Error": "Número del dado incorrecto"}


def test_availablePositions_success(client, dataBoard):
    response = client.get("/games/1/availablePositions/1", params={"diceNumber": 3})
    assert response.json() == {
        "availablePositions": [[0, 6], [1, 6], [2, 6], [3, 6]],
        "availableRooms": ["Cochera"],
    }


def test_movePlayer_wrongDiceNumber(client, dataBoard):
    response = client.patch(
        "/games/1/move/1", json={"diceNumber": -1, "room": "BIBLIOTECA"}
    )
    assert response.status_code == 400
    assert response.json() == {"Error": "Número del dado incorrecto"}
    response = client.patch(
        "/games/1/move/1", json={"diceNumber": 7, "room": "BIBLIOTECA"}
    )
    assert response.status_code == 400
    assert response.json() == {"Error": "Número del dado incorrecto"}


def test_movePlayer_correctRoom(client, dataBoard):
    manager.createGameConnection(1)
    with client.websocket_connect("/games/1/ws/1") as websocket:
        response = client.patch(
            "/games/1/move/1", json={"diceNumber": 3, "room": "Cochera"}
        )
        ans = websocket.receive_json()
        type = ans["type"]
        payload = ans["payload"]
        assert type == "ENTER_ROOM_EVENT"
        assert payload == {"playerId": 1, "playerRoom": "Cochera"}


def test_movePlayer_wrongRoom(client, dataBoard):
    response = client.patch(
        "/games/1/move/1", json={"diceNumber": 3, "room": "BIBLIOTECA"}
    )
    assert response.json() == {"Error": "Recinto no disponible para este jugador."}


def test_movePlayer_correctPosition(client, dataBoard):
    manager.createGameConnection(1)

    with client.websocket_connect("/games/1/ws/1") as websocket:
        response = client.patch(
            "/games/1/move/1", json={"diceNumber": 3, "position": [1, 6]}
        )
        ans = websocket.receive_json()
        type = ans["type"]
        payload = ans["payload"]
        assert type == "MOVE_PLAYER_EVENT"
        assert payload == {"playerId": 1, "playerPosition": [1, 6]}


def test_movePlayer_wrongPosition(client, dataBoard):
    response = client.patch(
        "/games/1/move/1", json={"diceNumber": 3, "position": [5, 6]}
    )
    assert response.json() == {"Error": "Posición no disponible para este jugador."}


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
        "players": [
            {
                "id": 0,
                "nickname": "p0",
                "turnOrder": None,
                "isSuspecting": False,
                "position": None,
                "room": None,
            }
        ],
        "host": {
            "id": 0,
            "nickname": "p0",
            "turnOrder": None,
            "isSuspecting": False,
            "position": None,
            "room": None,
        },
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
        "players": [
            {
                "id": 0,
                "nickname": "p0",
                "turnOrder": 1,
                "isSuspecting": False,
                "position": [0, 6],
                "room": None,
            }
        ],
        "host": {
            "id": 0,
            "nickname": "p0",
            "turnOrder": 1,
            "isSuspecting": False,
            "position": [0, 6],
            "room": None,
        },
    }


def test_getGameDetails_multiplePlayers(client, dataTirarDado):

    response = client.get("/games/1", params={"playerId": 1})

    assert response.json() == {
        "id": 1,
        "name": "g1",
        "started": False,
        "currentTurn": 1,
        "players": [
            {
                "id": 1,
                "nickname": "p1",
                "turnOrder": 1,
                "position": None,
                "room": None,
                "isSuspecting": False,
            },
            {
                "id": 2,
                "nickname": "p2",
                "turnOrder": 2,
                "position": None,
                "room": None,
                "isSuspecting": False,
            },
        ],
        "host": {
            "id": 1,
            "nickname": "p1",
            "turnOrder": 1,
            "isSuspecting": False,
            "position": None,
            "room": None,
        },
    }


def test_suspect_success(client, dataSuspect):

    manager.createGameConnection(1)

    with client.websocket_connect(
        "/games/1/ws/1"
    ) as websocket1, client.websocket_connect("/games/1/ws/2") as websocket2:

        response = client.post(
            "/games/1/suspect/1",
            json={
                "card1Name": VictimsNames.CONDE.value,
                "card2Name": MonstersNames.DRACULA.value,
            },
        )
        assert response.status_code == 204
        ans = websocket1.receive_json()
        assert ans["type"] == SUSPICION_MADE_EVENT
        assert ans["payload"] == {
            "playerId": 1,
            "card1Name": VictimsNames.CONDE.value,
            "card2Name": MonstersNames.DRACULA.value,
            "roomName": RoomsNames.LABORATORIO.value,
        }

        ans = websocket2.receive_json()
        assert ans["type"] == SUSPICION_MADE_EVENT
        assert ans["payload"] == {
            "playerId": 1,
            "card1Name": VictimsNames.CONDE.value,
            "card2Name": MonstersNames.DRACULA.value,
            "roomName": RoomsNames.LABORATORIO.value,
        }

        ans = websocket2.receive_json()
        assert ans["type"] == YOU_ARE_SUSPICIOUS_EVENT
        assert ans["payload"] == {"playerId": 1, "cards": [MonstersNames.DRACULA.value]}

        with db_session:
            assert Player[1].isSuspecting


def test_suspect_success_otherPlayerWithCard(client, dataSuspect):

    manager.createGameConnection(1)

    with client.websocket_connect(
        "/games/1/ws/1"
    ) as websocket1, client.websocket_connect("/games/1/ws/3") as websocket3:

        response = client.post(
            "/games/1/suspect/1",
            json={
                "card1Name": VictimsNames.CONDE.value,
                "card2Name": MonstersNames.HOMBRE_LOBO.value,
            },
        )
        assert response.status_code == 204
        ans = websocket1.receive_json()
        assert ans["type"] == SUSPICION_MADE_EVENT
        assert ans["payload"] == {
            "playerId": 1,
            "card1Name": VictimsNames.CONDE.value,
            "card2Name": MonstersNames.HOMBRE_LOBO.value,
            "roomName": RoomsNames.LABORATORIO.value,
        }

        ans = websocket3.receive_json()
        assert ans["type"] == SUSPICION_MADE_EVENT
        assert ans["payload"] == {
            "playerId": 1,
            "card1Name": VictimsNames.CONDE.value,
            "card2Name": MonstersNames.HOMBRE_LOBO.value,
            "roomName": RoomsNames.LABORATORIO.value,
        }

        ans = websocket3.receive_json()
        assert ans["type"] == YOU_ARE_SUSPICIOUS_EVENT
        assert ans["payload"] == {"playerId": 1, "cards": [VictimsNames.CONDE.value]}

        with db_session:
            assert Player[1].isSuspecting


def test_suspect_noPlayerWithCards(client, dataSuspect):
    manager.createGameConnection(1)

    with client.websocket_connect(
        "/games/1/ws/1"
    ) as websocket1, client.websocket_connect("/games/1/ws/2") as websocket2:

        response = client.post(
            "/games/1/suspect/1",
            json={
                "card1Name": VictimsNames.MAYORDOMO.value,
                "card2Name": MonstersNames.HOMBRE_LOBO.value,
            },
        )
        assert response.status_code == 204
        ans = websocket1.receive_json()
        assert ans["type"] == SUSPICION_MADE_EVENT
        assert ans["payload"] == {
            "playerId": 1,
            "card1Name": VictimsNames.MAYORDOMO.value,
            "card2Name": MonstersNames.HOMBRE_LOBO.value,
            "roomName": RoomsNames.LABORATORIO.value,
        }

        ans = websocket2.receive_json()
        assert ans["type"] == SUSPICION_MADE_EVENT
        assert ans["payload"] == {
            "playerId": 1,
            "card1Name": VictimsNames.MAYORDOMO.value,
            "card2Name": MonstersNames.HOMBRE_LOBO.value,
            "roomName": RoomsNames.LABORATORIO.value,
        }

        ans = websocket1.receive_json()
        assert ans["type"] == SUSPICION_FAILED_EVENT
        assert ans["payload"] == {
            "Error": "No hay jugadores que posean alguna de las cartas de la sospecha."
        }

        ans = websocket2.receive_json()
        assert ans["type"] == SUSPICION_FAILED_EVENT
        assert ans["payload"] == {
            "Error": "No hay jugadores que posean alguna de las cartas de la sospecha."
        }

        ans = websocket1.receive_json()
        assert ans["type"] == TURN_ENDED_EVENT
        assert ans["payload"] == {"playerId": 2}

        ans = websocket2.receive_json()
        assert ans["type"] == TURN_ENDED_EVENT
        assert ans["payload"] == {"playerId": 2}

        with db_session:
            assert not Player[1].isSuspecting


def test_suspect_playerInNoRoom(client, dataSuspect):
    manager.createGameConnection(1)

    with db_session:
        p1 = Player[1]
        p1.room = None

    with client.websocket_connect(
        "/games/1/ws/1"
    ) as websocket1, client.websocket_connect("/games/1/ws/2") as websocket2:

        response = client.post(
            "/games/1/suspect/1",
            json={
                "card1Name": VictimsNames.MAYORDOMO.value,
                "card2Name": MonstersNames.HOMBRE_LOBO.value,
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"Error": f"El jugador 1 no está en ningun recinto"}


def test_suspect_card1NoExists(client, dataCards):

    with db_session:
        p1 = Player[1]
        p1.room = 8

    response = client.post(
        "/games/1/suspect/1",
        json={"card1Name": "Perro", "card2Name": VictimsNames.CONDESA.value},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "La carta Perro no existe"}


def test_suspect_card2NoExists(client, dataCards):

    with db_session:
        p1 = Player[1]
        p1.room = 8

    response = client.post(
        "/games/1/suspect/1",
        json={"card1Name": VictimsNames.CONDESA.value, "card2Name": "Gato"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "La carta Gato no existe"}


def test_suspect_twoVictimas(client, dataCards):

    with db_session:
        p1 = Player[1]
        p1.room = 8

    response = client.post(
        "/games/1/suspect/1",
        json={
            "card1Name": VictimsNames.CONDE.value,
            "card2Name": VictimsNames.CONDESA.value,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"Error": "Debes mandar una victima y un monstruo"}


def test_suspect_noCurrentTurn(client, dataCards):

    response = client.post(
        "/games/1/suspect/2",
        json={
            "card1Name": VictimsNames.CONDE.value,
            "card2Name": VictimsNames.CONDESA.value,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "No es el turno del jugador"}


def test_replySuspect_success(client, dataSuspect):

    manager.createGameConnection(1)

    with client.websocket_connect(
        "/games/1/ws/1"
    ) as websocket1, client.websocket_connect(
        "/games/1/ws/2"
    ) as websocket2, client.websocket_connect(
        "/games/1/ws/3"
    ) as websocket3:

        with db_session:
            assert not Player[1].isSuspecting

        client.post(
            "/games/1/suspect/1",
            json={
                "card1Name": VictimsNames.CONDE.value,
                "card2Name": MonstersNames.DRACULA.value,
            },
        )

        with db_session:
            assert Player[1].isSuspecting

        websocket1.receive_json()  # SUSPICION MADE
        websocket2.receive_json()  # SUSPICION MADE
        websocket3.receive_json()  # SUSPICION MADE
        websocket2.receive_json()  # YOU ARE SUSPICIOUS

        response = client.post(
            "/games/1/replySuspect/2",
            json={"replyToPlayerId": 1, "cardName": MonstersNames.DRACULA.value},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        ans = websocket1.receive_json()  # SUSPICION RESPONSE
        assert ans["type"] == SUSPICION_RESPONSE_EVENT
        assert ans["payload"] == {
            "playerId": 2,
            "cardName": MonstersNames.DRACULA.value,
        }

        ans = websocket1.receive_json()  # SUSPICION RESPONSE
        assert ans["type"] == PLAYER_REPLIED_EVENT
        assert ans["payload"] == {"playerId": 2}

        ans = websocket2.receive_json()  # SUSPICION RESPONSE
        assert ans["type"] == PLAYER_REPLIED_EVENT
        assert ans["payload"] == {"playerId": 2}

        ans = websocket3.receive_json()  # SUSPICION RESPONSE
        assert ans["type"] == PLAYER_REPLIED_EVENT
        assert ans["payload"] == {"playerId": 2}

        ans = websocket1.receive_json()  # TURN ENDED
        assert ans["type"] == TURN_ENDED_EVENT
        assert ans["payload"] == {"playerId": 2}

        ans = websocket2.receive_json()  # TURN ENDED
        assert ans["type"] == TURN_ENDED_EVENT
        assert ans["payload"] == {"playerId": 2}

        ans = websocket3.receive_json()  # TURN ENDED
        assert ans["type"] == TURN_ENDED_EVENT
        assert ans["payload"] == {"playerId": 2}

        with db_session:
            assert Player[1].isSuspecting


def test_replySuspect_cardNoExists(client, dataSuspect):

    response = client.post(
        "/games/1/replySuspect/2",
        json={"replyToPlayerId": 1, "cardName": "Gato"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "La carta Gato no existe"}


def test_replySuspect_playerDontHaveCard(client, dataSuspect):

    response = client.post(
        "/games/1/replySuspect/2",
        json={"replyToPlayerId": 1, "cardName": VictimsNames.CONDE.value},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"Error": "El jugador 2 no tiene la carta Conde"}


def test_replySuspect_repliedNoExists(client, dataSuspect):

    response = client.post(
        "/games/1/replySuspect/2",
        json={"replyToPlayerId": 30, "cardName": VictimsNames.CONDESA.value},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"Error": "El jugador 30 no existe"}


def test_replySuspect_repliedNotInGame(client, dataSuspect):

    with db_session:
        p10 = Player(id=10, nickname="p10")

    response = client.post(
        "/games/1/replySuspect/2",
        json={"replyToPlayerId": 10, "cardName": VictimsNames.CONDESA.value},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "El jugador 10 no está en la partida 1"}


def test_replySuspect_repliedInAnotherGame(client, dataSuspect):

    with db_session:
        p10 = Player(id=10, nickname="p10")
        g2 = Game(id=2, name="p2", host=p10)

        flush()

        g2.players.add(p10)

    response = client.post(
        "/games/1/replySuspect/2",
        json={"replyToPlayerId": 10, "cardName": VictimsNames.CONDESA.value},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": "El jugador 10 no está en la partida 1"}


def test_replySuspect_repliedIsNotSuspecting(client, dataSuspect):

    response = client.post(
        "/games/1/replySuspect/2",
        json={"replyToPlayerId": 1, "cardName": VictimsNames.CONDESA.value},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"Error": f"El jugador 1 no está sospechando."}
