from fastapi import responses, APIRouter, Response, status
from app.models import *
from random import randint

router = APIRouter(prefix='/games')

@router.patch("/{idG}/begin/{idP}")
async def beginGame(idG:int, idP: int, response:Response):
    with db_session:
        game = Game.get(id=idG)
        player = Player.get(id=idP)
        if (game is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Partida no existente'}
        elif(player is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Jugador no existente'}
        elif (game.host.id == player.id):
            if (game.started == False):
                game.started = True
                response.status_code = status.HTTP_200_OK
                return 1
            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                return {'Error' : 'La partida ya empezó'} 
        else: 
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Error' : 'El jugador no es el host'}