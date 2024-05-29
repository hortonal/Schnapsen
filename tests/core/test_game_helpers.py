import random

from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core import match_helpers
from schnapsen.core.player import Player


def test_play_automated_game():
    # Play some games at random. 10 games seems to cover almost all game actions and finds glaring syntax bugs.
    random.seed(0)

    for _ in range(10):
        state = match_helpers.play_automated_match(player_1=RandomPlayer("Randy1"), player_2=RandomPlayer("Randy2"))
        assert isinstance(state.match_winner, Player)


def test_play_automated_games():
    match_helpers.play_automated_matches(
        player_1=RandomPlayer("Randy1"),
        player_2=RandomPlayer("Randy2"),
        number_of_matches=1)
