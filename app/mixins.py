from pony.orm.core import commit, db_session


class GameMixin(object):
    def setPlayersTurnOrder(self):
        currentTurn = 1
        for player in self.players:
            player.turnOrder = currentTurn
            currentTurn += 1
