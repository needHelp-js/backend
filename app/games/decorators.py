import functools

from app.models import Game
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

            game = Game.get(id=kargs["gameId"])

            if game is None:
                kargs["response"].status_code = status.HTTP_404_NOT_FOUND
                return {"Error": f"Partida {kargs['gameId']} no existe."}

            return await f(*args, **kargs)

    return fWrapper


def playerInGame(f):
    """
    Decorator that checks if a player is inside a game given a playerId and a gameId.
    """

    @functools.wraps(f)
    async def fWrapper(*args, **kargs):
        with db_session:

            game = Game.get(id=kargs["gameId"])

            players = game.players.filter(lambda player: player.id == kargs["playerId"])

            if len(players) == 0:
                kargs["response"].status_code = status.HTTP_403_FORBIDDEN
                return {
                    "Error": f"El jugador {kargs['playerId']} no esta en la partida {kargs['gameId']}."
                }

            return await f(*args, **kargs)

    return fWrapper
