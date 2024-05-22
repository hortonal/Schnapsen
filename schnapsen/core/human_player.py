"""Module for human player instance."""
from schnapsen.core.player import Player


class HumanPlayer(Player):
    """Non-automated player instance."""

    def __init__(self, name: str = 'Huuuman') -> None:
        """Instantiate player object."""
        super().__init__(name=name, automated=False)
