import random
from unittest import TestCase

from schnapsen.core.deck import Deck


class TestDeck(TestCase):
    def test_shuffle(self):
        random.seed(0)
        deck_1 = Deck()
        deck_2 = Deck()

        assert deck_1 != deck_2
