from random import randint
from typing import List

from app.games.connections import GameConnectionManager
from app.games.decorators import gameRequired, playerInGame
from app.games.events import (
    BEGIN_GAME_EVENT,
    DICE_ROLL_EVENT,
    PLAYER_JOINED_EVENT,
    SOSPECHA_MADE_EVENT,
)
from app.games.exceptions import GameConnectionDoesNotExist, PlayerAlreadyConnected
from app.games.schemas import (
    AvailableGameSchema,
    CreateGameSchema,
    SospecharSchema,
    joinGameSchema,
)
from app.models import Card, Game, Player
from fastapi import APIRouter, Response, WebSocket, status
from pony.orm import db_session
from pony.orm.core import flush
from starlette.websockets import WebSocketDisconnect

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
            if game.countPlayers() <= 1:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {
                    "Error": "La partida no tiene la cantidad de jugadores suficientes como para ser iniciada"
                }
            elif game.started == False:
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


@router.patch("/{gameId}/join")
async def joinGame(gameId: int, joinGameData: joinGameSchema, response: Response):
    with db_session:

        game = Game.get(id=gameId)

        if game is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"Partida {gameId} no existe."}

        players = [p for p in game.players if p.nickname == joinGameData.playerNickname]

        if len(players) > 0:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                "Error": f"Jugador {joinGameData.playerNickname}"
                f" ya se encuentra en la partida {gameId}"
            }

        if game.started:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": f"La partida {gameId} ya esta empezada."}

        if game.countPlayers() == 6:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": f"La partida {gameId} ya esta llena."}

        player = Player(nickname=joinGameData.playerNickname)

        flush()

        game.players.add(player)

        await manager.broadcastToGame(
            game.id,
            {
                "type": PLAYER_JOINED_EVENT,
                "payload": {"playerId": player.id, "playerNickname": player.nickname},
            },
        )

        return {"playerId": player.id}


@router.get("/{gameId}")
@gameRequired
@playerInGame
async def getGameDetails(gameId: int, playerId: int, response: Response):
    with db_session:

        game = Game.get(id=gameId)

        dict = game.to_dict(related_objects=True, with_collections=True)
        excluded_fields = ["hostedGame", "currentGame"]

        dict["players"] = [p.to_dict(exclude=excluded_fields) for p in dict["players"]]

        dict["host"] = dict["host"].to_dict(exclude=excluded_fields)

        return dict


@router.post("/{gameId}/sospechar/{playerId}")
@gameRequired
@playerInGame
async def sospechar(
    gameId: int, playerId: int, schema: SospecharSchema, response: Response
):

    with db_session:
        player = Player[playerId]
        game = Game[gameId]

        if player.turnOrder != game.currentTurn:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": "No es el turno del jugador"}

        card1 = Card.get(lambda c: c.game.id == gameId and c.name == schema.card1Name)
        card2 = Card.get(lambda c: c.game.id == gameId and c.name == schema.card2Name)

        if card1 == None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"La carta {schema.card1Name} no existe"}

        if card2 == None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"La carta {schema.card2Name} no existe"}

        if {card1.type, card2.type} != {"victima", "monstruo"}:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": "Debes mandar una victima y un monstruo"}

        response.status_code = status.HTTP_204_NO_CONTENT
        await manager.broadcastToGame(
            gameId,
            {
                "type": SOSPECHA_MADE_EVENT,
                "payload": {
                    "playerId": playerId,
                    "card1Name": schema.card1Name,
                    "card2Name": schema.card2Name,
                    "roomId": player.room,
                },
            },
        )


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
