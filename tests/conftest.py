import pytest
import os
from fastapi.testclient import TestClient
from app.games.connections import GameConnectionManager

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
def gameManager():
    return GameConnectionManager()