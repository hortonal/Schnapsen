from unittest import TestCase


class TestDeck(TestCase):
    def test_shuffle(self):
        from Game.Deck import Deck
        deck = Deck()
        deck.shuffle()
        deck2 = Deck()
        deck2.shuffle()

        self.assertNotEqual(deck, deck2)
