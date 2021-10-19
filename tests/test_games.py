def test_nonExistentGame(client, data):
    response = client.get("/games/5/dice/4")
    assert response.status_code == 404
    assert response.json() == {'Error' : 'Partida no existente'}

def test_nonExistentPlayer(client, data):
    response = client.get("/games/4/dice/6")
    assert response.status_code == 404
    assert response.json() == {'Error' : 'Jugador no existente'}


def test_incorrectTurn(client, data):
    response = client.get("/games/4/dice/5")
    assert response.status_code == 403
    assert response.json() == {'Error' : 'No es el turno del jugador'}


def test_rollDice(client, data):
    response = client.get("/games/4/dice/4")
    assert response.status_code == 200
    assert (response.json() == 1 or response.json() == 2 or response.json() == 3 or
            response.json() == 4 or response.json() == 5 or response.json() == 6)