from typing import List
from app.enums import CardType, MonstersNames, RoomName, VictimsNames
from app import models
from random import randrange


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

        for roomName in RoomName:
            cards["rooms"].append(
                models.Card(type=CardType.ROOM.value, name=roomName.value, game=self)
            )

        cards["victims"][randrange(len(cards["victims"]))].isInEnvelope = True
        cards["monsters"][randrange(len(cards["monsters"]))].isInEnvelope = True
        cards["rooms"][randrange(len(cards["rooms"]))].isInEnvelope = True

        return cards

    def findPlayerIdWithCards(self, cardNames: List[str]): 
        
        for player in self.players:
            playerCards = player.filterCards(cardNames)
            if len(playerCards) > 0:
                return {"playerId": player.id, "cards": [c.name for c in playerCards]}

        return None

class PlayerMixin():

    def filterCards(self, cardNames: List[str]):
        return self.cards.filter(lambda card: card.name in cardNames)