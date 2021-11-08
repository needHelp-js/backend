from typing import List


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

    def startGame(self):
        self.currentTurn = 1
        self.setPlayersTurnOrder()
        self.started = True

    #TODO: ENCONTRAR MEJOR NOMBRE
    def findPlayerIdWithCards(self, cardNames: List[str]): 
        
        for player in self.players:
            playerCards = player.filterCards(cardNames)
            if len(playerCards) > 0:
                return {"playerId": player.id, "cards": [c.name for c in playerCards]}

        return None

class PlayerMixin():

    def filterCards(self, cardNames: List[str]):
        return self.cards.filter(lambda card: card.name in cardNames)