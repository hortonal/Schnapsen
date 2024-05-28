"""Module for handling single Marriage instances."""
from __future__ import annotations

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value


class Marriage:
    """Marriage class.

    This is when a queen and king of the same suit are declared. This is worth 20 points if a non trump is played. and
    40 points if they of the trump suit.
    """

    def __init__(self, queen: Card, king: Card) -> None:
        """Create Marriage instance.

        Args:
            queen (Card): The Queen card of the Marriage.
            king (Card): The King card of the Marriage.

        Raises:
            ValueError: If the Marriage is invalid for improper cards or suits.
        """
        if queen.suit != king.suit:
            raise ValueError('Invalid Marriage - suits not equal')
        if queen.value != Value.QUEEN:
            raise ValueError('Invalid marriage - queen not a queen')
        if king.value != Value.KING:
            raise ValueError('Invalid marriage - king not a king')

        self.suit = queen.suit  # Take suit from a card arbitrarily as we've already checked both are the same suit.
        self.queen = queen
        self.king = king
        self.cards = [queen, king]  # Purely for convenience

        self.points = 0  # Set by game
        self.points_awarded = False

    def notify_card_played(self, card: Card) -> None:
        """Notify object that a card has been played.

        Args:
            card (Card): The Card being played.

        Raises:
            ValueError: If card not in Marriage.
        """
        card_found = False
        for i, iter_card in enumerate(self.cards):
            if iter_card == card:
                card_found = True
                self.cards.pop(i)
                break

        if not card_found:
            raise ValueError('Invalid card given to marriage')

    def card_in_marriage(self, card: Card) -> bool:
        """Check if card is in Marriage.

        Args:
            card (Card): Card to check.

        Returns:
            bool: True if card is in marriage, False otherwise.
        """
        return card in self.cards

    def set_points(self, trump_suit: Suit) -> None:
        """Determine and set the value of the Marriage.

        Args:
            trump_suit (Suit): The trump suit to compare against.
        """
        if self.suit == trump_suit:
            self.points = 40
        else:
            self.points = 20

    def __eq__(self, other: Marriage) -> bool:
        """Test Marriage for equivalence.

        Args:
            other (Marriage): Marriage to check against.

        Returns:
            bool: True if Marriage instance is equivalent.
        """
        if isinstance(other, Marriage):
            return self.queen == other.queen and self.king == other.king
