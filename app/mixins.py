from random import randrange
from sys import set_asyncgen_hooks
from typing import List

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

        if self.currentPlayer().hasLost:
            self.incrementTurn()

        if self.currentPlayer().isInTrap:
            self.currentPlayer().isInTrap = False
            self.incrementTurn()

    def currentPlayer(self):
        return self.players.filter(
            lambda player: player.turnOrder == self.currentTurn
        ).first()

    def setPlayersTurnOrder(self):
        turnToAssign = 1
        for player in self.players:
            player.turnOrder = turnToAssign
            turnToAssign += 1

        aux = 0
        for player in self.players:
            if player.hostedGame != None:
                aux = player.turnOrder 
                player.turnOrder = 1
        
        for player in self.players:
            if player.turnOrder == 1 and player.hostedGame == None:
                player.turnOrder = aux

    def setPlayersInitialPositions(self):
        initialPositions = [6, 13, 120, 139, 260, 279, 386, 393]
        i = 0
        for player in self.players:
            player.position = initialPositions[i]
            i += 1

    def startGame(self):
        self.setPlayersTurnOrder()
        self.setPlayersInitialPositions()
        self.currentTurn = 1
        cards = self.createGameCards()
        self.assignCardsToPlayers(cards)
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
        del cards["victims"][i]

        i = randrange(len(cards["monsters"]))
        cards["monsters"][i].isInEnvelope = True
        del cards["monsters"][i]

        i = randrange(len(cards["rooms"]))
        cards["rooms"][i].isInEnvelope = True
        del cards["rooms"][i]

        return cards

    def findPlayerIdWithCards(self, cardNames: List[str], fromPlayerId: int):

        fromTurnOrder = models.Player[fromPlayerId].turnOrder
        checkingTurn = fromTurnOrder % self.countPlayers()
        players = self.players.sort_by(models.Player.turnOrder)[:]

        while checkingTurn + 1 != fromTurnOrder:
            checkingPlayer = players[checkingTurn]

            playerCards = checkingPlayer.filterCards(cardNames)
            if len(playerCards) > 0:
                return {
                    "playerId": checkingPlayer.id,
                    "cards": [c.name for c in playerCards],
                }

            checkingTurn = (checkingTurn + 1) % self.countPlayers()

        return None

    def assignCardsToPlayers(self, cards):

        card_set = set(cards["victims"])
        card_set.update(cards["monsters"])
        card_set.update(cards["rooms"])

        players = list(self.players)

        i = 0
        while len(card_set) > 0:
            players[i % len(players)].cards.add(card_set.pop())
            i += 1

    def finishGame(self, winnerNickname: str):
        self.ended = True
        self.winnerNickname = winnerNickname

    def checkIfFinished(self):
        playersPlaying = self.players.filter(lambda p: not p.hasLost)[:]

        if len(playersPlaying) <= 1:
            self.finishGame(winnerNickname=playersPlaying[0].nickname)

        return self.ended


class PlayerMixin:
    def filterCards(self, cardNames: List[str]):
        return self.cards.filter(lambda card: card.name in cardNames)

    def looseGame(self):
        self.hasLost = True
        self.position = None
        self.room = None
