from pony.orm import *

from app.enums import CardType, MonstersNames, RoomsNames, VictimsNames
from app.mixins import GameMixin, PlayerMixin

db = Database()


class Game(db.Entity, GameMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    started = Required(bool, default=False)
    currentTurn = Optional(int, default=0)
    players = Set("Player", reverse="currentGame")
    host = Required("Player", reverse="hostedGame")
    cards = Set("Card")
    ended = Required(bool, default=False)
    winnerNickname = Optional(str)


class Player(db.Entity, PlayerMixin):
    id = PrimaryKey(int, auto=True)
    nickname = Required(str)
    turnOrder = Optional(int)
    currentGame = Optional(Game, reverse="players")
    hostedGame = Optional(Game, reverse="host")
    position = Optional(int)
    room = Optional(int)
    isSuspecting = Required(bool, default=False)
    cards = Set("Card")
    hasLost = Required(bool, default=False)


def checkCardType(val):
    for elem in CardType:
        if elem.value == val:
            return True
    return False


def checkCardName(val):
    for elem in VictimsNames:
        if elem.value == val:
            return True
    for elem in MonstersNames:
        if elem.value == val:
            return True
    for elem in RoomsNames:
        if elem.value == val:
            return True
    return False


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str, py_check=checkCardType)
    name = Required(str, py_check=checkCardName)
    game = Required(Game)
    isInEnvelope = Required(bool, default=False)
    player = Optional(Player)
