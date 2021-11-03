from app.games.decorators import gameRequired, playerInGame
from app.models import Game, Player
from fastapi import Response
from pony.orm.core import db_session, flush
from starlette.testclient import TestClient


def test_gameRequired_success(app, dataTirarDado):
    @app.get("/test")
    @gameRequired
    async def decoratedFunc(gameId: int, response: Response):
        return {"Success": "success"}

    client = TestClient(app)

    result = client.get("/test", params={"gameId": 1})
    assert result.json() == {"Success": "success"}


def test_gameRequired_gameNoExistent(app, dataTirarDado):
    @app.get("/test")
    @gameRequired
    async def decoratedFunc(gameId: int, response: Response):
        return {"Success": "success"}

    client = TestClient(app)

    result = client.get("/test", params={"gameId": 2})
    assert result.status_code == 404
    assert result.json() == {"Error": "Partida 2 no existe."}


def test_playerInGame_success(app, dataTirarDado):
    @app.get("/test")
    @playerInGame
    async def decoratedFunc(gameId: int, playerId: int, response: Response):
        return {"Success": "success"}

    client = TestClient(app)

    result = client.get("/test", params={"gameId": 1, "playerId": 1})
    assert result.json() == {"Success": "success"}


def test_playerInGame_playerNoExists(app, dataTirarDado):
    @app.get("/test")
    @playerInGame
    async def decoratedFunc(gameId: int, playerId: int, response: Response):
        return {"Success": "success"}

    client = TestClient(app)

    result = client.get("/test", params={"gameId": 1, "playerId": 3})
    assert result.status_code == 404
    assert result.json() == {"Error": "El jugador 3 no existe."}


def test_playerInGame_playerInNoGame(app, dataTirarDado):
    @app.get("/test")
    @playerInGame
    async def decoratedFunc(gameId: int, playerId: int, response: Response):
        return {"Success": "success"}

    client = TestClient(app)

    with db_session:
        p4 = Player(id=4, nickname="p4")

    result = client.get("/test", params={"gameId": 1, "playerId": 4})
    assert result.status_code == 403
    assert result.json() == {"Error": "El jugador 4 no esta en la partida 1."}


def test_playerInGame_playerInOtherGame(app, dataTirarDado):
    @app.get("/test")
    @playerInGame
    async def decoratedFunc(gameId: int, playerId: int, response: Response):
        return {"Success": "success"}

    client = TestClient(app)

    with db_session:
        p4 = Player(id=4, nickname="p4")
        g2 = Game(id=2, name="g2", currentTurn=1, host=p4)
        flush()
        g2.players.add(p4)

    result = client.get("/test", params={"gameId": 1, "playerId": 4})
    assert result.status_code == 403
    assert result.json() == {"Error": "El jugador 4 no esta en la partida 1."}
