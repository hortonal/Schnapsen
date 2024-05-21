from unittest import TestCase

from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.hand import Hand
from schnapsen.core.marriage import Marriage


class TestHand(TestCase):

    def test_cards_of_same_suit_all_same_suit(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.JACK))
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))
        hand.append(Card(Suit.DIAMOND, Value.KING))

        assert len(hand.cards_of_same_suit(Suit.DIAMOND)) == 3

    def test_cards_of_same_suit_1_greater_than(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.JACK))
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))
        card = Card(Suit.DIAMOND, Value.ACE)
        hand.append(card)

        assert hand.cards_of_same_suit(Suit.DIAMOND, Value.KING)[0] == card

    def test_cards_of_same_suit_no_mathces(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.JACK))
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))

        assert hand.cards_of_same_suit(Suit.CLUB, Value.ACE) == []

    def test_available_marriages_inorder(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.JACK))
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))
        hand.append(Card(Suit.DIAMOND, Value.KING))
        hand.append(Card(Suit.DIAMOND, Value.TEN))
        hand.append(Card(Suit.DIAMOND, Value.ACE))

        expected_marriage = Marriage(queen=Card(Suit.DIAMOND, Value.QUEEN), king=Card(Suit.DIAMOND, Value.KING))

        marriages = hand.available_marriages()

        assert len(marriages) == 1
        assert marriages[0] == expected_marriage

    def test_available_marriages_out_of_order(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.JACK))
        hand.append(Card(Suit.DIAMOND, Value.KING))
        hand.append(Card(Suit.DIAMOND, Value.ACE))
        hand.append(Card(Suit.DIAMOND, Value.TEN))
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))

        expected_marriage = Marriage(queen=Card(Suit.DIAMOND, Value.QUEEN), king=Card(Suit.DIAMOND, Value.KING))

        marriages = hand.available_marriages()
        assert marriages[0] == expected_marriage

    def test_available_marriages_two_marriages(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.QUEEN))
        hand.append(Card(Suit.DIAMOND, Value.KING))
        hand.append(Card(Suit.CLUB, Value.QUEEN))
        hand.append(Card(Suit.HEART, Value.KING))
        hand.append(Card(Suit.CLUB, Value.KING))

        marriages = hand.available_marriages()
        assert len(marriages) == 2
        assert marriages[0].queen == Card(Suit.DIAMOND, Value.QUEEN)
        assert marriages[1].king == Card(Suit.CLUB, Value.KING)

    def test_available_marriages_no_marriages(self):
        hand = Hand()
        hand.append(Card(Suit.DIAMOND, Value.TEN))
        hand.append(Card(Suit.DIAMOND, Value.KING))
        hand.append(Card(Suit.CLUB, Value.ACE))
        hand.append(Card(Suit.HEART, Value.KING))
        hand.append(Card(Suit.CLUB, Value.KING))

        expected_marriage = []
        marriages = hand.available_marriages()
        assert len(marriages) == 0
        assert expected_marriage == marriages
