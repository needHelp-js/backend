import pytest
import os
from fastapi.testclient import TestClient

from config import Config
from app.api import create_app
from pony.orm import db_session 
from app.models import Player, Game

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
        p4 = Player(id=4, nickname='p4', turnOrder=4)
        p5 = Player(id=5, nickname='p5', turnOrder=5)
        g4 = Game(id=4, name='g4', currentTurn=4, host=p4)
