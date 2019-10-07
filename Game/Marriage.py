

class Marriage:

    def __init__(self, player, queen_card, king_card, value):
        self.player = player
        self.cards = [queen_card, king_card]
        self.declared_but_not_played = True
        self.value = value
        self.points_awarded = False

    # Expect card to be in marriage. Exception raised if not
    def play_card(self, card):
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
