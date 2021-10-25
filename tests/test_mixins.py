from pony.orm import db_session
from app.models import Game


def test_countPlayers(app, data):
    with db_session:
        g1 = Game[1]
        l = g1.countPlayers()
        assert l == 2


def test_incrementTurn(app, data):
    with db_session:
        g1 = Game[1]
        g1.incrementTurn()
        assert g1.currentTurn == 2
