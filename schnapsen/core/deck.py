"""Card Deck Class."""
import random
from typing import List, Optional

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value


class Deck(list):
    """Collection of Cards used in this game."""

    def __init__(self, cards: Optional[List[Card]] = None) -> None:
        """Create a Deck.

        Args:
            cards (Optional[List[Card]], optional): A deck of cards (for testing/simulation). Defaults to None.
        """
        super().__init__()
        if cards is None:
            for card_key in Value:
                for suit_key in Suit:
                    self.append(Card(suit_key, card_key))
            # Shuffle deck ready for dealing.
            random.shuffle(self)
        else:
            [self.append(card) for card in cards]
