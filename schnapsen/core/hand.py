"""Module for player's hand related objects."""
from typing import List

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.marriage import Marriage


class Hand(list):
    """A hand is a list of cards with some extra validation and logic."""

    def available_marriages(self) -> List[Marriage]:
        """Determine available Marriages.

        Returns
        -------
        List[Marriage]
            Returns a list of available Marriage objects (or an empty list).
        """
        # Keep track of a running count of matches for each suit
        marriage_check_dict = {
            Suit.DIAMOND: [],
            Suit.CLUB: [],
            Suit.HEART: [],
            Suit.SPADE: []
        }

        # First add queens, then kings. Not hugely efficient but it guarantees order later.
        for card in self:
            if card.value == Value.QUEEN:
                marriage_check_dict[card.suit].append(card)

        for card in self:
            if card.value == Value.KING:
                marriage_check_dict[card.suit].append(card)

        # Any dic item with a count of 2 is marriage
        result = []
        for _, cards in marriage_check_dict.items():
            if len(cards) == 2:
                result.append(Marriage(queen=cards[0], king=cards[1]))

        return result

    def has_card(self, card: Card) -> bool:
        """Simple check if card is in the current hand.

        Parameters
        ----------
        card: Card
            Card to check.

        Returns
        -------
        bool
            True if card is present in hand; else False.
        """
        return any(card == card_in_hand for card_in_hand in self)

    def pop_card(self, card: Card) -> Card:
        """Remove card from hand.

        This assumes the card exists in the Hand.

        Parameters
        ----------
        card: Card
            Card to remove.

        Returns
        -------
        Card
            The removed Card.

        Raises
        ------
        ValueError
            If card is not present in hand.
        """
        selected_card = None
        for i, card_in_hand in enumerate(self):
            if card == card_in_hand:
                selected_card = self.pop(i)
                break
        if selected_card is None:
            raise ValueError("Card not in hand")
        return selected_card

    def cards_of_same_suit(self, suit: Suit, greater_than: Value = 0) -> List[Card]:
        """Get cards of a matching suit.

        Parameters
        ----------
        suit : Suit
            Suit to check.
        greater_than : Value, optional
            An optional value threshold (exclusive), by default 0

        Returns
        -------
        List[Card]
            The list of matching cards.
        """
        return_list = []
        for card in self:
            if card.suit == suit and card.value > greater_than:
                return_list.append(card)
        return return_list
