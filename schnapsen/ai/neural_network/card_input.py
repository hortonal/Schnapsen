from dataclasses import dataclass

from schnapsen.core.card import Suit
from schnapsen.core.card import Value


@dataclass
class CardInput:

    def __init__(self, suit: Suit, value: Value) -> None:
        self.suit: Suit = suit
        self.value: Value = value
        self.in_my_hand: bool = False
        self.in_opponent_hand: bool = False
        self.won_by_me: bool = False
        self.won_by_opponent: bool = False
        self.is_leading_card: bool = False
