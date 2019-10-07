import random
from Game.HandHelpers import HandHelpers
from Game.Player import Player

class SimplerPlayer(Player):

    def __init__(self, name='default'):
        super().__init__(name)

    def play(self, opponents_card=None):

        have_marriages, marriage_suits = HandHelpers.available_marriages(self.hand)
        leader = opponents_card is None

        # Noddy play the queen of a marriage if we have it
        if have_marriages and leader:
            marriage_suit = marriage_suits.pop()
            queen = None
            king = None
            for card in self.hand:
                if card.suit == marriage_suit:
                    if card.value == 3:
                        queen = card
                    elif card.value == 4:
                        king = card

            self.game.declare_marriage(self, queen, king)
            self.check_and_declare_win()

            for item, card in enumerate(self.hand):
                if card.value == 3 and card.suit == marriage_suit:
                    return_card = self.hand.pop(item)
                    break

        # Random pop
        else:
            return_card = self.hand.pop()

        return return_card



