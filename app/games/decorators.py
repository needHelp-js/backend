import functools

from app.models import Game, Player
from fastapi import responses, status
from pony.orm import db_session
from starlette.responses import Response


def gameRequired(f):
    """
    Decorator that checks if a game exists given a gameId.
    """

    @functools.wraps(f)
    async def fWrapper(*args, **kargs):

        with db_session:

            gameExists = Game.exists(id=kargs["gameId"])

            if not gameExists:
                kargs["response"].status_code = status.HTTP_404_NOT_FOUND
                return {"Error": f"Partida {kargs['gameId']} no existe."}

            return await f(*args, **kargs)

    return fWrapper


def playerInGame(f):
    """
    Decorator that checks if a player exists given a playerId.
    If it exists, checks if they are inside a game given a gameId.
    """

    @functools.wraps(f)
    async def fWrapper(*args, **kargs):

        with db_session:

            player = Player.get(id=kargs["playerId"])
            game = Game.get(id=kargs['gameId'])

            if player is None:
                kargs["response"].status_code = status.HTTP_404_NOT_FOUND
                return {"Error": f"El jugador {kargs['playerId']} no existe."}

            if player.currentGame is None or player.currentGame.id != kargs["gameId"]:
                kargs["response"].status_code = status.HTTP_403_FORBIDDEN
                return {
                    "Error": f"El jugador {player.nickname} no esta en la partida {game.name}."
                }

            return await f(*args, **kargs)

    return fWrapper


def isPlayersTurn(f):
    """
    Decorator that checks if it's the player's turn.
    This decorator already calls @gameRequired and @playerInGame.
    """

    @functools.wraps(f)
    @gameRequired
    @playerInGame
    async def fWrapper(*args, **kargs):

        with db_session:

            player = Player[kargs["playerId"]]

            if player.turnOrder != player.currentGame.currentTurn:
                kargs["response"].status_code = status.HTTP_403_FORBIDDEN
                return {"Error": f"No es el turno del jugador {player.nickname}"}

            return await f(*args, **kargs)

    return fWrapper
