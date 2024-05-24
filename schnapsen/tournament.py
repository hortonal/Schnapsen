"""Main file (test for now)."""
from itertools import combinations

from schnapsen.ai.better_player import BetterPlayer
from schnapsen.ai.neural_network.simple_linear.nn_linear_player import NNSimpleLinearPlayer
from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core import match_helpers
from schnapsen.core.match_controller import MatchController
from schnapsen.logs import basic_logger


def run_tournament(number_of_matches_per_battle: int = 999) -> None:
    """Pit all players against each other.

    Parameters
    ----------
    number_of_matches_per_battle : int, optional
        The number of matches that each pair of players will play to decide a winner, by default 999
    """
    logger = basic_logger()
    logger.debug('Starting Aritificial Mortal Kombat')

    players = [
        BetterPlayer("Betty"),
        RandomPlayer("Randy"),
        NNSimpleLinearPlayer("NN_Simple")
    ]

    # Load models if required.
    for player in players:
        if player.requires_model_load:
            player.load_model()

    # Initialise results dicts.
    tournament_results = {player: 0 for player in players}

    # Now play all combinations of players
    for (player1, player2) in combinations(players, 2):
        game = MatchController(player1, player2)
        results = match_helpers.play_automated_matches(
            match_controller=game, number_of_matches=number_of_matches_per_battle)
        tournament_results[results.winner] = tournament_results[results.winner] + 1

    # And print out sorted results
    for player in sorted(tournament_results, key=tournament_results.get, reverse=True):
        logger.info("Tournament results: %s: %i wins", player, tournament_results[player])


if __name__ == "__main__":
    run_tournament()