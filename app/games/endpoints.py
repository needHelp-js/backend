from fastapi import responses, APIRouter, Response, status
from app.models import *
from random import randint

router = APIRouter(prefix='/games')

@router.get("/{idG}/dice/{idP}")
async def getDice(idG:int, idP:int, response:Response):
    with db_session:
        game = Game.get(id=idG)
        player = Player.get(id=idP)
        if (game is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Partida no existente'}
        elif (player is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Jugador no existente'}
        elif (game.currentTurn == player.turnOrder):
            return randint(1,6)
        else: 
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Error' : 'No es el turno del jugador'}
