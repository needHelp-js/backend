from pydantic import BaseModel
from typing import Tuple


class AvailableGameSchema(BaseModel):
    id: int
    name: str
    playerCount: int


class CreateGameSchema(BaseModel):
    gameName: str
    hostNickname: str


class joinGameSchema(BaseModel):
    playerNickname: str


class MovePlayerSchema(BaseModel):
    diceNumber: int
    position: Tuple = (-1, -1)
    room: str = ""
class SuspectSchema(BaseModel):
    card1Name: str
    card2Name: str
