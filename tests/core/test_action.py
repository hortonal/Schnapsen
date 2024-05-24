from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value


def test_card_action():
    action = Action(card=Card(Suit.CLUB, Value.ACE))
    expected_str = "Ace Clubs"
    assert action._nice_str() == expected_str
    assert str(action) == expected_str
    assert action.__repr__() == expected_str


def test_swap_trump():
    action = Action(swap_trump=True)
    assert action._nice_str() == "Swap trump"


def test_close_deck():
    action = Action(close_deck=True)
    assert action._nice_str() == "Close Deck"


def test_equality():
    action = Action(card=Card(Suit.CLUB, Value.ACE))
    action2 = Action(card=Card(Suit.CLUB, Value.ACE))
    action3 = Action(card=Card(Suit.CLUB, Value.KING))
    action4a = Action(swap_trump=True)
    action4b = Action(swap_trump=True)
    action5 = Action(close_deck=True)
    assert action == action2
    assert action != action3
    assert action4a == action4b
    assert action4a != action5
