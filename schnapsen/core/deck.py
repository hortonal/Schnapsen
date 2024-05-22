"""Card Deck Class."""
import random

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value


class Deck(list):
    """Collection of Cards used in this game."""

    def __init__(self) -> None:
        """Create a Deck."""
        super().__init__()
        for card_key in Value:
            for suit_key in Suit:
                self.append(Card(suit_key, card_key))

    def shuffle(self) -> None:
        """Shuffle the deck randomly."""
        random.shuffle(self)
