from unittest.mock import MagicMock

from schnapsen.core.player import Player
from schnapsen.gui import gui


def test_gui():
    """This simple placeholder at least imports and runs most basic gui code."""
    mock_player = MagicMock(spec=Player)
    test_app = gui.GUI(human_player=mock_player, opponent=mock_player)
    assert test_app

# TODO: add unit/functional tests. This is the biggest source of "untested" lines in this repo.
