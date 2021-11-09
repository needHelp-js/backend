from pony.orm import db_session
from app.models import Card, Game, Player


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

def test_filterCards_noCardsMatching(app, dataSuspect):

    with db_session:
        p1 = Player[1]
        finalCards = p1.filterCards(["Hombre Lobo", "Gato", "Perro"])[:]

        assert finalCards == []

def test_filterCards_success(app, dataSuspect):

    with db_session:
        p2 = Player[2]
        finalCards = p2.filterCards(["Condesa", "Gato", "Perro"])[:]

        assert [c.name for c in finalCards] == ["Condesa"]

def test_filterCards_multipleSuccess(app, dataSuspect):

    with db_session:
        p2 = Player[2]
        finalCards = p2.filterCards(["Condesa", "Drácula", "Perro"])[:]

        assert [c.name for c in finalCards] == ["Condesa", "Drácula"]

def test_findPlayerIdWithCards_success(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(["Condesa", "Drácula", "Panteón"], fromPlayerId=1)

        assert response["playerId"] == 2
        assert response["cards"] == ["Condesa", "Drácula"]

def test_findPlayerIdWithCards_successSecondPlayer(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(["Conde", "Momia", "Panteón"], fromPlayerId=1)

        assert response["playerId"] == 3
        assert response["cards"] == ["Conde"]


def test_findPlayerIdWithCards_noCards(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(["Gato", "Perro", "Hola"], fromPlayerId=1)

        assert response is None

def test_findPlayerIdWithCards_imLastPlayer(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(["Panteón", "Condesa", "Doncella"], fromPlayerId=4)

        assert response["playerId"] == 1
        assert response["cards"] == ["Doncella"]

def test_findPlayerIdWithCards_fromFirstPlayer(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(["Panteón", "Condesa", "Doncella"], fromPlayerId=1)

        assert response["playerId"] == 2
        assert response["cards"] == ["Condesa"]