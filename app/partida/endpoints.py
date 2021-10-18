from fastapi import responses, APIRouter, Response, status
from app.models import *
from random import randint

router = APIRouter(prefix='/games')

@router.get("/dice")
async def get_dado(idP:int, idJ:int, response:Response):
    with db_session:
        p = Game.get(id=idP)
        j = Player.get(id=idJ)
        if (p is None or j is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Jugador o partida no existentes'}
        elif (p.currentTurn == j.turnOrder):
            return randint(1,6)
        else: 
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Error' : 'No es el turno del jugador'}