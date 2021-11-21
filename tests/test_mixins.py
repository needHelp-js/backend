from app.enums import MonstersNames, RoomsNames, VictimsNames
from app.models import Card, Game, Player
from pony.orm import db_session


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


def test_incrementTurn_success(app, dataTirarDado):
    with db_session:
        g1 = Game[1]
        g1.incrementTurn()
        assert g1.currentTurn == 2

def test_incrementTurn_onePlayerLost(app, dataSuspect):
    # We'll use game 1 with players 1,2,3 and 4. CurrentTurn = 1
    with db_session:
        g1 = Game[1]
        p2 = Player[2]
        assert g1.currentTurn == 1

        p2.looseGame()

        g1.incrementTurn()
        assert g1.currentTurn == 3

def test_incrementTurn_twoPlayersLost(app, dataSuspect):
    # We'll use game 1 with players 1,2,3 and 4. CurrentTurn = 1
    with db_session:
        g1 = Game[1]
        p3 = Player[3]
        p4 = Player[4]
        assert g1.currentTurn == 1

        p3.looseGame()
        p4.looseGame()

        g1.incrementTurn()
        g1.incrementTurn()
        assert g1.currentTurn == 1

def test_currentPlayer_success(client, dataCards):
    with db_session:
        game = Game[1]
        player = Player[1]

        cPlayer = game.currentPlayer()

        assert cPlayer == player


def test_currentPlayer_noPlayersInGame(client, dataGameNoPlayers):
    with db_session:
        game = Game[1]

        cPlayer = game.currentPlayer()

        assert cPlayer is None


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
        finalCards = p1.filterCards([MonstersNames.HOMBRE_LOBO.value, "Gato", "Perro"])[
            :
        ]

        assert finalCards == []


def test_filterCards_success(app, dataSuspect):

    with db_session:
        p2 = Player[2]
        finalCards = p2.filterCards([VictimsNames.CONDESA.value, "Gato", "Perro"])[:]

        assert [c.name for c in finalCards] == [VictimsNames.CONDESA.value]


def test_filterCards_multipleSuccess(app, dataSuspect):

    with db_session:
        p2 = Player[2]
        finalCards = p2.filterCards(
            [VictimsNames.CONDESA.value, MonstersNames.DRACULA.value, "Perro"]
        )[:]

        assert [c.name for c in finalCards] == [
            VictimsNames.CONDESA.value,
            MonstersNames.DRACULA.value,
        ]


def test_findPlayerIdWithCards_success(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(
            [
                VictimsNames.CONDESA.value,
                MonstersNames.DRACULA.value,
                RoomsNames.PANTEON.value,
            ],
            fromPlayerId=1,
        )

        assert response["playerId"] == 2
        assert response["cards"] == [
            VictimsNames.CONDESA.value,
            MonstersNames.DRACULA.value,
        ]


def test_findPlayerIdWithCards_successSecondPlayer(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(
            [
                VictimsNames.CONDE.value,
                MonstersNames.MOMIA.value,
                RoomsNames.PANTEON.value,
            ],
            fromPlayerId=1,
        )

        assert response["playerId"] == 3
        assert response["cards"] == [VictimsNames.CONDE.value]


def test_findPlayerIdWithCards_noCards(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(["Gato", "Perro", "Hola"], fromPlayerId=1)

        assert response is None


def test_findPlayerIdWithCards_imLastPlayer(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(
            [
                RoomsNames.PANTEON.value,
                VictimsNames.CONDESA.value,
                VictimsNames.DONCELLA.value,
            ],
            fromPlayerId=4,
        )

        assert response["playerId"] == 1
        assert response["cards"] == [VictimsNames.DONCELLA.value]


def test_findPlayerIdWithCards_fromFirstPlayer(app, dataSuspect):

    with db_session:
        g1 = Game[1]

        response = g1.findPlayerIdWithCards(
            [
                RoomsNames.PANTEON.value,
                VictimsNames.CONDESA.value,
                VictimsNames.DONCELLA.value,
            ],
            fromPlayerId=1,
        )

        assert response["playerId"] == 2
        assert response["cards"] == [VictimsNames.CONDESA.value]


def test_finishGame_success(app, dataGameNoPlayers):
    with db_session:
        game = Game[1]

        assert not game.ended
        assert game.winnerNickname == ""

        game.finishGame(winnerNickname="Nickname")

        assert game.ended
        assert game.winnerNickname == "Nickname"


def test_checkIfFinished_gameNotEnded(app, data):
    with db_session:
        game = Game[1]
        assert not game.ended
        assert not game.checkIfFinished()


def test_checkIfFinished_gameAlreadyEnded(app, data):
    with db_session:
        game = Game[1]
        game.ended = True
        assert game.ended
        assert game.checkIfFinished()


def test_checkIfFinished_gameWithOnePlayerActive(app, dataTirarDado):
    with db_session:
        game = Game[1]
        player = Player[1]
        assert not game.ended
        player.looseGame()
        assert game.checkIfFinished()


def test_looseGame(app, dataTirarDado):
    with db_session:
        player = Player[1]
        player.room = 2
        player.position = 24
        assert not player.hasLost
        player.looseGame()
        assert player.hasLost
        assert player.room == None
        assert player.position == None
