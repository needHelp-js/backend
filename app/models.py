from pony.orm import *
from app.mixins import GameMixin

db = Database()


class Game(db.Entity, GameMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    started = Required(bool, default=False)
    currentTurn = Optional(int, default=0)
    players = Set("Player", reverse="currentGame")
    host = Required("Player", reverse="hostedGame")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    nickname = Required(str)
    turnOrder = Optional(int)
    currentGame = Optional(Game, reverse="players")
    hostedGame = Optional(Game, reverse="host")
