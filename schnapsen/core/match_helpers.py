"""Module for Game helpers."""
from dataclasses import dataclass
import logging

from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player


@dataclass
class Results():
    """Simple structure for storing match results."""
    player1: Player
    player2: Player
    number_of_matches_played: int
    player1_wins: int
    player2_wins: int
    winner: Player


def play_automated_matches(game: MatchController, number_of_matches: int = 999) -> Results:
    """Play games automatically (assuming players are both automatable).

    Parameters
    ----------
    game : Game
        The Game instance to use.
    number_of_matches : int, optional
        The number of games to play through, by default 999 (odd to avoid ties)
    """
    logger = logging.getLogger()

    player1 = game._player_a
    player2 = game._player_b
    player1_wins = 0
    player2_wins = 0

    for _ in range(number_of_matches):
        game.play_automated_match()

        if game.match_winner is player1:
            player1_wins += 1
        else:
            player2_wins += 1

        logger.debug('%s vs %s, winner is %s. Running Total: %i:%i',
                     player1.name, player2.name, game.match_winner.name, player1_wins, player2_wins)

    logger.info('%s vs %s. %i:%i', player1.name, player2.name, player1_wins, player2_wins)

    return Results(player1=player1, player2=player2, number_of_matches_played=number_of_matches,
                   player1_wins=player1_wins, player2_wins=player2_wins,
                   winner=player1 if player1_wins > player2_wins else player2)
