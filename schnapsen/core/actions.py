"""Module for helpers around the complete action space."""
from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value

ALL_GAME_ACTIONS = {
    0: Action(card=Card(Suit.DIAMOND, Value.JACK)),
    1: Action(card=Card(Suit.DIAMOND, Value.QUEEN)),
    2: Action(card=Card(Suit.DIAMOND, Value.KING)),
    3: Action(card=Card(Suit.DIAMOND, Value.TEN)),
    4: Action(card=Card(Suit.DIAMOND, Value.ACE)),
    5: Action(card=Card(Suit.SPADE, Value.JACK)),
    6: Action(card=Card(Suit.SPADE, Value.QUEEN)),
    7: Action(card=Card(Suit.SPADE, Value.KING)),
    8: Action(card=Card(Suit.SPADE, Value.TEN)),
    9: Action(card=Card(Suit.SPADE, Value.ACE)),
    10: Action(card=Card(Suit.HEART, Value.JACK)),
    11: Action(card=Card(Suit.HEART, Value.QUEEN)),
    12: Action(card=Card(Suit.HEART, Value.KING)),
    13: Action(card=Card(Suit.HEART, Value.TEN)),
    14: Action(card=Card(Suit.HEART, Value.ACE)),
    15: Action(card=Card(Suit.CLUB, Value.JACK)),
    16: Action(card=Card(Suit.CLUB, Value.QUEEN)),
    17: Action(card=Card(Suit.CLUB, Value.KING)),
    18: Action(card=Card(Suit.CLUB, Value.TEN)),
    19: Action(card=Card(Suit.CLUB, Value.ACE)),
    # Marriages
    20: Action(card=Card(Suit.DIAMOND, Value.QUEEN), declare_marriage=True),
    21: Action(card=Card(Suit.DIAMOND, Value.KING), declare_marriage=True),
    22: Action(card=Card(Suit.SPADE, Value.QUEEN), declare_marriage=True),
    23: Action(card=Card(Suit.SPADE, Value.KING), declare_marriage=True),
    24: Action(card=Card(Suit.HEART, Value.QUEEN), declare_marriage=True),
    25: Action(card=Card(Suit.HEART, Value.KING), declare_marriage=True),
    26: Action(card=Card(Suit.CLUB, Value.QUEEN), declare_marriage=True),
    27: Action(card=Card(Suit.CLUB, Value.KING), declare_marriage=True),
    # Special Actions
    28: Action(swap_trump=True),
    29: Action(close_deck=True),
}


def get_action_index(action: Action) -> int:
    """Determine the action id given an action.

    Args:
        action (Action): Input Action.

    Returns:
        int: Actions index.
    """
    # let's do this the slow way to start
    for key, value in ALL_GAME_ACTIONS.items():
        if value == action:
            return key
