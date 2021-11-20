from typing import List, Tuple

from app.enums import RoomsNames
from app.models import Player


class Room:
    def __init__(self, id, name, entries):
        self.id = id
        self.name = name
        self.entries = entries


class SpecialCell:
    def __init__(self, initialPosition: Tuple, teleportPosition: Tuple):
        self.initialPosition = initialPosition
        self.teleportPosition = teleportPosition


class BoardManager:
    def __init__(self):
        self._board = [[]]
        self._rooms = []
        self._specialCells = []
        self._boardTuples = {}
        self._boardId = [[]]

    def createBoard(self):
        """Creates and configures the initials things for the board

        Models the board as a matrix of size 20x20, marking with '.' the availaible positions where the players
        can move, and with '#' the room's entries.

        It also gives an ID to each cell of the matrix, doing so able us to save the position of the players
        in the data base.
        """
        self._board = [["*" for x in range(20)] for y in range(20)]
        for y in range(20):
            self._board[y][6] = "."
            self._board[y][13] = "."

        for x in range(20):
            self._board[6][x] = "."
            self._board[13][x] = "."

        # Entradas a recintos
        self._board[2][6] = "#"
        self._board[10][6] = "#"
        self._board[15][6] = "#"
        self._board[4][13] = "#"
        self._board[10][13] = "#"
        self._board[16][13] = "#"
        self._board[6][4] = "#"
        self._board[6][10] = "#"
        self._board[6][15] = "#"
        self._board[13][3] = "#"
        self._board[13][10] = "#"
        self._board[13][16] = "#"

        room1 = Room(id=1, name=RoomsNames.COCHERA.value, entries=[(2, 6)])
        self._rooms.append(room1)
        room2 = Room(id=2, name=RoomsNames.ALCOBA.value, entries=[(6, 10)])
        self._rooms.append(room2)
        room3 = Room(id=3, name=RoomsNames.BIBLIOTECA.value, entries=[(4, 13)])
        self._rooms.append(room3)
        room4 = Room(
            id=4, name=RoomsNames.VESTIBULO.value, entries=[(6, 4), (10, 6), (13, 3)]
        )
        self._rooms.append(room4)
        room5 = Room(
            id=5, name=RoomsNames.PANTEON.value, entries=[(6, 15), (10, 13), (13, 16)]
        )
        self._rooms.append(room5)
        room6 = Room(id=6, name=RoomsNames.BODEGA.value, entries=[(15, 6)])
        self._rooms.append(room6)
        room7 = Room(id=7, name=RoomsNames.SALON.value, entries=[(13, 10)])
        self._rooms.append(room7)
        room8 = Room(id=8, name=RoomsNames.LABORATORIO.value, entries=[(16, 13)])
        self._rooms.append(room8)

        """
        Casillas especiales: [(3, 6) -> (14, 6)]
                             [(3, 13) -> (14, 13)]
                             [(13, 4) -> (13, 15)]
        """

        # Casillas Especiales
        self._board[6][3] = "!"
        self._board[6][14] = "!"
        self._board[13][4] = "!"
        self._board[13][15] = "!"
        self._board[4][6] = "!"
        self._board[14][6] = "!"
        self._board[3][13] = "!"
        self._board[14][13] = "!"

        specialCell1 = SpecialCell(initialPosition=(6, 3), teleportPosition=(6, 14))
        self._specialCells.append(specialCell1)
        specialCell2 = SpecialCell(initialPosition=(6, 14), teleportPosition=(6, 3))
        self._specialCells.append(specialCell2)
        specialCell3 = SpecialCell(initialPosition=(13, 4), teleportPosition=(13, 15))
        self._specialCells.append(specialCell3)
        specialCell4 = SpecialCell(initialPosition=(13, 15), teleportPosition=(13, 4))
        self._specialCells.append(specialCell4)
        specialCell5 = SpecialCell(initialPosition=(4, 6), teleportPosition=(14, 6))
        self._specialCells.append(specialCell5)
        specialCell6 = SpecialCell(initialPosition=(14, 6), teleportPosition=(4, 6))
        self._specialCells.append(specialCell6)
        specialCell7 = SpecialCell(initialPosition=(3, 13), teleportPosition=(14, 13))
        self._specialCells.append(specialCell7)
        specialCell8 = SpecialCell(initialPosition=(14, 13), teleportPosition=(3, 13))
        self._specialCells.append(specialCell8)

        i = 0
        for j in range(20):
            for k in range(20):
                self._boardTuples[i] = (j, k)
                i += 1

        self._boardId = [[0 for x in range(20)] for y in range(20)]
        i = 0
        for j in range(20):
            for k in range(20):
                self._boardId[j][k] = i
                i += 1

    def getPositionIdFromTuple(self, position: Tuple):
        """Get the ID of a cell in the board from its coordinates x and y

        Args:
            position: a tuple which represent the position (x, y)
        """

        if position[0] < 0 or position[0] > 19 or position[1] < 0 or position[1] > 19:
            return None

        return self._boardId[position[0]][position[1]]

    def getPositionTupleFromId(self, id: int):
        """Get the tuple representing the position (x, y) of a cell in a matrix from its ID

        Args:
            id: id of the cell
        """
        if id is None:
            return None

        if id < 0 or id > 399:
            return None

        return self._boardTuples[id][0], self._boardTuples[id][1]

    def getRoomId(self, roomName):
        """Get the id of a room from its name

        Args:
            roomName: name of the room
        """

        for r in self._rooms:
            if r.name == roomName:
                return r.id

        return None

    def getRoomName(self, roomId):
        """Get the room's name from its ID

        Args:
            roomId: Id of the room
        """

        for r in self._rooms:
            if r.id == roomId:
                return r.name

        return None

    def detectRoom(self, y: int, x: int):
        """Detect which room is available for the player

        Args:
            y, x: represent the position in the board of the room's entrie
        """

        for r in self._rooms:
            if (y, x) in r.entries:
                return r.name

    def detectSpecialCell(self, y: int, x: int):

        for c in self._specialCells:
            if (y, x) == c.initialPosition:
                return c.teleportPosition[0], c.teleportPosition[1]

        return None

    def moveLeft(self, y, x, moves, availablePositions, availableRooms):
        """Detects all the cells and rooms which are available to the left of the player.

        Args:
            y, x: represent the initial position of the player
            moves: number of available moves
            availablePositions: list for storing the available positions
            availableRooms: list for storing the available rooms
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x - 1, y, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and x_AxisPosition >= 0:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

            if self._board[y_AxisPosition][x_AxisPosition] == "!":
                if remainingMoves >= 1:
                    aux_Y, aux_X = self.detectSpecialCell(
                        y_AxisPosition, x_AxisPosition
                    )
                    availablePositions.append((aux_Y, aux_X))
                    self.moveLeft(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )
                    self.moveRight(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )

            if self._board[y_AxisPosition + 1][x_AxisPosition] != "*":
                aux_remainingMoves = remainingMoves
                aux_yAxis = y_AxisPosition
                aux_xAxis = x_AxisPosition

            if (
                self._board[y_AxisPosition][x_AxisPosition] == "#"
                and remainingMoves >= 1
            ):
                room = self.detectRoom(y_AxisPosition, x_AxisPosition)
                availableRooms.append(room)

            x_AxisPosition -= 1
            remainingMoves -= 1

        if aux_remainingMoves > 0:
            self.moveUp(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )
            self.moveDown(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )

    def moveRight(self, y, x, moves, availablePositions, availableRooms):
        """Detects all the cells and rooms which are available to the right of the player.

        Args:
            y, x: represent the initial position of the player
            moves: number of available moves
            availablePositions: list for storing the available positions
            availableRooms: list for storing the available rooms
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x + 1, y, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and x_AxisPosition <= 19:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

            if self._board[y_AxisPosition][x_AxisPosition] == "!":
                if remainingMoves >= 1:
                    aux_Y, aux_X = self.detectSpecialCell(
                        y_AxisPosition, x_AxisPosition
                    )
                    availablePositions.append((aux_Y, aux_X))
                    self.moveLeft(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )
                    self.moveRight(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )

            if self._board[y_AxisPosition + 1][x_AxisPosition] != "*":
                aux_remainingMoves = remainingMoves
                aux_yAxis = y_AxisPosition
                aux_xAxis = x_AxisPosition

            if (
                self._board[y_AxisPosition][x_AxisPosition] == "#"
                and remainingMoves >= 1
            ):
                room = self.detectRoom(y_AxisPosition, x_AxisPosition)
                availableRooms.append(room)

            x_AxisPosition += 1
            remainingMoves -= 1

        if aux_remainingMoves > 0:
            self.moveUp(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )
            self.moveDown(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )

    def moveUp(self, y, x, moves, availablePositions, availableRooms):
        """Detects all the cells and rooms which are available above the player.

        Args:
            y, x: represent the initial position of the player
            moves: number of available moves
            availablePositions: list for storing the available positions
            availableRooms: list for storing the available rooms
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x, y - 1, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and y_AxisPosition >= 0:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

            if self._board[y_AxisPosition][x_AxisPosition] == "!":
                if remainingMoves >= 1:
                    aux_Y, aux_X = self.detectSpecialCell(
                        y_AxisPosition, x_AxisPosition
                    )
                    availablePositions.append((aux_Y, aux_X))
                    self.moveUp(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )
                    self.moveDown(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )

            if self._board[y_AxisPosition][x_AxisPosition + 1] != "*":
                aux_remainingMoves = remainingMoves
                aux_yAxis = y_AxisPosition
                aux_xAxis = x_AxisPosition

            if (
                self._board[y_AxisPosition][x_AxisPosition] == "#"
                and remainingMoves >= 1
            ):
                room = self.detectRoom(y_AxisPosition, x_AxisPosition)
                availableRooms.append(room)

            y_AxisPosition -= 1
            remainingMoves -= 1

        if aux_remainingMoves > 0:
            self.moveLeft(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )
            self.moveRight(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )

    def moveDown(self, y, x, moves, availablePositions, availableRooms):
        """Detects all the cells and rooms which are available below the player.

        Args:
            y, x: represent the initial position of the player
            moves: number of available moves
            availablePositions: list for storing the available positions
            availableRooms: list for storing the available rooms
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x, y + 1, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and y_AxisPosition <= 19:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

            if self._board[y_AxisPosition][x_AxisPosition] == "!":
                if remainingMoves >= 1:
                    aux_Y, aux_X = self.detectSpecialCell(
                        y_AxisPosition, x_AxisPosition
                    )
                    availablePositions.append((aux_Y, aux_X))
                    self.moveUp(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )
                    self.moveDown(
                        aux_Y,
                        aux_X,
                        remainingMoves - 1,
                        availablePositions,
                        availableRooms,
                    )

            if self._board[y_AxisPosition][x_AxisPosition + 1] != "*":
                aux_remainingMoves = remainingMoves
                aux_yAxis = y_AxisPosition
                aux_xAxis = x_AxisPosition

            if (
                self._board[y_AxisPosition][x_AxisPosition] == "#"
                and remainingMoves >= 1
            ):
                room = self.detectRoom(y_AxisPosition, x_AxisPosition)
                availableRooms.append(room)

            y_AxisPosition += 1
            remainingMoves -= 1

        if aux_remainingMoves > 0:
            self.moveLeft(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )
            self.moveRight(
                aux_yAxis,
                aux_xAxis,
                aux_remainingMoves,
                availablePositions,
                availableRooms,
            )

    def _calculateAvailablePositions(self, y, x, diceNumber):
        """Calculate all the cells availables for a player

        Args:
            y, x: represent the initial position of the player
            diceNumber: Dice number
        """
        availablePositions = []
        availableRooms = []

        if x != 6 and x != 13 and y != 6 and y != 13:
            return [], []

        if diceNumber > 1:
            availablePositions.append((y, x))

        if diceNumber >= 1 and self._board[y][x] == "#":
            room = self.detectRoom(y, x)
            availableRooms.append(room)

        if x == 6 or x == 13:
            # Calculo las posiciones disponibles en caso de teletransportarte
            if diceNumber >= 1 and self._board[y][x] == "!":
                aux_Y, aux_X = self.detectSpecialCell(y, x)
                availablePositions.append((aux_Y, aux_X))
                self.moveUp(
                    aux_Y, aux_X, diceNumber - 1, availablePositions, availableRooms
                )
                self.moveDown(
                    aux_Y, aux_X, diceNumber - 1, availablePositions, availableRooms
                )

            # Calculo las posiciones disponibles desde la posición actual (sin teletransportación)
            self.moveUp(y, x, diceNumber, availablePositions, availableRooms)
            self.moveDown(y, x, diceNumber, availablePositions, availableRooms)

        if y == 6 or y == 13:
            # Calculo las posiciones disponibles en caso de teletransportarte
            if diceNumber >= 1 and self._board[y][x] == "!":
                aux_Y, aux_X = self.detectSpecialCell(y, x)
                availablePositions.append((aux_Y, aux_X))
                self.moveLeft(
                    aux_Y, aux_X, diceNumber - 1, availablePositions, availableRooms
                )
                self.moveRight(
                    aux_Y, aux_X, diceNumber - 1, availablePositions, availableRooms
                )

            # Calculo las posiciones disponibles desde la posición actual (sin teletransportación)
            self.moveLeft(y, x, diceNumber, availablePositions, availableRooms)
            self.moveRight(y, x, diceNumber, availablePositions, availableRooms)

        return availablePositions, availableRooms

    def calculatePositions(self, player: Player, diceNumber):
        """Checks if a player is in a room and calculates all the available positions they can move to

        If the player is in a room, then calculates all the availables cells from each exit of the room.
        Otherwise, just calculate the availables cells from the position of the player.
        Args:
            player: player who wants to move
            diceNumber: dice number
        """
        availablePositions = []
        availableRooms = []

        exits = []

        if player.room:
            for r in self._rooms:
                if r.id == player.room:
                    exits = r.entries
                    break

            for e in exits:
                y, x = e[0], e[1]
                availablePositions.append((y, x))
                if diceNumber != 1:
                    l1, l2 = self._calculateAvailablePositions(y, x, diceNumber - 1)
                    availablePositions.extend(l1)
                    availableRooms.extend(l2)

        else:
            y, x = self.getPositionTupleFromId(player.position)
            availablePositions, availableRooms = self._calculateAvailablePositions(
                y, x, diceNumber
            )

        # Elimina repetidos en caso de que los haya
        availablePositions = list(dict.fromkeys(availablePositions))
        availableRooms = list(dict.fromkeys(availableRooms))

        return availablePositions, availableRooms

    def checkPosition(self, player: Player, diceNumber, position: Tuple):
        """Checks if the position to which the player wants to move to is available for them.

        Args:
            player: player who wants to move
            diceNumber: dice number
            position: position to which the player wants to move to
        """

        availablePositions, _ = self.calculatePositions(player, diceNumber)

        return tuple(position) in availablePositions

    def checkRoom(self, player: Player, diceNumber, room: str):
        """Checks if the room to which the player wants to enter to is available for them.

        Args:
            player: player who wants to move
            diceNumber: dice number
            room: room to which the player wants to enter to
        """

        _, availableRooms = self.calculatePositions(player, diceNumber)

        return room in availableRooms
