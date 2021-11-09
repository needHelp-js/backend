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

        for roomName in RoomName:
            cards["rooms"].append(
                models.Card(type=CardType.ROOM.value, name=roomName.value, game=self)
            )

        cards["victims"][randrange(len(cards["victims"]))].isInEnvelope = True
        cards["monsters"][randrange(len(cards["monsters"]))].isInEnvelope = True
        cards["rooms"][randrange(len(cards["rooms"]))].isInEnvelope = True

        return cards
