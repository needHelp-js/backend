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

    for i in range (20):
        if (i == 2 or i == 10 or i == 15):
            assert board._board[i][6] == "#"
        elif (i == 4 or i == 10 or i == 16):
            assert board._board[i][13] == "#"
        else:
            assert board._board[i][6] == "."
            assert board._board[i][13] == "."

    for k in range(20):
        if (k == 4 or k == 10 or k == 15):
            assert board._board[6][k] == "#"
        elif (k == 3 or k == 10 or k == 16):
            assert board._board[13][k] == "#"
        else:
            assert board._board[6][k] == "."
            assert board._board[13][k] == "."
    
    for i in range(8):
        assert i+1 == board._rooms[i].id


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
    assert 1 == board.getRoomId("COCHERA")
    assert 2 == board.getRoomId("ALCOBA")
    assert 3 == board.getRoomId("BIBLIOTECA")
    assert 4 == board.getRoomId("VESTIBULO")
    assert 5 == board.getRoomId("PANTEON")
    assert 6 == board.getRoomId("BODEGA")
    assert 7 == board.getRoomId("SALON")
    assert 8 == board.getRoomId("LABORATORIO")


def test_getRoomId_fail():
    assert None == board.getRoomId("sdf")


def test_getRoomName_succes():
    assert "COCHERA" == board.getRoomName(1)
    assert "ALCOBA" == board.getRoomName(2)
    assert "BIBLIOTECA" == board.getRoomName(3)
    assert "VESTIBULO" == board.getRoomName(4)
    assert "PANTEON" == board.getRoomName(5)
    assert "BODEGA" == board.getRoomName(6)
    assert "SALON" == board.getRoomName(7)
    assert "LABORATORIO" == board.getRoomName(8)


def test_getRoomName_fail():
    assert None == board.getRoomName(0)
    assert None == board.getRoomName(9)


def test_detectRoom_success():
    assert "COCHERA" == board.detectRoom(2, 6)
    assert "ALCOBA" == board.detectRoom(6, 10)
    assert "BIBLIOTECA" == board.detectRoom(4, 6)
    assert "VESTIBULO" == board.detectRoom(6, 4)
    assert "VESTIBULO" == board.detectRoom(10, 6)
    assert "VESTIBULO" == board.detectRoom(13, 3)
    assert "PANTEON" == board.detectRoom(6, 15)
    assert "PANTEON" == board.detectRoom(10, 13)
    assert "PANTEON" == board.detectRoom(13, 16)
    assert "BODEGA" == board.detectRoom(15, 6)
    assert "SALON" == board.detectRoom(13, 10)
    assert "LABORATORIO" == board.detectRoom(16, 13)


def test_moveLeft():
    board.createBoard()

    availablePositions = []
    availableRooms = []
    board.moveLeft(6, 5, 3, availablePositions, availableRooms)
    assert [(6, 4), (6, 3), (6, 2)] == availablePositions
    assert ["VESTIBULO"] == availableRooms

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
    assert ["PANTEON"] == availableRooms

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
    assert ["BODEGA"] == availableRooms

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
    assert ["COCHERA"] == availableRooms

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

def test_calculatePositions():
    availablePositions, availableRooms = board.calculatePositions(0, 0, 6)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    availablePositions, availableRooms = board.calculatePositions(6, 6, 0)
    assert [] == availablePositions
    assert [] == availableRooms

    availablePositions = []
    availableRooms = []
    availablePositions, availableRooms = board.calculatePositions(2, 6, 2)
    assert [(2, 6), (1, 6), (0, 6), (3, 6), (4, 6)] == availablePositions
    assert ["COCHERA"] == availableRooms
    
def test_checkIfPlayerInRoom(app, boardData):
    with db_session:

        p1 = Player.get(id=1)
        availablePositions, availableRooms = board.checkIfPlayerInRoom(p1, 2)
        assert [(2, 6), (1, 6), (3, 6)] == availablePositions
        assert ["COCHERA"] == availableRooms

        p2 = Player.get(id=2)
        availablePositions, availableRooms = board.checkIfPlayerInRoom(p2, 2)
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
        assert board.checkRoom(p2, 6, "COCHERA")

def test_checkRoom_fail(app, boardData):
    with db_session:

        p2 = Player.get(id=2)
        assert not board.checkRoom(p2, 6, "BIBLIOTECA")