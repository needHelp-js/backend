import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocket
from app.games.exceptions import (
    GameConnectionDoesNotExist,
    PlayerAlreadyConnected,
    PlayerNotConnected,
)
from app.games.endpoints import availablePositions, board
from app.models import Player
from pony.orm import db_session


def test_createBoard():
    board.createBoard()

    for i in range(20):
        if i == 3:
            assert board._board[i][13] == "!"

        elif i == 4:
            assert board._board[i][6] == "!"
            assert board._board[i][13] == "#"

        elif i == 14:
            assert board._board[i][6] == "!"
            assert board._board[i][13] == "!"

        elif i == 2 or i == 10 or i == 15:
            assert board._board[i][6] == "#"

        elif i == 10 or i == 16:
            assert board._board[i][13] == "#"

        else:
            assert board._board[i][6] == "."
            assert board._board[i][13] == "."

    for k in range(20):

        if k == 14:
            assert board._board[6][k] == "!"

        elif k == 3:
            assert board._board[6][k] == "!"
            assert board._board[13][k] == "#"

        elif k == 15:
            assert board._board[13][k] == "!"
            assert board._board[6][k] == "#"

        elif k == 4 or k == 10 or k == 15:
            assert board._board[6][k] == "#"

        elif k == 10 or k == 16:
            assert board._board[13][k] == "#"

        else:
            assert board._board[6][k] == "."
            assert board._board[13][k] == "."

    for i in range(8):
        assert i + 1 == board._rooms[i].id


def test_getPositionIdFromTuple_success():
    k = 0
    for i in range(20):
        for j in range(20):
            assert k == board.getPositionIdFromTuple((i, j))
            k += 1


def test_getPositionIdFromTuple_fail():
    assert None == board.getPositionIdFromTuple((-1, 6))
    assert None == board.getPositionIdFromTuple((20, 6))
    assert None == board.getPositionIdFromTuple((6, -1))
    assert None == board.getPositionIdFromTuple((6, 20))
    assert None == board.getPositionIdFromTuple((20, 20))


def test_getPositionTuplefromId_succes():
    k = 0
    for i in range(20):
        for j in range(20):
            assert (i, j) == board.getPositionTupleFromId(k)
            k += 1


def test_getPositionTuplefromId_fail():
    assert None == board.getPositionTupleFromId(400)
    assert None == board.getPositionTupleFromId(-1)


def test_getRoomId_success():
    assert 1 == board.getRoomId("Cochera")
    assert 2 == board.getRoomId("Alcoba")
    assert 3 == board.getRoomId("Biblioteca")
    assert 4 == board.getRoomId("Vestibulo")
    assert 5 == board.getRoomId("Panteon")
    assert 6 == board.getRoomId("Bodega")
    assert 7 == board.getRoomId("Salon")
    assert 8 == board.getRoomId("Laboratorio")


def test_getRoomId_fail():
    assert None == board.getRoomId("sdf")


def test_getRoomName_succes():
    assert "Cochera" == board.getRoomName(1)
    assert "Alcoba" == board.getRoomName(2)
    assert "Biblioteca" == board.getRoomName(3)
    assert "Vestibulo" == board.getRoomName(4)
    assert "Panteon" == board.getRoomName(5)
    assert "Bodega" == board.getRoomName(6)
    assert "Salon" == board.getRoomName(7)
    assert "Laboratorio" == board.getRoomName(8)


def test_getRoomName_fail():
    assert None == board.getRoomName(0)
    assert None == board.getRoomName(9)


def test_detectRoom_success():
    assert "Cochera" == board.detectRoom(2, 6)
    assert "Alcoba" == board.detectRoom(6, 10)
    assert "Biblioteca" == board.detectRoom(4, 13)
    assert "Vestibulo" == board.detectRoom(6, 4)
    assert "Vestibulo" == board.detectRoom(10, 6)
    assert "Vestibulo" == board.detectRoom(13, 3)
    assert "Panteon" == board.detectRoom(6, 15)
    assert "Panteon" == board.detectRoom(10, 13)
    assert "Panteon" == board.detectRoom(13, 16)
    assert "Bodega" == board.detectRoom(15, 6)
    assert "Salon" == board.detectRoom(13, 10)
    assert "Laboratorio" == board.detectRoom(16, 13)


def test_specialCells():
    board.createBoard()

    availablePositions, _ = board._calculateAvailablePositions(4, 6, 1)
    assert [(14, 6), (3, 6), (5, 6)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(14, 6, 1)
    assert [(4, 6), (13, 6), (15, 6)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(3, 13, 1)
    assert [(14, 13), (2, 13), (4, 13)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(14, 13, 1)
    assert [(3, 13), (13, 13), (15, 13)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(6, 3, 1)
    assert [(6, 14), (6, 2), (6, 4)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(6, 14, 1)
    assert [(6, 3), (6, 13), (6, 15)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(13, 4, 1)
    assert [(13, 15), (13, 3), (13, 5)] == availablePositions

    availablePositions, _ = board._calculateAvailablePositions(13, 15, 1)
    assert [(13, 4), (13, 14), (13, 16)] == availablePositions


def test_moveLeft():
    board.createBoard()

    availablePositions = []
    availableRooms = []
    board.moveLeft(6, 2, 3, availablePositions, availableRooms)
    assert [(6, 1), (6, 0)] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveLeft(6, 5, 4, availablePositions, availableRooms)
    assert [(6, 4), (6, 3), (6, 14), (6, 13), (6, 2), (6, 1)]
    assert ["Vestibulo"] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveLeft(6, 0, 2, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveLeft(6, 3, 0, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms


def test_moveRight():
    board.createBoard()

    availablePositions = []
    availableRooms = []
    board.moveRight(6, 14, 3, availablePositions, availableRooms)
    assert [(6, 15), (6, 16), (6, 17)] == availablePositions
    assert ["Panteon"] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveRight(6, 13, 3, availablePositions, availableRooms)
    assert [(6, 14), (6, 3), (6, 2), (6, 4), (6, 15), (6, 16)] == availablePositions
    assert ["Panteon"] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveRight(6, 19, 2, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveRight(6, 19, 0, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms


def test_moveUp():
    board.createBoard()

    availablePositions = []
    availableRooms = []
    board.moveUp(17, 6, 3, availablePositions, availableRooms)
    assert [(16, 6), (15, 6), (14, 6)] == availablePositions
    assert ["Bodega"] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveUp(4, 13, 3, availablePositions, availableRooms)
    assert [
        (3, 13),
        (14, 13),
        (13, 13),
        (15, 13),
        (2, 13),
        (1, 13),
    ] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveUp(0, 6, 2, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveUp(10, 6, 0, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms


def test_moveDown():
    board.createBoard()

    availablePositions = []
    availableRooms = []
    board.moveDown(0, 6, 3, availablePositions, availableRooms)
    assert [(1, 6), (2, 6), (3, 6)] == availablePositions
    assert ["Cochera"] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveDown(3, 6, 3, availablePositions, availableRooms)
    assert [(4, 6), (14, 6), (13, 6), (15, 6), (5, 6), (6, 6)] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveDown(19, 6, 2, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    board.moveDown(6, 6, 0, availablePositions, availableRooms)
    assert [] == availablePositions
    assert [] == availableRooms


def test_calculateAvailablePositions():
    board.createBoard()

    availablePositions, availableRooms = board._calculateAvailablePositions(0, 0, 6)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    availablePositions, availableRooms = board._calculateAvailablePositions(6, 6, 0)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    availablePositions, availableRooms = board._calculateAvailablePositions(2, 6, 2)
    assert [(2, 6), (1, 6), (0, 6), (3, 6), (4, 6)] == availablePositions
    assert ["Cochera"] == availableRooms

    availablePositions = []
    availableRooms = []
    availablePositions, availableRooms = board._calculateAvailablePositions(6, 6, 3)
    assert [
        (6, 6),
        (5, 6),
        (4, 6),
        (14, 6),
        (3, 6),
        (7, 6),
        (8, 6),
        (9, 6),
        (6, 5),
        (6, 4),
        (6, 3),
        (6, 7),
        (6, 8),
        (6, 9),
    ] == availablePositions

    assert ["Vestibulo"] == availableRooms


def test_calculatePositions(app, boardData):
    board.createBoard()

    with db_session:

        p1 = Player.get(id=1)
        availablePositions, availableRooms = board.calculatePositions(p1, 2)
        assert [(2, 6), (1, 6), (3, 6)] == availablePositions
        assert ["Cochera"] == availableRooms

        p2 = Player.get(id=2)
        availablePositions, availableRooms = board.calculatePositions(p2, 2)
        assert [(0, 6), (1, 6), (2, 6)] == availablePositions
        assert [] == availableRooms


def test_checkPosition_success(app, boardData):
    with db_session:

        p2 = Player.get(id=2)
        assert board.checkPosition(p2, 2, (2, 6))


def test_checkPosition_fail(app, boardData):
    with db_session:

        p2 = Player.get(id=2)
        assert board.checkPosition(p2, 2, (2, 6))


def test_checkRoom_success(app, boardData):
    with db_session:

        p2 = Player.get(id=2)
        assert board.checkRoom(p2, 6, "Cochera")


def test_checkRoom_fail(app, boardData):
    with db_session:

        p2 = Player.get(id=2)
        assert not board.checkRoom(p2, 6, "Biblioteca")
