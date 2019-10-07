from unittest import TestCase


class TestHandHelpers(TestCase):
    def test_available_marriages_inorder(self):
        from Game.Deck import Card
        from Game.HandHelpers import HandHelpers

        hand = [Card(0, 2),
                Card(0, 3),
                Card(0, 4),
                Card(0, 10),
                Card(0, 11)]

        expected_marriage = [0]

        result, marriage = HandHelpers.available_marriages(hand)

        self.assertEqual(result, True)
        self.assertEqual(expected_marriage, marriage)


    def test_available_marriages_out_of_order(self):
        from Game.Deck import Card
        from Game.HandHelpers import HandHelpers

        hand = [Card(0, 2),
                Card(0, 4),
                Card(0, 10),
                Card(0, 11),
                Card(0, 3)]

        expected_marriage = [0]

        result, marriage = HandHelpers.available_marriages(hand)

        self.assertEqual(result, True)
        self.assertEqual(expected_marriage, marriage)

    def test_available_marriages_two_marriages(self):
        from Game.Deck import Card
        from Game.HandHelpers import HandHelpers

        hand = [Card(2, 3),
                Card(0, 4),
                Card(1, 3),
                Card(1, 4),
                Card(0, 3)]

        expected_marriage = [0, 1]

        result, marriage = HandHelpers.available_marriages(hand)

        self.assertEqual(result, True)
        self.assertEqual(expected_marriage, marriage)

    def test_available_marriages_no_marriages(self):
        from Game.Deck import Card
        from Game.HandHelpers import HandHelpers

        hand = [Card(2, 2),
                Card(0, 4),
                Card(1, 3),
                Card(3, 4),
                Card(0, 2)]

        expected_marriage = []

        result, marriage = HandHelpers.available_marriages(hand)

        self.assertEqual(result, False)
        self.assertEqual(expected_marriage, marriage)