from unittest import TestCase


class TestHand(TestCase):

    def test_cards_of_same_suit_all_same_suit(self):
        from Game.Hand import Hand
        from Game.Card import Card

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Jack))
        hand.append(Card(Card.Diamonds, Card.Queen))
        hand.append(Card(Card.Diamonds, Card.King))

        self.assertEqual(len(hand.cards_of_same_suit(Card.Diamonds)), 3)

    def test_cards_of_same_suit_1_greater_than(self):
        from Game.Hand import Hand
        from Game.Card import Card

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Jack))
        hand.append(Card(Card.Diamonds, Card.Queen))
        card = Card(Card.Diamonds, Card.Ace)
        hand.append(card)

        self.assertEqual(
            hand.cards_of_same_suit(Card.Diamonds, Card.King)[0],
            card)

    def test_cards_of_same_suit_no_mathces(self):
        from Game.Hand import Hand
        from Game.Card import Card

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Jack))
        hand.append(Card(Card.Diamonds, Card.Queen))
        hand.append(Card(Card.Diamonds, Card.Queen))

        self.assertEqual(
            hand.cards_of_same_suit(Card.Clubs, Card.Ace),
            [])

    def test_available_marriages_inorder(self):
        from Game.Deck import Card
        from Game.Hand import Hand

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Jack))
        hand.append(Card(Card.Diamonds, Card.Queen))
        hand.append(Card(Card.Diamonds, Card.King))
        hand.append(Card(Card.Diamonds, Card.Ten))
        hand.append(Card(Card.Diamonds, Card.Ace))

        expected_marriage = [Card.Diamonds]

        result, marriage = hand.available_marriages()

        self.assertEqual(result, True)
        self.assertEqual(expected_marriage, marriage)

    def test_available_marriages_out_of_order(self):
        from Game.Deck import Card
        from Game.Hand import Hand

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Jack))
        hand.append(Card(Card.Diamonds, Card.King))
        hand.append(Card(Card.Diamonds, Card.Ace))
        hand.append(Card(Card.Diamonds, Card.Ten))
        hand.append(Card(Card.Diamonds, Card.Queen))

        expected_marriage = [Card.Diamonds]

        result, marriage = hand.available_marriages()

        self.assertEqual(result, True)
        self.assertEqual(expected_marriage, marriage)

    def test_available_marriages_two_marriages(self):
        from Game.Deck import Card
        from Game.Hand import Hand

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Queen))
        hand.append(Card(Card.Diamonds, Card.King))
        hand.append(Card(Card.Clubs, Card.Queen))
        hand.append(Card(Card.Hearts, Card.King))
        hand.append(Card(Card.Clubs, Card.King))

        expected_marriage = [Card.Diamonds, Card.Clubs]

        result, marriage = hand.available_marriages()

        self.assertEqual(result, True)
        self.assertEqual(expected_marriage, marriage)

    def test_available_marriages_no_marriages(self):
        from Game.Deck import Card
        from Game.Hand import Hand

        hand = Hand()
        hand.append(Card(Card.Diamonds, Card.Ten))
        hand.append(Card(Card.Diamonds, Card.King))
        hand.append(Card(Card.Clubs, Card.Ace))
        hand.append(Card(Card.Hearts, Card.King))
        hand.append(Card(Card.Clubs, Card.King))

        expected_marriage = []

        result, marriage = hand.available_marriages()

        self.assertEqual(result, False)
        self.assertEqual(expected_marriage, marriage)
