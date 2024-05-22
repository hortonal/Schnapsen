import random

from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player


def test_play_automated():
    random.seed(0)

    game = MatchController(player_a=RandomPlayer("Randy1"), player_b=RandomPlayer("Randy2"))
    # 10 random games seems to cover most game actions.
    for _ in range(10):
        game.play_automated_match()
    assert isinstance(game.game_winner, Player)
