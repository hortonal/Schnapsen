"""Modules for a simple player implementation."""
import random
from typing import List

from schnapsen.core.action import Action
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


class RandomPlayer(Player):
    """The simplest/least intelligent player we could create. A good benchmark."""

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> Action:  # noqa:U100
        """Select and action at random.

        Args:
            state (MatchState): Not used.
            legal_actions (List[Action]): The valid actions to choose from at random.

        Returns:
            Action: Selected action.
        """
        return random.choice(legal_actions)
