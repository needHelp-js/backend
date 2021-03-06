from os import stat
from random import randint
from typing import List, Tuple

from app.enums import CardType
from app.games.boardManager import BoardManager
from app.games.connections import GameConnectionManager
from app.games.decorators import gameRequired, isPlayersTurn, playerInGame
from app.games.events import (BEGIN_GAME_EVENT, DEAL_CARDS_EVENT,
                              DICE_ROLL_EVENT, ENTER_ROOM_EVENT,
                              GAME_ENDED_EVENT, MOVE_PLAYER_EVENT,
                              PLAYER_ACCUSED_EVENT, PLAYER_JOINED_EVENT,
                              PLAYER_LOST_EVENT, PLAYER_REPLIED_EVENT,
                              SUSPICION_FAILED_EVENT, SUSPICION_MADE_EVENT,
                              SUSPICION_RESPONSE_EVENT, TURN_ENDED_EVENT,
                              YOU_ARE_SUSPICIOUS_EVENT)
from app.games.exceptions import (GameConnectionDoesNotExist,
                                  PlayerAlreadyConnected, PlayerNotConnected)
from app.games.schemas import (AccuseSchema, AvailableGameSchema,
                               CreateGameSchema, MovePlayerSchema,
                               ReplySuspectSchema, SuspectSchema,
                               joinGameSchema)
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
        newGame = Game(
            name=gameCreationData.gameName,
            host=hostPlayer,
            password=gameCreationData.password,
        )

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

            if game.password != "":
                gameDict["hasPassword"] = True
            else:
                gameDict["hasPassword"] = False

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

                for player in game.players:

                    cards = [card.name for card in player.cards]

                    try:
                        await manager.sendToPlayer(
                            gameID,
                            player.id,
                            {"type": DEAL_CARDS_EVENT, "payload": cards},
                        )
                    except PlayerNotConnected:
                        pass

                return {}

            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "La partida ya empez??"}
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

        elif player.hasRolledDice:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": "Este jugador ya tir?? el dado"}

        elif game.currentTurn == player.turnOrder:
            ans = randint(1, 6)
            player.hasRolledDice = True
            await manager.broadcastToGame(
                gameID, {"type": DICE_ROLL_EVENT, "payload": ans}
            )
            response.status_code = status.HTTP_204_NO_CONTENT

            return {}

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
            return {"Error": f"La partida {game.name} ya esta empezada."}

        if game.countPlayers() == 6:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": f"La partida {game.name} ya esta llena."}

        if game.password != joinGameData.password:
            if game.password == "":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "Esta partida no tiene contrase??a"}
            if game.password != "":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "Contrase??a incorrecta"}

        player = Player(nickname=joinGameData.playerNickname)

        flush()

        game.players.add(player)

        try:
            await manager.broadcastToGame(
                game.id,
                {
                    "type": PLAYER_JOINED_EVENT,
                    "payload": {
                        "playerId": player.id,
                        "playerNickname": player.nickname,
                    },
                },
            )
        except GameConnectionDoesNotExist:
            manager.createGameConnection(game.id)
            await manager.broadcastToGame(
                game.id,
                {
                    "type": PLAYER_JOINED_EVENT,
                    "payload": {
                        "playerId": player.id,
                        "playerNickname": player.nickname,
                    },
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
        return {"Error": "N??mero del dado incorrecto"}

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
        return {"Error": "N??mero del dado incorrecto"}

    with db_session:

        game = Game.get(id=gameId)
        player = Player.get(id=playerId)

        if data.position == (-1, -1) and data.room == "":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": "Faltan par??metros"}

        elif data.position != (-1, -1) and data.room != "":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": "Par??metros incorrectos"}

        elif player.hasMoved:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": "Este jugador ya se movi??"}

        elif data.room != "":

            if board.checkRoom(player, data.diceNumber, data.room):
                player.room = board.getRoomId(data.room)
                player.position = None
                player.hasMoved = True
                await manager.broadcastToGame(
                    game.id,
                    {
                        "type": ENTER_ROOM_EVENT,
                        "payload": {
                            "playerId": player.id,
                            "playerNickname": player.nickname,
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
                player.hasMoved = True
                await manager.broadcastToGame(
                    game.id,
                    {
                        "type": MOVE_PLAYER_EVENT,
                        "payload": {
                            "playerId": player.id,
                            "playerNickname": player.nickname,
                            "playerPosition": tuple(data.position),
                        },
                    },
                )
            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"Error": "Posici??n no disponible para este jugador."}
    response.status_code == 204
    return {}


@router.get("/{gameId}")
@gameRequired
@playerInGame
async def getGameDetails(gameId: int, playerId: int, response: Response):
    with db_session:

        game = Game.get(id=gameId)

        dict = game.to_dict(
            related_objects=True, with_collections=True, exclude=["cards", "password"]
        )
        excluded_fields = [
            "hostedGame",
            "currentGame",
            "hasRolledDice",
            "hasMoved",
            "hasSuspected",
        ]

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

        if player.room is None:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": f"El jugador {player.nickname} no est?? en ningun recinto"}

        card1Name = schema.card1Name
        card2Name = schema.card2Name

        card1 = Card.get(lambda c: c.game.id == gameId and c.name == card1Name)
        card2 = Card.get(lambda c: c.game.id == gameId and c.name == card2Name)

        playerRoom = board.getRoomName(player.room)

        if card1 is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"La carta {card1Name} no existe"}

        if card2 is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"La carta {card2Name} no existe"}

        if {card1.type, card2.type} != {CardType.VICTIM.value, CardType.MONSTER.value}:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"Error": "Debes mandar una victima y un monstruo"}

        if player.hasSuspected:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {"Error": "Este jugador ya realiz?? una sospecha"}

        response.status_code = status.HTTP_204_NO_CONTENT
        await manager.broadcastToGame(
            gameId,
            {
                "type": SUSPICION_MADE_EVENT,
                "payload": {
                    "playerId": player.id,
                    "playerNickname": player.nickname,
                    "card1Name": card1Name,
                    "card2Name": card2Name,
                    "roomName": playerRoom,
                },
            },
        )

        player.hasSuspected = True
        player.isSuspecting = True

        game = Game[gameId]

        responseInfo = game.findPlayerIdWithCards(
            cardNames=[card1Name, card2Name, playerRoom], fromPlayerId=playerId
        )

        if responseInfo is None:
            player.isSuspecting = False
            await manager.broadcastToGame(
                gameId,
                {
                    "type": SUSPICION_FAILED_EVENT,
                    "payload": {
                        "Error": "No hay jugadores que posean alguna de las cartas de la sospecha."
                    },
                },
            )

        else:
            await manager.sendToPlayer(
                gameId,
                responseInfo["playerId"],
                {
                    "type": YOU_ARE_SUSPICIOUS_EVENT,
                    "payload": {
                        "playerId": player.id,
                        "playerNickname": player.nickname,
                        "cards": responseInfo["cards"],
                    },
                },
            )

        return {}


@router.post("/{gameId}/replySuspect/{playerId}")
@gameRequired
@playerInGame
async def replySuspect(
    gameId: int, playerId: int, schema: ReplySuspectSchema, response: Response
):

    with db_session:

        game = Game[gameId]
        player = Player[playerId]

        card = Card.get(lambda c: c.game.id == gameId and c.name == schema.cardName)

        if card is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"La carta {schema.cardName} no existe"}

        if card not in player.cards:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "Error": f"El jugador {player.nickname} no tiene la carta {schema.cardName}"
            }

        # We now know that the selected card is valid and the player has it.

        repliedPlayer = Player.get(id=schema.replyToPlayerId)

        if repliedPlayer is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": f"El jugador {schema.replyToPlayerId} no existe"}

        if repliedPlayer.currentGame != game:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                "Error": f"El jugador {schema.replyToPlayerId} no est?? en la partida {gameId}"
            }

        if not repliedPlayer.isSuspecting:
            response.status_code = status.HTTP_403_FORBIDDEN
            return {
                "Error": f"El jugador {schema.replyToPlayerId} no est?? sospechando."
            }

        # We now know the replied player exists, it's on the same game as playerId and they are suspecting.
        repliedPlayer.isSuspecting = False
        response.status_code = status.HTTP_204_NO_CONTENT
        await manager.sendToPlayer(
            gameId,
            schema.replyToPlayerId,
            {
                "type": SUSPICION_RESPONSE_EVENT,
                "payload": {
                    "playerId": player.id,
                    "playerNickname": player.nickname,
                    "cardName": schema.cardName,
                },
            },
        )

        await manager.broadcastToGame(
            gameId,
            {
                "type": PLAYER_REPLIED_EVENT,
                "payload": {"playerId": player.id, "playerNickname": player.nickname},
            },
        )


@router.post("/{gameId}/endTurn/{playerId}")
@isPlayersTurn
async def end_turn(gameId: int, playerId: int, response: Response):
    with db_session:
        game = Game[gameId]
        player = Player[playerId]
        player.hasRolledDice = False
        player.hasMoved = False
        player.hasSuspected = False

        if player.isSuspecting:
            response.status_code == status.HTTP_403_FORBIDDEN
            return {
                "Error": f"El jugador {player.nickname} est?? esperando la respuesta de su sospecha"
            }

        game.incrementTurn()
        currentPlayer = game.players.filter(
            lambda player: player.turnOrder == game.currentTurn
        ).first()
        await manager.broadcastToGame(
            gameId,
            {
                "type": TURN_ENDED_EVENT,
                "payload": {
                    "playerId": currentPlayer.id,
                    "playerNickname": currentPlayer.nickname,
                },
            },
        )
        response.status_code = status.HTTP_204_NO_CONTENT
        return {}


@router.post("/{gameId}/accuse/{playerId}")
@isPlayersTurn
async def accuse(gameId: int, playerId: int, schema: AccuseSchema, response: Response):

    with db_session:

        player = Player[playerId]
        game = Game[gameId]

        victimCardName = schema.victimCardName
        monsterCardName = schema.monsterCardName
        roomCardName = schema.roomCardName

        victimCard = Card.get(
            lambda c: c.game.id == gameId and c.name == victimCardName.value
        )
        monsterCard = Card.get(
            lambda c: c.game.id == gameId and c.name == monsterCardName.value
        )
        roomCard = Card.get(
            lambda c: c.game.id == gameId and c.name == roomCardName.value
        )

        await manager.broadcastToGame(
            gameId,
            {
                "type": PLAYER_ACCUSED_EVENT,
                "payload": {"playerId": player.id, "playerNickname": player.nickname},
            },
        )

        cardsInEnvelope = Card.select(lambda c: c.game.id == gameId and c.isInEnvelope)[
            :
        ]

        response.status_code = status.HTTP_204_NO_CONTENT

        if set([victimCard, monsterCard, roomCard]) != set(cardsInEnvelope):

            await manager.broadcastToGame(
                gameId,
                {
                    "type": PLAYER_LOST_EVENT,
                    "payload": {
                        "playerId": player.id,
                        "playerNickname": player.nickname,
                    },
                },
            )

            player.looseGame()
        else:
            game.finishGame(winnerNickname=player.nickname)

        if game.checkIfFinished():

            winner = game.players.filter(
                lambda p: p.nickname == game.winnerNickname
            ).first()

            await manager.broadcastToGame(
                gameId,
                {
                    "type": GAME_ENDED_EVENT,
                    "payload": {
                        "playerId": winner.id,
                        "playerNickname": game.winnerNickname,
                        "cardsInEnvelope": [
                            c.to_dict(["type", "name"]) for c in cardsInEnvelope
                        ],
                    },
                },
            )
        else:
            game.incrementTurn()
            currentPlayer = game.currentPlayer()
            await manager.broadcastToGame(
                gameId,
                {
                    "type": TURN_ENDED_EVENT,
                    "payload": {
                        "playerId": currentPlayer.id,
                        "playerNickname": currentPlayer.nickname,
                    },
                },
            )

        return {}


@router.websocket("/games/{gameId}/ws/{playerId}")
async def createWebsocketConnection(gameId: int, playerId: int, websocket: WebSocket):
    await websocket.accept()

    try:
        try:
            manager.connectPlayerToGame(gameId, playerId, websocket)
            await GameConnectionManager.keepAlive(websocket)
        except GameConnectionDoesNotExist:
            await websocket.send_json(
                {"Error": f"Conexi??n a la partida {gameId} no existe"}
            )
            await websocket.close(4404)
        except PlayerAlreadyConnected:
            await websocket.send_json(
                {
                    "Error": f"Jugador {playerId} ya tiene una conexi??n activa a la partida {gameId}"
                }
            )
            await websocket.close(4409)
            raise WebSocketDisconnect

    except WebSocketDisconnect:
        manager.disconnectPlayerFromGame(gameId, playerId)
