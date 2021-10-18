from fastapi import APIRouter, status, Response
from app.models import Game, Player
from .schemas import CreateGameSchema
from pony.orm import db_session

router = APIRouter(prefix='/games')

@router.post('', status_code=status.HTTP_201_CREATED)
def createGame(gameCreationData: CreateGameSchema, response: Response):
    with db_session:
        if Game.exists(name=gameCreationData.gameName):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'Error': f'Partida {gameCreationData.gameName} ya existe'}

        hostPlayer = Player(nickname=gameCreationData.hostNickname, turnOrder=0)
        newGame = Game(name=gameCreationData.gameName, host=hostPlayer)
        hostPlayer.hostedGame=newGame
    
    return {'partida': gameCreationData}