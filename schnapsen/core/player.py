"""Parent player class.

All player implementation should inherit from this and simply implement the select_action method to notify the game
of what action it would take from a given state.
"""
from __future__ import annotations

from typing import Callable, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:   # Needed only for type hints and avoids circular dependencies.
    from schnapsen.core.action import Action
    from schnapsen.core.state import MatchState


class Player:
    """Parent player class.

    This should generally be inherited from.
    """

    def __init__(self, name: str, automated: Optional[bool] = True,
                 requires_model_load: Optional[bool] = False) -> None:
        """Create a Player instance.

        Args:
            name (str): Print friendly name.
            automated (Optional[bool], optional): True if AI/Bot, False otherwise. Defaults to True.
            requires_model_load (Optional[bool], optional): If True attempt to load model before using (e.g. for
                AI models). Defaults to False.
        """
        # Not critical but useful for logging/UI.
        self.name = name
        # Used for AI players to progress actions automatically when possible.
        self.automated = automated
        # Used for model based players alongside a load_model method on the player.
        # TODO: make ModelPlayer child of the Player object and replace this bool with a simple isinstance check.
        self.requires_model_load = requires_model_load
        # Track the player's current hand. This could/should also be tracked by the match controller but it's cleaner
        # for a player to own his hand.
        self.declare_win_callback: Callable = None  # Assigned by game controller. This is used but isn't necessary

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> Action:     # noqa:U100
        """Method for selecting Player Action.

        A child player class must implement this method and return an action. The player or some other controller
        should probably first ask for the legal actions to evaluated (but an illegal action is handled by the
        game controller).

        Args:
            state (MatchState): The current match state. In practice this gives the player the opponents hand. For AI
                implementations/bots, we choose to ignore this information.
            legal_actions (List[Action]): A set of legal actions provided by the match controller.

        Raises:
            NotImplementedError: If a child object fails to implement this necessary method.

        Returns:    # noqa: DAR202
            Action: The selected game Action.
        """
        raise NotImplementedError('Must be implemented by child')

    def _print_str_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        """String represenation.

        Returns:
            str: Player name.
        """
        return self._print_str_name()

    def __str__(self) -> str:
        """String represenation.

        Returns:
            str: Player name.
        """
        return self._print_str_name()
