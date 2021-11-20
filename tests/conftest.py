import os

import pytest
from app.api import create_app
from app.enums import CardType, MonstersNames, RoomsNames, VictimsNames
from app.games.connections import GameConnectionManager
from app.models import Card, Game, Player
from config import Config
from fastapi.testclient import TestClient
from pony.orm import commit, db_session, flush

basedir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def app():
    class TestConfig(Config):
        dbBind = {
            "provider": "sqlite",
            "filename": basedir + "/test_db.sqlite",
            "create_db": True,
        }

    testConfig = TestConfig()

    app, db = create_app(testConfig)

    yield app

    db.schema = None
    db.provider = None
    os.remove(testConfig.dbBind["filename"])


@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def dataPasswordGame():
    with db_session:
        p1 = Player(id=1, nickname="p1")
        g1 = Game(id=1, name="g1", host=p1, password="1234")
        p2 = Player(id=2, nickname="p2")
        g2 = Game(id=2, name="g2", host=p2)
        flush()

        g1.players.add(p1)
        g2.players.add(p2)

@pytest.fixture
def dataListGames():
    with db_session:
        players = []
        for i in range(21):
            players.append(Player(id=i, nickname=f"p{i}"))

        # Only one player
        g1 = Game(id=1, name="g1", host=players[0])
        # Six players
        g2 = Game(id=2, name="g2", host=players[1])
        # Four players, and started
        g3 = Game(id=3, name="g3", host=players[7], started=True)
        # Six players and started
        g4 = Game(id=4, name="g4", host=players[11], started=True)
        # Four players, not started
        g5 = Game(id=5, name="g5", host=players[17])

        flush()

        g1.players.add(players[0])  # 1
        g2.players.add(players[1:7])  # 6
        g3.players.add(players[7:11])  # 4
        g4.players.add(players[11:17])  # 6
        g5.players.add(players[17:21])  # 4


@pytest.fixture
def dataGameNoPlayers():
    with db_session:
        p1 = Player(nickname="p1")
        g1 = Game(name="g1", host=p1)


@pytest.fixture
def dataTirarDado():
    with db_session:
        p1 = Player(id=1, nickname="p1", turnOrder=1)
        p2 = Player(id=2, nickname="p2", turnOrder=2)
        g1 = Game(id=1, name="g1", currentTurn=1, host=p1)
        flush()
        g1.players = [p1, p2]


@pytest.fixture
def data():
    with db_session:
        players = []
        for i in range(6):
            players.append(Player(id=i, nickname=f"p{i}"))

        g1 = Game(id=1, name="g1", host=players[0])

        flush()

        g1.players.add(players)  # 6


@pytest.fixture
def gameManager():
    return GameConnectionManager()


@pytest.fixture
def beginGameData():
    with db_session:
        p1 = Player(id=1, nickname="p1", turnOrder=1)
        p2 = Player(id=2, nickname="p2", turnOrder=2)
        g1 = Game(id=1, name="g1", currentTurn=0, host=p1)
        p3 = Player(id=3, nickname="p3", turnOrder=1)
        p4 = Player(id=4, nickname="p4", turnOrder=2)
        g2 = Game(id=2, name="g2", started=True, currentTurn=2, host=p3)
        p5 = Player(id=5, nickname="p5", turnOrder=1)
        g3 = Game(id=3, name="g3", currentTurn=0, host=p5)

        flush()

        g1.players.add([p1, p2])
        g2.players.add([p3, p4])
        g3.players.add(p5)


@pytest.fixture
def boardData():
    with db_session:
        p1 = Player(id=1, nickname="p1", room=1)
        p2 = Player(id=2, nickname="p2", position=6)


@pytest.fixture
def dataBoard():
    with db_session:
        p1 = Player(id=1, nickname="p1", turnOrder=1, position=6)
        g1 = Game(id=1, name="g1", currentTurn=1, host=p1)

        flush()
        g1.players.add(p1)


@pytest.fixture
def dataCards():
    with db_session:
        p1 = Player(id=1, nickname="p1", turnOrder=1)
        p2 = Player(id=2, nickname="p2", turnOrder=2)
        g1 = Game(id=1, name="g1", host=p1, currentTurn=1)

        c1 = Card(id=1, type="victima", name="Conde", game=g1)
        c2 = Card(id=2, type="victima", name="Condesa", game=g1)
        c3 = Card(id=3, type="monstruo", name="Drácula", game=g1)
        c4 = Card(id=4, type="monstruo", name="Hombre Lobo", game=g1)
        c5 = Card(id=5, type="recinto", name="Cochera", game=g1)
        c6 = Card(id=6, type="recinto", name="Panteon", game=g1)

        flush()

        g1.players.add([p1, p2])


@pytest.fixture
def dataSuspect():
    with db_session:
        p1 = Player(id=1, nickname="p1", turnOrder=1)
        p2 = Player(id=2, nickname="p2", turnOrder=2)
        p3 = Player(id=3, nickname="p3", turnOrder=3)
        p4 = Player(id=4, nickname="p4", turnOrder=4)
        g1 = Game(id=1, name="g1", host=p1, currentTurn=1)

        flush()

        g1.players.add([p1, p2, p3, p4])

        c1 = Card(
            id=1, type=CardType.VICTIM.value, name=VictimsNames.CONDE.value, game=g1
        )
        c2 = Card(
            id=2, type=CardType.VICTIM.value, name=VictimsNames.CONDESA.value, game=g1
        )
        c3 = Card(
            id=3, type=CardType.MONSTER.value, name=MonstersNames.DRACULA.value, game=g1
        )
        c4 = Card(
            id=4,
            type=CardType.MONSTER.value,
            name=MonstersNames.HOMBRE_LOBO.value,
            game=g1,
        )
        c5 = Card(
            id=5, type=CardType.ROOM.value, name=RoomsNames.COCHERA.value, game=g1
        )
        c6 = Card(
            id=6, type=CardType.ROOM.value, name=RoomsNames.PANTEON.value, game=g1
        )

        c7 = Card(
            id=7, type=CardType.VICTIM.value, name=VictimsNames.MAYORDOMO.value, game=g1
        )
        c8 = Card(
            id=8, type=CardType.VICTIM.value, name=VictimsNames.DONCELLA.value, game=g1
        )

        p1.cards.add(c8)
        p2.cards.add([c2, c3, c5])
        p3.cards.add(c1)
        p4.cards.add(c6)

        p1.room = 8  # COCHERA
