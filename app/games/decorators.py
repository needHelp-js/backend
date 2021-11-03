from fastapi import responses, status
from starlette.responses import Response
from app.models import Game
from pony.orm import db_session
import functools

def gameRequired(f):


        @functools.wraps(f)
        async def fWrapper(*args, **kargs):

            with db_session:

                game = Game.get(id=kargs['gameId'])

                if game is None:
                    kargs['response'].status_code = status.HTTP_404_NOT_FOUND
                    return {"Error": f"Partida {kargs['gameId']} no existe."}
                
                return await f(*args, **kargs)

        return fWrapper