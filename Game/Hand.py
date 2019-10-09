from Game.Card import Card
from Game.Marriage import Marriage

class Hand(list):

    def __init__(self):
        super().__init__()

    # Returns the suits of available marriages and a boolean
    # ToDo: There's probably a sexy pythonic way to do this with comprehension/filters/maps
    def available_marriages(self, player):

        # Keep track of a running count of matches for each suit
        dic = {Card.Diamonds: [],
               Card.Clubs: [],
               Card.Hearts: [],
               Card.Spades: []}

        # First add queens, then kings. This guarantees order later
        for card in self:
            if card.value == Card.Queen:
                dic[card.suit].append(card)

        for card in self:
            if card.value == Card.King:
                dic[card.suit].append(card)

        # Any dic item with a count of 2 is marriage
        result = []
        for suit, cards in dic.items():
            if len(cards) == 2:
                result.append(Marriage(player, cards[0], cards[1]))

        return len(result) > 0, result

    # Returns true if card exists in hand
    def has_card(self, suit, value):
        return_value = False
        for i, card in enumerate(self):
            if card.suit == suit and card.value == value:
                return_value = True
                break
        return return_value

    # Assume caller knows this card exists
    # Throw exception if it doesn't
    def pop_card(self, suit, value):
        card = None
        for i, card in enumerate(self):
            if card.suit == suit and card.value == value:
                card = self.pop(i)
                break
        if card is None:
            raise Exception("Cannot pop card - doesn't exist")
        return card

    def cards_of_same_suit(self, suit, greater_than=0):
        return_list = []
        for card in self:
            if card.suit == suit and card.value > greater_than:
                return_list.append(card)
        return return_list
