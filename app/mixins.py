from random import randrange
from typing import List

from app import models
from app.enums import (CardType, MonstersNames, RoomsNames,
                       VictimsNames)


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
        self.createGameCards()
        self.setPlayersTurnOrder()
        self.started = True

    def createGameCards(self):
        cards = {"victims": [], "monsters": [], "rooms": []}

        for victimName in VictimsNames:
            cards["victims"].append(
                models.Card(
                    type=CardType.VICTIM.value, name=victimName.value, game=self
                )
            )

        for monsterName in MonstersNames:
            cards["monsters"].append(
                models.Card(
                    type=CardType.MONSTER.value, name=monsterName.value, game=self
                )
            )

        for roomName in RoomsNames:
            cards["rooms"].append(
                models.Card(type=CardType.ROOM.value, name=roomName.value, game=self)
            )

        cards["victims"][randrange(len(cards["victims"]))].isInEnvelope = True
        cards["monsters"][randrange(len(cards["monsters"]))].isInEnvelope = True
        cards["rooms"][randrange(len(cards["rooms"]))].isInEnvelope = True

        return cards

    def findPlayerIdWithCards(self, cardNames: List[str], fromPlayerId: int): 
        
        fromTurnOrder = models.Player[fromPlayerId].turnOrder
        checkingTurn = fromTurnOrder % self.countPlayers()
        players = self.players.sort_by(models.Player.turnOrder)[:]

        while (checkingTurn + 1 != fromTurnOrder):
            checkingPlayer = players[checkingTurn]

            playerCards = checkingPlayer.filterCards(cardNames)
            if len(playerCards) > 0:
                return {"playerId": checkingPlayer.id, "cards": [c.name for c in playerCards]}

            checkingTurn = (checkingTurn + 1) % self.countPlayers()

        return None

class PlayerMixin():

    def filterCards(self, cardNames: List[str]):
        return self.cards.filter(lambda card: card.name in cardNames)
