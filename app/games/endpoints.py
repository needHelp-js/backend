from typing import List
from fastapi import APIRouter, Response
from app.games.schemas import AvailableGameSchema
from app.models import *

router = APIRouter(prefix="/games")


@router.get("/", response_model=List[AvailableGameSchema])
async def getGames():
    with db_session:
        games = Game.select(lambda p: len(p.players) < 6 and p.started == False)[:]

        gamesList = []

        for game in games:
            gameDict = game.to_dict(["id", "name"])
            gameDict.update(playerCount=len(game.players))

            gamesList.append(gameDict)

        return gamesList
