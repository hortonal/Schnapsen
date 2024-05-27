"""Simple object to define a particular player action."""
from __future__ import annotations

from dataclasses import dataclass

from schnapsen.core.card import Card


@dataclass
class Action:
    """A wrapper for possible game actions."""

    card: Card = None                   # The Card involved in the Action if appropriate
    declare_marriage: bool = False      # True, with a card set, declares a marriage of that suit
    swap_trump: bool = False            # True if the action is swapping trumps
    close_deck: bool = False            # True if the action is closing the deck

    def _nice_str(self) -> str:
        return_string = ''
        if self.swap_trump:
            return_string = 'Swap trump'

        if self.close_deck:
            return_string += 'Close Deck'

        if self.declare_marriage:
            return_string += 'Play marriage - '

        if self.card is not None:
            return_string += str(self.card)

        return return_string

    def __repr__(self) -> str:
        """Get str rep.

        Returns:
            str: The string representation.
        """
        return self._nice_str()

    def __str__(self) -> str:
        """Get str rep.

        Returns:
            str: The string representation.
        """
        return self._nice_str()

    def __eq__(self, other: Action) -> bool:
        """Check for eqaulity.

        Args:
            other (Action): Item to check against.

        Returns:
            bool: True if items equivalent, otherwise False.
        """
        if isinstance(other, Action):
            return self.card == other.card and self.declare_marriage == other.declare_marriage and \
                self.swap_trump == other.swap_trump and self.close_deck == other.close_deck
