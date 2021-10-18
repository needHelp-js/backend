from fastapi import responses, APIRouter, Response, status
from app.models import *
from random import randint

router = APIRouter(prefix='/games')

@router.get("/{idG}/dice/{idP}")
async def getDice(idG:int, idP:int, response:Response):
    with db_session:
        g = Game.get(id=idG)
        p = Player.get(id=idP)
        if (p is None or g is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Jugador o partida no existentes'}
        elif (g.currentTurn == p.turnOrder):
            return randint(1,6)
        else: 
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Error' : 'No es el turno del jugador'}
