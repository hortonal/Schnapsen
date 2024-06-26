"""Module for match/round state classes."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, List, Tuple

from schnapsen.core.card import Card
from schnapsen.core.deck import Deck
from schnapsen.core.hand import Hand
from schnapsen.core.player import Player


@dataclass
class PlayerState:
    """Container for each player specific state."""
    round_points: int = 0
    match_points: int = 0
    hand: Hand = None
    cards_won: List[Card] = None
    match_points_on_offer = 1


@dataclass
class MatchState:
    """Container for all current match state."""
    # Match players
    players: Tuple[Player, Player]
    # Round specific state
    deck: Deck

    player_states: Dict[Player, PlayerState] = None  # set in post init
    active_player: Player = None
    marriages_info = {}

    # Table State
    leading_card: Card = None
    following_card: Card = None
    trump_card: Card = None
    deck_closed: bool = False
    hand_winner: Player = None
    leading_player: Player = None

    deck_closer: Player = None
    round_winner: Player = None
    round_winner_match_points: int = None    # Specifically holds the last match points awards

    # Game rules
    round_point_limit: int = 66
    match_point_limit: int = 7

    # Match level state
    player_with_1st_deal: Player = None
    match_winner: Player = None

    def __post_init__(self) -> None:
        """Initialise child state objects."""
        self.player_states = {}
        for player in self.players:
            self.player_states[player] = PlayerState()

    def get_other_player(self, player: Player) -> Player:
        """Returns the second Player instance, assuming only 2 players.

        Args:
            player (Player): The first Player instance.

        Returns:
            Player: The second Player instance.
        """
        return self.players[1] if player is self.players[0] else self.players[0]

    def copy(self) -> MatchState:
        """Deep copy the current game state.

        Returns:
            MatchState: New state copy.
        """
        return deepcopy(self)

    def normalised_value_is_terminal(self) -> Tuple[float, bool]:
        """Get a normalised state value and terminal state from active player's perspective.

        This is explicitly for a round only.

        Returns:
            Tuple[float, bool]: The match value, True if terminal
        """
        is_terminal = self.round_winner is not None
        if is_terminal:
            value = self.round_winner_match_points / 3
            return value, True
        else:
            return 0, False
