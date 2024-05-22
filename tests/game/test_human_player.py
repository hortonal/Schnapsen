from schnapsen.core.human_player import HumanPlayer
from schnapsen.core.player import Player


def test_human_player():
    player = HumanPlayer("Dave")
    assert isinstance(player, Player)
    assert player.name == "Dave"
