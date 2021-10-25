class GameMixin(object):
    def countPlayers(self):
        l = len(self.players)
        print(l)
        return l

    def incrementTurn(self):
        l = self.countPlayers()
        if self.currentTurn == l:
            self.currentTurn = 1
        else:
            self.currentTurn += 1
