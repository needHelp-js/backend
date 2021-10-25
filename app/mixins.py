class GameMixin(object):
    def countPlayers(self):
        l = len(self.players)
        return l

    def incrementTurn(self):
        l = self.countPlayers()
        if self.currentTurn == l:
            self.currentTurn = 1
        else:
            self.currentTurn += 1

    def setPlayersTurnOrder(self):
        turnToAssign = 1
        for player in self.players:
            player.turnOrder = turnToAssign
            turnToAssign += 1
