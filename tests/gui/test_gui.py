from unittest.mock import MagicMock

from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.gui import gui


def test_gui():
    """This simple placeholder at least imports and runs most basic gui code."""
    mock_controller = MagicMock(spec=MatchController)
    mock_player = MagicMock(spec=Player)
    test_app = gui.GUI(match_controller=mock_controller, human_player=mock_player)
    assert test_app

# TODO: add unit/functional tests
