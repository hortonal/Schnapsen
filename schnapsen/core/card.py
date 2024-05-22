"""Module for Card related objects."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Suit(IntEnum):
    """Int enum representing suits."""
    SPADE = 0
    CLUB = 1
    HEART = 2
    DIAMOND = 3


class Value(IntEnum):
    """Int enum representing card values.

    The int here is used to store the card's basic game value.
    """
    TEN = 10
    JACK = 2
    QUEEN = 3
    KING = 4
    ACE = 11


Value_string_map = {
    Value.TEN: 'Ten',
    Value.JACK: 'Jack',
    Value.QUEEN: 'Queen',
    Value.KING: 'King',
    Value.ACE: 'Ace'}

Suit_string_map = {
    Suit.SPADE: 'Spades',
    Suit.CLUB: 'Clubs',
    Suit.HEART: 'Hearts',
    Suit.DIAMOND: 'Diamonds'}


@dataclass()
class Card:
    """Simple card object."""
    suit: Suit
    value: Value

    def _print_str_name(self) -> str:
        return Value_string_map[self.value] + ' ' + Suit_string_map[self.suit]

    def __repr__(self) -> str:
        """String rep."""
        return self._print_str_name()

    def __str__(self) -> str:
        """String rep."""
        return self._print_str_name()

    def __eq__(self, other: Card) -> bool:
        """Determine Card equality."""
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
