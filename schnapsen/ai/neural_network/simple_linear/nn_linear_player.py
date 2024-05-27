"""Simple player nueral network player module."""
import os
from typing import List

import torch

from schnapsen.ai.neural_network.simple_linear.io_helpers import IOHelpers
from schnapsen.core.action import Action
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


class NNSimpleLinearPlayer(Player):
    """Simple player nueral network player implementation."""

    def __init__(self, name: str = 'Nanny') -> None:
        """Initialise Player object.

        Parameters
        ----------
        name : str, optional
            Sets a default name for the NN player, by default 'Nanny'
        """
        super().__init__(name, automated=True, requires_model_load=True)
        self.model = None
        self._file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  'trained_models', self.__class__.__name__ + '_model.bin')

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> None:
        """Implements requisite action selection method from parent object."""
        inputs = IOHelpers.create_input_from_game_state(state)
        # no_grad disables tracking of gradients which speeds up model call.
        with torch.no_grad():
            _, action = IOHelpers.policy(self.model(inputs), state)
        return action

    def load_model(self) -> None:
        """Load a saved model from file."""
        self.model = torch.load(self._file)

    def save_model(self) -> None:
        """Save an existing model to file."""
        torch.save(self.model, self._file)
