"""Modules for a simple player implementation."""
import random

from schnapsen.core.action import Action
from schnapsen.core.player import Player


class RandomPlayer(Player):
    """The simplest/least intelligent player we could create. A good benchmark."""

    def select_action(self) -> Action:
        """Select Card (at random...).

        Returns
        -------
        Action
            The selected Action.
        """
        return random.choice(self.legal_actions)
