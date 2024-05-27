"""Module for human player instance."""
from typing import Optional

from schnapsen.core.player import Player


class HumanPlayer(Player):
    """Non-automated player instance."""

    def __init__(self, name: Optional[str] = 'Huuuman') -> None:
        """Create a human player.

        Args:
            name (Optional[str]): Name of the player. Defaults to 'Huuuman'.
        """
        super().__init__(name=name, automated=False)
