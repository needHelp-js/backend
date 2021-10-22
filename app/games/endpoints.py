from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected
from .connections import GameConnectionManager

router = APIRouter(prefix="/games")

manager = GameConnectionManager()


@router.websocket("/games/{gameId}/ws/{playerId}")
async def createWebsocketConnection(gameId: int, playerId: int, websocket: WebSocket):
    await websocket.accept()

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
    except WebSocketDisconnect:
        manager.disconnectPlayerFromGame(gameId, playerId)
