"""Card Deck Class"""
import random
from Game.Card import Card


class Deck(list):
    def __init__(self):

        super().__init__()

        for cardKey in Card.Values.keys():
            for suitKey in Card.Suits.keys():
                self.append(Card(suitKey, cardKey))

    def shuffle(self):
        random.shuffle(self)
