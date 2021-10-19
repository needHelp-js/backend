from fastapi import responses


def test_nonExistentGame(client, data):
    response = client.patch("/games/3/begin/6")
    assert response.status_code == 404
    assert response.json() == {'Error' : 'Partida no existente'}


def test_nonExistentPlayer(client, data):
    response = client.patch("/games/1/begin/6")
    assert response.status_code == 404
    assert response.json() == {'Error' : 'Jugador no existente'}


def test_playerIsNotHost(client, data):
    response = client.patch("/games/1/begin/2")
    assert response.status_code == 403
    assert response.json() == {'Error' : 'El jugador no es el host'}

def test_gameAlreadyStarted(client, data):
    response = client.patch("/games/2/begin/2")
    assert response.status_code == 403
    assert response.json() == {'Error' : 'La partida ya empezó'}

def test_successCase(client, data):
    response = client.patch("/games/1/begin/1")
    assert response.status_code == 200
    assert response.json() == 1