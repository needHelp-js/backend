from random import randrange

from app import models
from app.enums import CardType, MonstersNames, RoomsNames, VictimsNames


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
        cards = self.createGameCards()
        self.assignCardsToPlayers(cards)
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

        i = randrange(len(cards["victims"]))
        cards["victims"][i].isInEnvelope = True
        del cards["victims"][i];

        i = randrange(len(cards["monsters"]))
        cards["monsters"][i].isInEnvelope = True
        del cards["monsters"][i];

        i = randrange(len(cards["rooms"]))
        cards["rooms"][i].isInEnvelope = True
        del cards["rooms"][i];

        return cards

    def assignCardsToPlayers(self, cards):

        card_set = set(cards["victims"])
        card_set.update(cards["monsters"])
        card_set.update(cards["rooms"])

        players = list(self.players)

        i = 0
        while len(card_set) > 0:
            players[i % len(players)].cards.add(card_set.pop())
            i += 1
