from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core import match_helpers
from schnapsen.core.match_controller import MatchController


def test_play_automated_games():
    game = MatchController(RandomPlayer("Randy1"), RandomPlayer("Randy2"), match_point_limit=1)
    match_helpers.play_automated_matches(game=game, number_of_matches=1)
