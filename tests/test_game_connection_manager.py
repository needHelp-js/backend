import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket
from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected

def test_connectPlayerToGame_success(app, gameManager):

    @app.websocket('/wsTestRoute')
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
    
    client = TestClient(app)

    with client.websocket_connect('/wsTestRoute') as websocket:
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, 1, websocket)

        assert 1 in gameManager._games[1]
        assert websocket == gameManager._games[1][1]

def test_connectPlayerToGame_raiseExceptions(app, gameManager):

    @app.websocket('/wsTestRoute')
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect('/wsTestRoute') as websocket:
        with pytest.raises(GameConnectionDoesNotExist):
            gameManager.connectPlayerToGame(1, 1, websocket)
    
    gameManager.createGameConnection(1)

    with client.websocket_connect('/wsTestRoute') as websocket:
        gameManager.connectPlayerToGame(1, 1, websocket)
    
    with client.websocket_connect('/wsTestRoute') as websocket:
        with pytest.raises(PlayerAlreadyConnected):
            gameManager.connectPlayerToGame(1, 1, websocket)