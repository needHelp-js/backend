from typing import Tuple

from app.enums import MonstersNames, RoomsNames, VictimsNames
from pydantic import BaseModel


class AvailableGameSchema(BaseModel):
    id: int
    name: str
    hasPassword: bool
    playerCount: int


class CreateGameSchema(BaseModel):
    gameName: str
    hostNickname: str
    password: str = ""


class joinGameSchema(BaseModel):
    playerNickname: str
    password: str = ""


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
