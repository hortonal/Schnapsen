"""Module for card representation in our NN training."""
from dataclasses import dataclass

from schnapsen.core.card import Suit
from schnapsen.core.card import Value


@dataclass
class CardInput:
    """Object for handling card state in NN vectors."""
    suit: Suit
    value: Value
    in_my_hand: bool = False
    in_opponent_hand: bool = False
    won_by_me: bool = False
    won_by_opponent: bool = False
    is_leading_card: bool = False
