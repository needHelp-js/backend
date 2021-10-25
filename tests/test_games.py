from app.games.endpoints import manager
from starlette.websockets import WebSocket
from fastapi.testclient import TestClient
from app.games.events import DICE_ROLL_EVENT


def test_nonExistentGame(client, data):
    response = client.get("/games/5/dice/1")
    assert response.status_code == 404
    assert response.json() == {"Error": "Partida no existente"}


def test_nonExistentPlayer(client, data):
    response = client.get("/games/1/dice/6")
    assert response.status_code == 404
    assert response.json() == {"Error": "Jugador no existente"}


def test_incorrectTurn(client, data):
    response = client.get("/games/1/dice/2")
    assert response.status_code == 403
    assert response.json() == {"Error": "No es el turno del jugador"}


def test_rollDice(client, data):

    manager.createGameConnection(1)

    with client.websocket_connect("/games/1/ws/1") as websocket:
        response = client.get("/games/1/dice/1")
        assert response.status_code == 204
        ans = websocket.receive_json()["payload"]
        assert ans == 1 or ans == 2 or ans == 3 or ans == 4 or ans == 5 or ans == 6
