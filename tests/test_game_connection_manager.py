import asyncio
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket
from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected, PlayerNotConnected

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

def test_disconnectPlayerFromGame_success(app, gameManager):
    gameManager.createGameConnection(1)
    
    @app.websocket('/wsTestRoute')
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    
    client = TestClient(app)

    with client.websocket_connect('/wsTestRoute') as websocket:
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
    @app.websocket('/wsTestRoute')
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, 1, websocket)
        await gameManager.sendToPlayer(1, 1, {"msg": "data"})   
    
    client = TestClient(app)

    with client.websocket_connect('/wsTestRoute') as websocket:
        data = websocket.receive_json()
        assert {"msg": "data"} == data
    
def test_sendMessageToPlayer_raiseExceptions(app, gameManager):
    @app.websocket('/wsTestRoute')
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, 1, websocket)
        with pytest.raises(GameConnectionDoesNotExist):
            await gameManager.sendToPlayer(2, 1, {"msg": "data"})
        with pytest.raises(PlayerNotConnected):
            await gameManager.sendToPlayer(1, 2, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect('/wsTestRoute'):
        pass

@pytest.mark.asyncio
async def test_broadcastToGame_success(app, gameManager):
    @app.websocket('/wsTestRoute{playerID}')
    async def wsTestRoute(websocket: WebSocket, playerID : int):
        await websocket.accept()
        gameManager.createGameConnection(1)
        gameManager.connectPlayerToGame(1, playerID, websocket)

    async def clientFunction(playerID : int):
        client = TestClient(app)
        async with client.websocket_connect(f'/wsTestRoute{playerID}') as websocket:
            data = await websocket.receive_json()
            assert "msg" == data
    
    #for playerID in range(1,4):
    #    clientFunction(playerID)

    tasks = [clientFunction(i) for i in range(4)]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    await gameManager.broadcastToGame(1, "msg")