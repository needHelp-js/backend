from random import randint
from typing import List

from app.games.connections import GameConnectionManager
from app.games.events import DICE_ROLL_EVENT, BEGIN_GAME_EVENT
from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected
from app.games.schemas import AvailableGameSchema
from app.models import Game, Player
from fastapi import APIRouter, Response, WebSocket, status
from pony.orm import db_session
from pony.orm.core import flush
from starlette.websockets import WebSocketDisconnect

from .schemas import CreateGameSchema

router = APIRouter(prefix="/games")
manager = GameConnectionManager()


@router.post("", status_code=status.HTTP_201_CREATED)
def createGame(gameCreationData: CreateGameSchema, response: Response):
    with db_session:
        if Game.exists(name=gameCreationData.gameName):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": f"Partida {gameCreationData.gameName} ya existe"}

        hostPlayer = Player(nickname=gameCreationData.hostNickname)
        newGame = Game(name=gameCreationData.gameName, host=hostPlayer)

        flush()

        newGame.players.add(hostPlayer)

        manager.createGameConnection(newGame.id)

    return {"idPartida": newGame.id, "idHost": hostPlayer.id}


@router.get("", response_model=List[AvailableGameSchema])
async def getGames():
    with db_session:
        games = Game.select(lambda p: len(p.players) < 6 and p.started == False)[:]

        gamesList = []

        for game in games:
            gameDict = game.to_dict(["id", "name"])
            gameDict.update(playerCount=len(game.players))

            gamesList.append(gameDict)

        return gamesList


@router.patch("/{gameID}/begin/{playerID}")
async def beginGame(gameID: int, playerID: int, response: Response):
    with db_session:
        game = Game.get(id=gameID)
        player = Player.get(id=playerID)
        if game is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "Partida no existente"}
        elif player is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "Jugador no existente"}
        elif game.host.id == player.id:
            if game.started == False:
                game.startGame()
                response.status_code = status.HTTP_204_NO_CONTENT
                await manager.broadcastToGame(
                    gameID, {"type": BEGIN_GAME_EVENT, "payload": None}
                )
            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "La partida ya empezó"}
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": "El jugador no es el host"}


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
            ans = randint(1, 6)
            await manager.broadcastToGame(
                gameID, {"type": DICE_ROLL_EVENT, "payload": ans}
            )
            game.incrementTurn()
            response.status_code = status.HTTP_204_NO_CONTENT
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
