"""Parent player class.

All player implementation should inherit from this and simply implement the
_select_action method to notify the game what it's doing. All other player logic
and game controller interaction handled in this class.
"""
from __future__ import annotations

from typing import Callable, List

from schnapsen.core.action import Action


class Player:
    """Parent player class.

    This should generally be inherited from.
    """

    def __init__(self, name: str, automated: bool = True, requires_model_load: bool = False) -> None:
        """Initialise Player.

        Parameters
        ----------
        name : str
            Print friendly name.
        automated : bool, optional
            True if AI/Bot, False otherwise, by default True
        requires_model_load : bool, optional
            If True attempt to load model before using (e.g. for AI models), by default False
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

    def select_action(self, legal_actions: List[Action]) -> Action:     # noqa:U100
        """Method for selecting Player Action.

        A child player class must implement this method and return an action. The player or some other controller
        should probably first ask for the legal actions to evaluated (but an illegal action is handled by the
        game controller).

        Parameters
        ----------
        legal_actions : List[Action]
            A set of legal actions provided by the match controller.

        Returns
        -------
        Action
            The selected game Action.

        Raises
        ------
        NotImplementedError
            If a child object fails to implement this necessary method.
        """
        raise NotImplementedError('Must be implemented by child')

    def _print_str_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        """String format.

        Returns
        -------
        str
            Object as str.
        """
        return self._print_str_name()

    def __str__(self) -> str:
        """String format.

        Returns
        -------
        str
            Object as str.
        """
        return self._print_str_name()
