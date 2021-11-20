from typing import Tuple

from pydantic import BaseModel

from app.enums import MonstersNames, RoomsNames, VictimsNames


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


class ReplySuspectSchema(BaseModel):
    replyToPlayerId: int
    cardName: str

class AccuseSchema(BaseModel):
    victimCardName: VictimsNames
    monsterCardName: MonstersNames
    roomCardName: RoomsNames 