"""Module for Game helpers."""
from dataclasses import dataclass
import logging
from typing import Optional

from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


@dataclass
class Results():
    """Simple structure for storing match results."""
    player1: Player
    player2: Player
    number_of_matches_played: int
    player1_wins: int
    player2_wins: int
    winner: Player

    def __str__(self) -> str:
        """String represenation of results.

        Returns:
            str: Compiled string.
        """
        return f"{self.player1} {self.player1_wins} : {self.player2} {self.player2_wins}"


def play_automated_match(player_1: Player, player_2: Player) -> MatchState:
    """Progress match/game state automatically.

    Args:
        player_1 (Player): First player.
        player_2 (Player): Second player.

    Returns:
        MatchState: Match state including results.
    """
    controller = MatchController()
    state = controller.get_new_match_state(player_1=player_1, player_2=player_2)
    while state.match_winner is None:
        controller.reset_round_state(state=state)
        while state.round_winner is None:
            controller.progress_automated_actions(state)
    return state


def play_automated_matches(player_1: Player, player_2: Player, number_of_matches: Optional[int] = 999) -> Results:
    """Play games automatically (assuming players are both automatable).

    Args:
        player_1 (Player): First player.
        player_2 (Player): Second player.
        number_of_matches (Optional[int], optional): The number of games to play through, by default 999 (odd to avoid
            ties). Defaults to 999.

    Returns:
        Results: _description_
    """
    logger = logging.getLogger()

    player_1_wins = 0
    player_2_wins = 0

    for _ in range(number_of_matches):
        state = play_automated_match(player_1=player_1, player_2=player_2)

        if state.match_winner is player_1:
            player_1_wins += 1
        else:
            player_2_wins += 1

        logger.debug(
            '%s vs %s, winner is %s. Running Total: %i:%i',
            player_1.name, player_2.name, state.match_winner.name, player_1_wins, player_2_wins)

    logger.info('%s vs %s. %i:%i', player_1.name, player_2.name, player_1_wins, player_2_wins)

    return Results(player1=player_1, player2=player_2, number_of_matches_played=number_of_matches,
                   player1_wins=player_1_wins, player2_wins=player_2_wins,
                   winner=player_1 if player_1_wins > player_2_wins else player_2)
