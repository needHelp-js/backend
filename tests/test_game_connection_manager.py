import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket
from app.games.exceptions import (
    GameConnectionDoesNotExist,
    PlayerAlreadyConnected,
    PlayerNotConnected,
)
from app.games.endpoints import manager


def test_connectPlayerToGame_success(app, gameManager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, 1, websocket)

        assert 1 in gameManager._games[1]
        assert websocket == gameManager._games[1][1]


def test_connectPlayerToGame_raiseExceptions(app, gameManager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        with pytest.raises(GameConnectionDoesNotExist):
            gameManager.connectPlayerToGame(1, 1, websocket)

    gameManager.createGameConnection(1)

    with client.websocket_connect("/wsTestRoute") as websocket:
        gameManager.connectPlayerToGame(1, 1, websocket)

    with client.websocket_connect("/wsTestRoute") as websocket:
        with pytest.raises(PlayerAlreadyConnected):
            gameManager.connectPlayerToGame(1, 1, websocket)


def test_disconnectPlayerFromGame_success(app, gameManager):
    gameManager.createGameConnection(1)

    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        gameManager.connectPlayerToGame(1, 1, websocket)
        gameManager.connectPlayerToGame(1, 2, websocket)

    gameManager.disconnectPlayerFromGame(1, 1)

    assert 1 not in gameManager._games[1]
    assert 2 in gameManager._games[1]

    gameManager.disconnectPlayerFromGame(1, 2)

    assert 1 not in gameManager._games


def test_disconnectPlayerFromGame_raiseExceptions(gameManager):

    with pytest.raises(GameConnectionDoesNotExist):
        gameManager.disconnectPlayerFromGame(1, 1)

    gameManager.createGameConnection(1)

    with pytest.raises(PlayerNotConnected):
        gameManager.disconnectPlayerFromGame(1, 2)


def test_sendMessageToPlayer_success(app, gameManager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, 1, websocket)
        await gameManager.sendToPlayer(1, 1, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        data = websocket.receive_json()
        assert {"msg": "data"} == data


def test_sendMessageToPlayer_raiseExceptions(app, gameManager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, 1, websocket)
        with pytest.raises(GameConnectionDoesNotExist):
            await gameManager.sendToPlayer(2, 1, {"msg": "data"})
        with pytest.raises(PlayerNotConnected):
            await gameManager.sendToPlayer(1, 2, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute"):
        pass


def test_broadcastToGame_success(app, gameManager):
    gameManager.createGameConnection(1)

    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        gameManager.connectPlayerToGame(1, 1, websocket)
        await gameManager.broadcastToGame(1, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        data = websocket.receive_json()
        assert {"msg": "data"} == data


def test_broadcastToGame_raiseExcpetions(app, gameManager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        with pytest.raises(GameConnectionDoesNotExist):
            await gameManager.broadcastToGame(1, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute"):
        pass


def test_createWebsocketConnection(app, gameManager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        manager.createGameConnection(1)

    client = TestClient(app)

    with client.websocket_connect("/games/1/ws/1") as websocket:
        data = websocket.receive_json()
        assert data == {"Error": "Conexión a la partida 1 no existe"}

    with client.websocket_connect("/wsTestRoute") as websocket:
        manager.connectPlayerToGame(1, 1, websocket)

    with client.websocket_connect("/games/1/ws/1") as websocket:
        data = websocket.receive_json()
        assert data == {
            "Error": "Jugador 1 ya tiene una conexión activa a la partida 1"
        }

    assert 1 not in manager._games
