"""Simple object to define a particular player action."""
from __future__ import annotations

from schnapsen.core.card import Card
from schnapsen.core.marriage import Marriage


class Action:
    """A wrapper for possible game actions."""

    def __init__(self, card: Card = None, marriage: Marriage = None,
                 swap_trump: bool = False, close_deck: bool = False) -> None:
        """Create action instance.

        Parameters
        ----------
        card : Card, optional
            The Card involved in the Action if appropriate, by default None
        marriage : Marriage, optional
            The Marriage involved in the Action if appropriate, by default None
        swap_trump : bool, optional
            True if the action is swapping trumps, by default False
        close_deck : bool, optional
            True if the action is closing the deck, by default False
        """
        self.card = card
        self.marriage = marriage
        self.swap_trump = swap_trump
        self.close_deck = close_deck

    def _nice_str(self) -> str:
        return_string = ''
        if self.swap_trump:
            return_string = 'Swap trump '

        if self.close_deck:
            return_string += 'Close Deck '

        if self.marriage is not None:
            return_string += 'Play marriage '

        if self.card is not None:
            return_string += 'Play card ' + str(self.card)

        return return_string

    def __repr__(self) -> str:
        """String rep."""
        return self._nice_str()

    def __str__(self) -> str:
        """String rep."""
        return self._nice_str()

    def __eq__(self, other: Action) -> bool:
        """Overrides the default implementation."""
        if isinstance(other, Action):
            return self.card == other.card and self.marriage == other.marriage and \
                self.swap_trump == other.swap_trump and self.close_deck == other.close_deck
