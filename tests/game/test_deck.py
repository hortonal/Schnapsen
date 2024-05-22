from unittest import TestCase

from schnapsen.core.deck import Deck


class TestDeck(TestCase):
    def test_shuffle(self):
        deck = Deck()
        deck.shuffle()
        deck2 = Deck()
        deck2.shuffle()

        assert deck != deck2
