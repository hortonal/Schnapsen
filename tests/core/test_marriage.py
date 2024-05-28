from unittest import TestCase

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.marriage import Marriage


class TestMarriage(TestCase):

    def test_set_points(self):
        marriage = Marriage(queen=Card(Suit.CLUB, Value.QUEEN),
                            king=Card(Suit.CLUB, Value.KING))

        marriage.set_points(trump_suit=Suit.CLUB)
        assert marriage.points == 40

        marriage.set_points(trump_suit=Suit.DIAMOND)
        assert marriage.points == 20
