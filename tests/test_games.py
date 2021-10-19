from fastapi import status
from pony.orm import db_session

from app.models import Player, Game


def test_createGame_success(client):
    gameName = 'Game test'
    hostNickname = 'test_host_nickname'

    response = client.post('/games',
                           json={
                               'gameName': gameName,
                               'hostNickname': hostNickname
                           })

    assert response.status_code == status.HTTP_201_CREATED
    with db_session:
        game = Game.get(name=gameName)
        player = Player.get(nickname=hostNickname)
    assert response.json() == {'idPartida': game.id, 'idHost': player.id}