from fastapi import responses, APIRouter, Response, status
from app.models import *
from random import randint

router = APIRouter(prefix='/games')

@router.patch("/{idG}/begin/{idP}")
async def beginGame(idG:int, idP: int, response:Response):
    with db_session:
        g = Game.get(id=idG)
        p = Player.get(id=idP)
        if (p is None or g is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Jugador o partida no existentes'}
        elif (g.host.id == p.id):
            g.started = True
            response.status_code = status.HTTP_204_NO_CONTENT
        else: 
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Error' : 'El jugador no es el host'}