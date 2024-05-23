"""Module for match/round state classes."""
from dataclasses import dataclass

from schnapsen.core.card import Card
from schnapsen.core.player import Player


@dataclass
class PublicRoundState:
    """Container for state that can be shared with all players."""
    active_player: Player = None
    leading_card: Card = None
    following_card: Card = None
    leading_player: Player = None
    following_player: Player = None
    trump_card: Card = None
    deck_closed: bool = False
    hand_winner: Player = None
    deck_closed_by_player: bool = False
    deck_closer: Player = None
    deck_closer_points: int = 0
    deck_non_closer_points: int = 0
    have_round_winner: bool = False
    round_winner: Player = None
    round_loser: Player = None


@dataclass
class PublicMatchState:
    """Simple container for match level state."""
    round_point_limit: int
    match_point_limit: int
    player_a_match_points: int = 0
    player_b_match_points: int = 0
    player_with_1st_deal: Player = None
    player_with_2nd_deal: Player = None
    match_winner: Player = None
    have_match_winner: bool = False
