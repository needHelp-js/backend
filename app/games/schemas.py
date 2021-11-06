from pydantic import BaseModel


class AvailableGameSchema(BaseModel):
    id: int
    name: str
    playerCount: int


class CreateGameSchema(BaseModel):
    gameName: str
    hostNickname: str


class joinGameSchema(BaseModel):
    playerNickname: str


class SospecharSchema(BaseModel):
    card1Name: str
    card2Name: str
