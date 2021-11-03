from pydantic import BaseModel
from typing import List

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
    position: List = [-1, -1]
    room: int = -1

