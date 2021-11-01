from app.models import checkCardName, checkCardType
from app.enums import CardType, MonstersNames, RoomName, VictimsNames

def test_checkCardType():

    assert checkCardType("something different") == False
    assert checkCardType(CardType.MONSTER.value)

def test_checkCardName():
    
    assert checkCardName("something different") == False
    assert checkCardName(VictimsNames.CONDE.value)
    assert checkCardName(MonstersNames.DRACULA.value)
    assert checkCardName(RoomName.ALCOBA.value)