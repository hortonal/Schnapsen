"""Modules for a simple player implementation."""
from typing import List
import random

from schnapsen.core.action import Action
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


class RandomPlayer(Player):
    """The simplest/least intelligent player we could create. A good benchmark."""

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> Action:  # noqa:U100
        """Select Card (at random...).

        Returns
        -------
        Action
            The selected Action.
        """
        return random.choice(legal_actions)
