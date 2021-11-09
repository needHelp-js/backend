from random import randint
from typing import List, Tuple

from app.games.boardManager import BoardManager
from app.games.connections import GameConnectionManager
from app.games.decorators import gameRequired, isPlayersTurn, playerInGame
from app.games.events import (BEGIN_GAME_EVENT, DICE_ROLL_EVENT,
                              ENTER_ROOM_EVENT, MOVE_PLAYER_EVENT,
                              PLAYER_JOINED_EVENT, SUSPICION_MADE_EVENT)
from app.games.exceptions import (GameConnectionDoesNotExist,
                                  PlayerAlreadyConnected)
from app.games.schemas import (AvailableGameSchema, CreateGameSchema,
                               MovePlayerSchema, SuspectSchema, joinGameSchema)
from app.models import Card, Game, Player
from fastapi import APIRouter, Response, WebSocket, status
from pony.orm import commit, db_session
from pony.orm.core import flush
from starlette.websockets import WebSocketDisconnect

router = APIRouter(prefix="/games")
manager = GameConnectionManager()
board = BoardManager()


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
                board.createBoard()
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


@router.get("/{gameId}/availablePositions/{playerId}")
@isPlayersTurn
async def availablePositions(
    gameId: int, playerId: int, diceNumber: int, response: Response
):

    if diceNumber < 1 or diceNumber > 6:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Error": "Número del dado incorrecto"}

    with db_session:
        game = Game.get(id=gameId)
        player = Player.get(id=playerId)

        availablePositions, availableRooms = board.calculatePositions(
            player, diceNumber
        )
        return {
            "availablePositions": availablePositions,
            "availableRooms": availableRooms,
        }


@router.patch("/{gameId}/move/{playerId}")
@isPlayersTurn
async def movePlayer(
    gameId: int,
    playerId: int,
    data: MovePlayerSchema,
    response: Response,
):
    if data.diceNumber < 1 or data.diceNumber > 6:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Error": "Número del dado incorrecto"}

    with db_session:

        game = Game.get(id=gameId)
        player = Player.get(id=playerId)

        if data.position == (-1, -1) and data.room == "":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": "Faltan parámetros"}

        elif data.position != (-1, -1) and data.room != "":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": "Parámetros incorrectos"}

        elif data.room != "":

            if board.checkRoom(player, data.diceNumber, data.room):
                player.room = board.getRoomId(data.room)
                player.position = None
                await manager.broadcastToGame(
                    game.id,
                    {
                        "type": ENTER_ROOM_EVENT,
                        "payload": {
                            "playerId": player.id,
                            "playerRoom": board.getRoomName(player.room),
                        },
                    },
                )

            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "Recinto no disponible para este jugador."}

        else:

            if board.checkPosition(player, data.diceNumber, data.position):

                position = board.getPositionIdFromTuple(data.position)
                player.position = position
                player.room = None
                await manager.broadcastToGame(
                    game.id,
                    {
                        "type": MOVE_PLAYER_EVENT,
                        "payload": {
                            "playerId": player.id,
                            "playerPosition": tuple(data.position),
                        },
                    },
                )
            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "Posición no disponible para este jugador."}


@router.get("/{gameId}")
@gameRequired
@playerInGame
async def getGameDetails(gameId: int, playerId: int, response: Response):
    with db_session:

        game = Game.get(id=gameId)

        dict = game.to_dict(
            related_objects=True, with_collections=True, exclude="cards"
        )
        excluded_fields = ["hostedGame", "currentGame"]

        dict["players"] = [p.to_dict(exclude=excluded_fields) for p in dict["players"]]

        dict["host"] = dict["host"].to_dict(exclude=excluded_fields)

        for player in dict["players"]:
            player["position"] = board.getPositionTupleFromId(player["position"])
            player["room"] = board.getRoomName(player["room"])

        dict["host"]["position"] = board.getPositionTupleFromId(
            dict["host"]["position"]
        )
        dict["host"]["room"] = board.getRoomName(dict["host"]["room"])

        return dict


@router.post("/{gameId}/suspect/{playerId}")
@isPlayersTurn
async def suspect(
    gameId: int, playerId: int, schema: SuspectSchema, response: Response
):

    with db_session:

        player = Player[playerId]

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
                "type": SUSPICION_MADE_EVENT,
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
