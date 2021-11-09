from typing import List, Tuple

from app.models import Player


class Room:
    def __init__(self, id, name, entries):
        self.id = id
        self.name = name
        self.entries = entries


class BoardManager:
    def __init__(self):
        self._board = [[]]
        self._rooms = []
        self._boardTuples = {}
        self._boardId = [[]]

    def createBoard(self):
        """Crea y configura las cosas iniciales del tablero

        Modela el tablero con una matriz de tamaño 20x20, marcando con '.' las casillas por donde los jugadores
        pueden moverse, y con '#' las entradas a los recintos.

        También se le da un ID a cada casilla de la matriz, para así poder guardar la posición de los jugadores
        en la base de datos.
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

        room1 = Room(id=1, name="COCHERA", entries=[(2, 6)])
        self._rooms.append(room1)
        room2 = Room(id=2, name="ALCOBA", entries=[(6, 10)])
        self._rooms.append(room2)
        room3 = Room(id=3, name="BIBLIOTECA", entries=[(4, 6)])
        self._rooms.append(room3)
        room4 = Room(id=4, name="VESTIBULO", entries=[(6, 4), (10, 6), (13, 3)])
        self._rooms.append(room4)
        room5 = Room(id=5, name="PANTEON", entries=[(6, 15), (10, 13), (13, 16)])
        self._rooms.append(room5)
        room6 = Room(id=6, name="BODEGA", entries=[(15, 6)])
        self._rooms.append(room6)
        room7 = Room(id=7, name="SALON", entries=[(13, 10)])
        self._rooms.append(room7)
        room8 = Room(id=8, name="LABORATORIO", entries=[(16, 13)])
        self._rooms.append(room8)

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
        """Obtiene el ID de una casilla del tablero a partir de sus coordenadas x, y

        Args:
            position: tupla que representa la posición (x, y) en la matriz del tablero
        """

        if position[0] < 0 or position[0] > 19 or position[1] < 0 or position[1] > 19:
            return None

        return self._boardId[position[0]][position[1]]

    def getPositionTupleFromId(self, id: int):
        """Obtiene a partir del ID de la casilla, la tupla (x, y) que representa su posición en la matriz

        Args:
            id: id único de la casilla
        """
        if id is None:
            return None

        if id < 0 or id > 399:
            return None

        return self._boardTuples[id][0], self._boardTuples[id][1]

    def getRoomId(self, roomName):
        """Obtiene el ID de un recinto a través de su nombre

        Args:
            roomName: nombre del recinto
        """

        for r in self._rooms:
            if r.name == roomName:
                return r.id

        return None

    def getRoomName(self, roomId):
        """Obtiene el nombre de un recinto a partir de su ID

        Args:
            roomId: ID del recinto
        """

        for r in self._rooms:
            if r.id == roomId:
                return r.name

        return None

    def detectRoom(self, y: int, x: int):
        """Detecta a qué recinto puede acceder un jugador

        Args:
            y, x: representan la posición en el tablero de la entrada al recinto disponible
        """

        for r in self._rooms:
            if (y, x) in r.entries:
                return r.name

    def moveLeft(self, y, x, moves, availablePositions, availableRooms):
        """Detecta todas las casillas y recintos que se encuentran disponibles a la izquierda del jugador

        Args:
            y, x: representan la posición a partir de donde se quiere realizar el cálculo de casillas
            moves: cantidad de movimientos disponibles
            availablePositions: lista que almacena las casillas disponibles
            availableRooms: lista que almacena los recintos disponibles
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x - 1, y, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and x_AxisPosition >= 0:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

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
        """Detecta todas las casillas y recintos que se encuentran disponibles a la derecha del jugador

        Args:
            y, x: representan la posición a partir de donde se quiere realizar el cálculo de casillas
            moves: cantidad de movimientos disponibles
            availablePositions: lista que almacena las casillas disponibles
            availableRooms: lista que almacena los recintos disponibles
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x + 1, y, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and x_AxisPosition <= 19:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

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
        """Detecta todas las casillas y recintos que se encuentran arriba de la posición del jugador

        Args:
            y, x: representan la posición a partir de donde se quiere realizar el cálculo de casillas
            moves: cantidad de movimientos disponibles
            availablePositions: lista que almacena las casillas disponibles
            availableRooms: lista que almacena los recintos disponibles
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x, y - 1, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and y_AxisPosition >= 0:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

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
        """Detecta todas las casillas y recintos que se encuentran debajo de la posición jugador

        Args:
            y, x: representan la posición a partir de donde se quiere realizar el cálculo de casillas
            moves: cantidad de movimientos disponibles
            availablePositions: lista que almacena las casillas disponibles
            availableRooms: lista que almacena los recintos disponibles
        """

        x_AxisPosition, y_AxisPosition, remainingMoves = x, y + 1, moves - 1
        aux_remainingMoves, aux_yAxis, aux_xAxis = 0, 0, 0

        while remainingMoves >= 0 and y_AxisPosition <= 19:

            availablePositions.append((y_AxisPosition, x_AxisPosition))

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
        """Calcula todas las casillas a las que se puede mover un jugador según el número que obtuvó en el dado

        Args:
            y, x: representan la posición inicial del jugador
            diceNumber: el número que obtuvo el jugador al tirar el dado
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

        if (x == 6 or x == 13) and (y == 6 or y == 13):
            self.moveUp(y, x, diceNumber, availablePositions, availableRooms)
            self.moveDown(y, x, diceNumber, availablePositions, availableRooms)
            self.moveLeft(y, x, diceNumber, availablePositions, availableRooms)
            self.moveRight(y, x, diceNumber, availablePositions, availableRooms)

        elif x == 6 or x == 13:
            self.moveUp(y, x, diceNumber, availablePositions, availableRooms)
            self.moveDown(y, x, diceNumber, availablePositions, availableRooms)

        elif y == 6 or y == 13:
            self.moveLeft(y, x, diceNumber, availablePositions, availableRooms)
            self.moveRight(y, x, diceNumber, availablePositions, availableRooms)

        return availablePositions, availableRooms

    def calculatePositions(self, player: Player, diceNumber):
        """Calcula las posiciones disponibles a partir de la posición del jugador.

        En caso de que el jugador se encuentre en un recinto, entonces calcula todas las casillas
        a las que se puede mover a partir de cada una de las salidas del recinto. En caso contrario,
        simplemente calcula las casillas disponibles a partir de la ubicación del jugador en el tablero.

        Args:
            player: jugador que intenta realizar el movimiento
            diceNumber: el número que el jugador obtuvo al tirar el dado
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
                if diceNumber == 1:
                    availablePositions.append((y, x))
                else:
                    availablePositions.append((y, x))
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
        """Chequea si la posición a la que un jugador se intenta mover está dentro de sus casillas disponibles

        Args:
            player: jugador que intenta moverse
            diceNumber: número que obtuvo en el dado
            position: posición a la que el jugador quiere moverse
        """

        availablePositions, _ = self.calculatePositions(player, diceNumber)

        if tuple(position) in availablePositions:
            return True

        return False

    def checkRoom(self, player: Player, diceNumber, room: str):
        """Chequea si el recinto al que un jugador quiere entrar está dentro de sus recintos disponibles

        Args:
            player: jugador que intenta entrar al recinto
            diceNumber: número que obtuvo en el dado
            room: recinto al que el jugador quiere entrar
        """

        _, availableRooms = self.calculatePositions(player, diceNumber)

        if room in availableRooms:
            return True

        return False
