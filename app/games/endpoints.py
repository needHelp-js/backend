from fastapi import responses, APIRouter, Response, status
from app.models import *
from random import randint

router = APIRouter(prefix='/games')

@router.patch("/{idG}/begin/{idP}")
async def beginGame(idG:int, idP: int, response:Response):
    with db_session:
        game = Game.get(id=idG)
        player = Player.get(id=idP)
        if (player is None or game is None):
            response.status_code = status.HTTP_404_NOT_FOUND
            return {'Error' : 'Jugador o partida no existentes'}
        elif (game.host.id == player.id):
            if (game.started == False):
                game.started = True
                response.status_code = status.HTTP_200_OK
                return 1
            else:
                response.status_code = status.HTTP_403_FORBIDDEN
                game.started = False
                return {'Error' : 'La partida ya empezó'} 
        else: 
            response.status_code = status.HTTP_403_FORBIDDEN
            return {'Error' : 'El jugador no es el host'}