

class Marriage:

    def __init__(self, player, queen, king):
        if queen.suit != king.suit:
            raise Exception('Invalid Marriage - suits not equal')
        if queen.value != 3:
            raise Exception('Invalid marriage - queen not a queen')
        if king.value != 4:
            raise Exception('Invalid marriage - king not a king')

        self.player = player
        self.suit = queen.suit
        self.queen = queen
        self.king = king
        self.cards = [queen, king]  # Purely for convenience
        self.declared_but_not_played = True
        self.points = 0  # Set by game
        self.points_awarded = False

    # Expect card to be in marriage. Exception raised if not
    def notify_card_played(self, card):
        card_found = False
        for i, iter_card in enumerate(self.cards):
            if iter_card == card:
                card_found = True
                self.cards.pop(i)
                break

        if card_found:
            self.declared_but_not_played = False
        else:
            raise Exception('Invalid card given to marriage')

    def card_in_marriage(self, card):
        return card in self.cards

    def set_points(self, trump_suit):
        if self.suit == trump_suit:
            self.points = 40
        else:
            self.points = 20

    def __eq__(self, other):
        """Test only for card equivalence"""
        if isinstance(other, Marriage):
            return self.queen == other.queen and self.king == other.king
        return NotImplemented

    def __ne__(self, other):

        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented