from pony.orm.core import db_session, flush
import pytest
import os
from fastapi.testclient import TestClient
from app.models import Game, Player

from config import Config

from app.api import create_app

basedir = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture
def app():
    class TestConfig(Config):
        dbBind = {
            'provider': 'sqlite',
            'filename': basedir + '/test_db.sqlite',
            'create_db': True,
        }
    testConfig = TestConfig()

    app, db = create_app(testConfig)

    yield app

    db.schema = None
    db.provider = None
    os.remove(testConfig.dbBind['filename'])

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def data():
    with db_session:
        players = []
        for i in range(21):
            players.append(Player(id=i, nickname=f'p{i}'))
        
        # Only one player
        g1 = Game(id=1, name='g1', host=players[0])
        # Six players
        g2 = Game(id=2, name='g2', host=players[1])
        # Four players, and started
        g3 = Game(id=3, name='g3', host=players[7], started=True)
        # Six players and started
        g4 = Game(id=4, name='g4', host=players[11], started=True)
        # Four players, not started
        g5 = Game(id=5, name='g5', host=players[17])
        
        flush()

        g1.players.add(players[0])     # 1
        g2.players.add(players[1:7])   # 6
        g3.players.add(players[7:11])  # 4
        g4.players.add(players[11:17]) # 6
        g5.players.add(players[17:21]) # 4