import os

import torch

from schnapsen.ai.neural_network.simple_linear.io_helpers import IOHelpers
from schnapsen.core.player import Player


class NNSimpleLinearPlayer(Player):

    def __init__(self, name: str = 'Nanny_1') -> None:
        super().__init__(name, automated=True, requires_model_load=True)
        self.model = None
        self._file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  'trained_models', self.__class__.__name__ + '_model.txt')

    def select_action(self):
        inputs = IOHelpers.create_input_from_game_state(self.game, self)
        with torch.no_grad():
            _, action = IOHelpers.policy(self.model(inputs), self.game, self)
        return action

    def load_model(self):
        self.model = torch.load(self._file)

    def save_model(self):
        torch.save(self.model, self._file)
