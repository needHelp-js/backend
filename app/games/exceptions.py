class MisterioBaseException(Exception):
    pass


class GameConnectionDoesNotExist(MisterioBaseException):
    def __init__(self, id: int):
        message: str = f"Game {id} doesn't have an open connection"
        super().__init__(message)


class PlayerAlreadyConnected(MisterioBaseException):
    def __init__(self, gameId: int, playerId: int):
        message: str = f"player {playerId} already connected to game {gameId}"
        super().__init__(message)


class PlayerNotConnected(MisterioBaseException):
    def __init__(self, gameId: int, playerId: int):
        message: str = f"Player {playerId} from game {gameId} not connected to the game"
        super().__init__(message)
