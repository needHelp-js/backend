from pony.orm import db_session
from app.mixins import GameMixin
from app.models import Game


def test_startGame(app, beginGameData):
    with db_session:
        g1 = Game[1]
        g1.startGame()
        assert g1.currentTurn == 1
        assert g1.started == True


def test_countPlayers(app, dataTirarDado):
    with db_session:
        g1 = Game[1]
        l = g1.countPlayers()
        assert l == 2


def test_incrementTurn(app, dataTirarDado):
    with db_session:
        g1 = Game[1]
        g1.incrementTurn()
        assert g1.currentTurn == 2


def test_setPlayerTurnOrder_success(app, data):
    with db_session:
        g1 = Game[1]

        g1.setPlayersTurnOrder()

        playerTurns = [p.turnOrder for p in g1.players]

    assert 1 in playerTurns
    assert 2 in playerTurns
    assert 3 in playerTurns
    assert 4 in playerTurns
    assert 5 in playerTurns
    assert 6 in playerTurns

    assert len(playerTurns) == len(set(playerTurns))
