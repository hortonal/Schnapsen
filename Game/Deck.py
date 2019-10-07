"""Card Deck Class"""
import random



class Card:
    Values = {10: 'Ten', 2: 'Jack', 3: 'Queen', 4: 'King', 11: 'Ace'}
    Suits = {0: 'Spades', 1: 'Clubs', 2: 'Hearts', 3: 'Diamonds'}

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def _print_str_name(self):
        return self.Values[self.value] + ' ' + self.Suits[self.suit]

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()


class Deck(list):
    def __init__(self):

        super().__init__()

        for cardKey in Card.Values.keys():
            for suitKey in Card.Suits.keys():
                self.append(Card(suitKey, cardKey))

    def print(self):
        for card in self:
            print("Value: {value}, Suit: {suit}, IntValue: {valueInt}, IntSuit: {suitInt}"
                  .format(value=Card.Values[card.value], suit=Card.Suits[card.suit],
                          valueInt=card.value, suitInt=card.suit))

    def shuffle(self):
        random.shuffle(self)
