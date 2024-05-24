from unittest import TestCase

import pytest

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.marriage import Marriage


class TestMarriage(TestCase):

    def test_play_queen(self):
        queen_card = Card(Suit.CLUB, Value.QUEEN)
        king_card = Card(Suit.CLUB, Value.KING)
        marriage = Marriage(queen_card, king_card)

        marriage.notify_card_played(queen_card)
        assert marriage.cards == [king_card]
        assert not marriage.declared_but_not_played

    def test_play_king(self):
        queen_card = Card(0, 3)
        king_card = Card(0, 4)
        marriage = Marriage(queen_card, king_card)

        marriage.notify_card_played(king_card)
        assert marriage.cards == [queen_card]
        assert not marriage.declared_but_not_played

    def test_exception_on_unexpected_card(self):
        queen_card = Card(0, 3)
        king_card = Card(0, 4)
        other = Card(0, 2)
        marriage = Marriage(queen_card, king_card)

        with pytest.raises(Exception, match="Invalid card"):
            marriage.notify_card_played(other)
