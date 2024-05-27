from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core import match_helpers


def test_play_automated_games():
    match_helpers.play_automated_matches(
        player_1=RandomPlayer("Randy1"),
        player_2=RandomPlayer("Randy2"),
        number_of_matches=1)
