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

    def setPlayersInitialPositions(self):
        initialPositions = [6, 13, 120, 139, 260, 279, 386, 393]
        i = 0
        for player in self.players:
            player.position = initialPositions[i]
            i += 1

    def startGame(self):
        self.setPlayersInitialPositions()
        self.currentTurn = 1
        self.setPlayersTurnOrder()
        self.started = True
