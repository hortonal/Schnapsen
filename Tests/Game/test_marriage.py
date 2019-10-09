from unittest import TestCase


class TestMarriage(TestCase):
    def test_PlayCard_play_queen(self):
        from Game.Marriage import Marriage
        from Game.Deck import Card

        queen_card = Card(0, 3)
        king_card = Card(0, 4)
        marriage = Marriage(None, queen_card, king_card, 0)

        marriage.notify_card_played(queen_card)
        self.assertEqual(marriage.cards, [king_card])
        self.assertEqual(marriage.declared_but_not_played, False)

    def test_PlayCard_play_king(self):
        from Game.Marriage import Marriage
        from Game.Deck import Card

        queen_card = Card(0, 3)
        king_card = Card(0, 4)
        marriage = Marriage(None, queen_card, king_card, 0)

        marriage.notify_card_played(king_card)
        self.assertEqual(marriage.cards, [queen_card])
        self.assertEqual(marriage.declared_but_not_played, False)

    def test_PlayCard_exception_on_unexpected_card(self):
        from Game.Marriage import Marriage
        from Game.Deck import Card

        queen_card = Card(0, 3)
        king_card = Card(0, 4)
        other = Card(0, 2)
        marriage = Marriage(None, queen_card, king_card, 0)

        self.assertRaises(Exception, marriage.notify_card_played, other)
