from typing import Any, Dict
from fastapi import WebSocket
from .exceptions import (
    GameConnectionDoesNotExist,
    PlayerAlreadyConnected,
    PlayerNotConnected,
)


class GameConnectionManager:
    def __init__(self):
        self._games: Dict[int, Dict[int, WebSocket]] = {}

    def createGameConnection(self, gameId: int):
        """Creates a new game entry for future connections.

        Args:
            gameId: game's id to create.
        """
        self._games[gameId] = {}

    @staticmethod
    async def keepAlive(websocket: WebSocket):
        """Keeps websocket connections alive

        Args:
            websocket: connection to keep alive.
        """

        while True:
            await websocket.receive()

    def connectPlayerToGame(self, gameId: int, playerId: int, websocket: WebSocket):
        """Connects players to game and saves the connections.

        Args:
            gameId: id of the game to join.
            playerId: id of the player who wants to join.
            websocket: websocket connection to save.
        """

        if gameId not in self._games:
            raise GameConnectionDoesNotExist(gameId)

        if playerId in self._games[gameId]:
            raise PlayerAlreadyConnected(gameId, playerId)

        self._games[gameId][playerId] = websocket

    def disconnectPlayerFromGame(self, gameId: int, playerId: int):
        """Removes a player connection to a game and the game's entry if no player left.

        Args:
            gameId: id of the game to disconnect from.
            playerId: id of the player who wants to disconnect.
            websocket: websocket connection to remove.
        """
        if gameId not in self._games:
            raise GameConnectionDoesNotExist(gameId)

        if playerId not in self._games[gameId]:
            raise PlayerNotConnected(gameId, playerId)

        del self._games[gameId][playerId]

        if gameId not in self._games:
            del self._games[gameId]

    async def broadcastToGame(self, gameId: int, msg: Any):
        """Sends message to all players in a game.

        Args:
            gameId: id of the game.
            msg: message to send.
        """

        if gameId not in self._games:
            raise GameConnectionDoesNotExist(gameId)

        for conn in self._games[gameId].values():
            await conn.send_json(msg)

    async def sendToPlayer(self, gameId: int, playerId: int, msg: Any):
        """Sends message to all players in a game.

        Args:
            gameId: id of the game.
            msg: message to send.
        """

        if gameId not in self._games:
            raise GameConnectionDoesNotExist(gameId)

        if playerId not in self._games[gameId]:
            raise PlayerNotConnected(gameId, playerId)

        conn: WebSocket = self._games[gameId][playerId]
        await conn.send_json(msg)
