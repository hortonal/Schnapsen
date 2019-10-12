from Game.Player import Player
import random


# Pretty much the simplest/least intelligent player we could create
# This is out benchmark!
class RandomPlayer(Player):

    def __init__(self, name='Randy'):
        super().__init__(name)

    def select_action(self):
        return random.choice(self.legal_actions)