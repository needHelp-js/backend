from fastapi import status
from pony.orm import db_session

from app.models import Player, Game


def test_createGame_success(client):
    response = client.post('/games',
                           json={
                               'gameName': 'Game test',
                               'hostNickname': 'test_host_nickname'
                           })

    assert response.status_code == status.HTTP_201_CREATED
    with db_session:
        game = Game.select().first()
        player = Player.select().first()
    assert response.json() == {'idPartida': game.id, 'idHost': player.id}