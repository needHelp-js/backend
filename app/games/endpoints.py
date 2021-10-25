from fastapi import APIRouter, Response, status, APIRouter, WebSocket
from app.models import *
from starlette.websockets import WebSocketDisconnect
from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected
from .connections import GameConnectionManager
from random import randint


router = APIRouter(prefix="/games")
manager = GameConnectionManager()


@router.get("/{gameID}/dice/{playerID}")
async def getDice(gameID: int, playerID: int, response: Response):
    with db_session:
        game = Game.get(id=gameID)
        player = Player.get(id=playerID)
        if game is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "Partida no existente"}
        elif player is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "Jugador no existente"}
        elif game.currentTurn == player.turnOrder:
            return randint(1, 6)
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": "No es el turno del jugador"}


@router.websocket("/games/{gameId}/ws/{playerId}")
async def createWebsocketConnection(gameId: int, playerId: int, websocket: WebSocket):
    await websocket.accept()

    try:
        try:
            manager.connectPlayerToGame(gameId, playerId, websocket)
            await GameConnectionManager.keepAlive(websocket)
        except GameConnectionDoesNotExist:
            await websocket.send_json(
                {"Error": f"Conexión a la partida {gameId} no existe"}
            )
            await websocket.close(4404)
        except PlayerAlreadyConnected:
            await websocket.send_json(
                {
                    "Error": f"Jugador {playerId} ya tiene una conexión activa a la partida {gameId}"
                }
            )
            await websocket.close(4409)
            raise WebSocketDisconnect

    except WebSocketDisconnect:
        manager.disconnectPlayerFromGame(gameId, playerId)
