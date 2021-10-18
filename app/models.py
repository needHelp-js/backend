from pony.orm import *

db = Database()

class Partida(db.Entity):
    id = PrimaryKey(int, auto=True)
    nombre = Required(str, unique=True)
    iniciada = Required(bool, default=False)
    turno = Optional(int, default=0)
    jugadores = Set('Jugador', reverse='partidaEnCurso')
    host = Required('Jugador', reverse='partidaHost')

class Jugador(db.Entity):
    id = PrimaryKey(int, auto=True)
    nickname = Required(str)
    orden = Optional(int)
    partidaEnCurso = Optional(Partida, reverse='jugadores')
    partidaHost = Optional(Partida, reverse='host')

