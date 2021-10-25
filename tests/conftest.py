import pytest
import os
from fastapi.testclient import TestClient
from app.games.connections import GameConnectionManager

from config import Config
from app.api import create_app
from pony.orm import db_session, flush
from app.models import Player, Game

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
def data():
    with db_session:
        p1 = Player(id=1, nickname="p1", turnOrder=1)
        p2 = Player(id=2, nickname="p2", turnOrder=2)
        g1 = Game(id=1, name="g1", currentTurn=1, host=p1)
        flush()
        g1.players = [p1, p2]


@pytest.fixture
def gameManager():
    return GameConnectionManager()
