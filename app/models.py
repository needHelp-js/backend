from pony.orm import *
from app.mixins import GameMixin
from app.enums import CardType, VictimsNames, MonstersNames, RoomName


db = Database()


class Game(db.Entity, GameMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    started = Required(bool, default=False)
    currentTurn = Optional(int, default=0)
    players = Set("Player", reverse="currentGame")
    host = Required("Player", reverse="hostedGame")
    cards = Set("Card")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    nickname = Required(str)
    turnOrder = Optional(int)
    currentGame = Optional(Game, reverse="players")
    hostedGame = Optional(Game, reverse="host")
    cards = Set("Card")


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
    for elem in RoomName:
        if elem.value == val:
            return True
    return False


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    type = Required(str, py_check=checkCardType)
    name = Required(str, py_check=checkCardName)
    game = Optional(Game)
    isInEnvelope = Optional(bool)
    player = Optional(Player)


db.bind(
    "sqlite", "db.sqlite", create_db=True
)  # Conectamos el objeto `db` con la base de dato.
db.generate_mapping(create_tables=True)  # Generamos las base de datos.
