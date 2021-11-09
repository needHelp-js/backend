import pytest
from app.enums import CardType, MonstersNames, RoomsNames, VictimsNames
from app.models import Card, Game, Player, checkCardName, checkCardType
from pony.orm import db_session
from pony.orm.core import flush


def test_checkCardType():

    assert checkCardType("something different") == False
    assert checkCardType(CardType.MONSTER.value)


def test_checkCardName():

    assert checkCardName("something different") == False
    assert checkCardName(VictimsNames.CONDE.value)
    assert checkCardName(MonstersNames.DRACULA.value)
    assert checkCardName(RoomsNames.ALCOBA.value)


def test_createGameCards(app):
    with db_session:
        p1 = Player(nickname="p1")
        g1 = Game(name="g1", host=p1)
        flush()
        g1.players.add(p1)
        cards = g1.createGameCards()

        card_set = set()

        victims_names = set(name.value for name in VictimsNames)
        monsters_names = set(name.value for name in MonstersNames)
        rooms_names = set(name.value for name in RoomsNames)

        for card in cards["victims"]:
            assert card.type == CardType.VICTIM.value
            assert card.name in victims_names
            assert card.name not in card_set

            card_set.add(card.name)

        assert len(card_set) == len(victims_names) - 1

        card_set.clear()

        for card in cards["monsters"]:
            assert card.type == CardType.MONSTER.value
            assert card.name in monsters_names
            assert card.name not in card_set

            card_set.add(card.name)

        assert len(card_set) == len(monsters_names) - 1

        card_set.clear()

        for card in cards["rooms"]:
            assert card.type == CardType.ROOM.value
            assert card.name in rooms_names
            assert card.name not in card_set

            card_set.add(card.name)

        assert len(card_set) == len(rooms_names) - 1

        envelope = g1.cards.filter(isInEnvelope=True)[:]

        assert len(envelope) == 3
        assert (
            envelope[0].type != envelope[1].type != envelope[2].type != envelope[0].type
        )
        assert (
            envelope[0].name != envelope[1].name != envelope[2].name != envelope[0].name
        )

        card_types = set(card_type.value for card_type in CardType)

        for card in envelope:
            assert card.type in card_types
            assert (
                card.name in victims_names
                or card.name in monsters_names
                or card.name in rooms_names
            )


def test_assignCardsToPlayers(app, dataTirarDado):

    with db_session:
        g1 = Game[1]
        cards = g1.createGameCards()
        g1.assignCardsToPlayers(cards)

        card_set = set(cards["victims"])
        card_set.update(cards["monsters"])
        card_set.update(cards["rooms"])

        cardsP1 = set(Player[1].cards)
        cardsP2 = set(Player[2].cards)

        assert len(cardsP1 & cardsP2) == 0
        assert cardsP1 | cardsP2 == card_set
