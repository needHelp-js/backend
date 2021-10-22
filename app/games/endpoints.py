from fastapi import APIRouter, Response, WebSocket, status
from starlette.websockets import WebSocketDisconnect

from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected
from .connections import GameConnectionManager

router = APIRouter(prefix="/games")

manager = GameConnectionManager()


@router.websocket("/{gameId}/ws/{playerId}")
async def createWebsocketConnection(
    gameId: int, playerId: int, websocket: WebSocket, response: Response
):
    await websocket.accept()

    try:
        manager.connectPlayerToGame(gameId, playerId, websocket)
    except GameConnectionDoesNotExist:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": f"Conexión a la partida {gameId} no existe"}
    except PlayerAlreadyConnected:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "Error": f"Jugador {playerId} ya tiene una conexión activa a la partida {gameId}"
        }

    try:
        manager.keepAlive(websocket)
    except WebSocketDisconnect:
        manager.disconnectPlayerFromGame(gameId, playerId)
