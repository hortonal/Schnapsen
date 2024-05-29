import random

import pytest

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.deck import Deck
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player


def test_regression():
    """Play through a fixed game checking key abilities."""
    random.seed(0)

    match_controller = MatchController()
    state = match_controller.get_new_match_state(
        player_1=Player(name="player_a", automated=False),
        player_2=Player(name="player_b", automated=False))

    assert len(state.players) == 2

    deck = Deck()
    deck.clear()
    # Tests the deal and sets up the game.
    cards = [
        # Player 1 gets 3, give them a trump marriage
        Card(Suit.DIAMOND, Value.ACE), Card(Suit.SPADE, Value.KING), Card(Suit.SPADE, Value.QUEEN),
        # Player 2 gets 3, give them a normal marriage.
        Card(Suit.CLUB, Value.TEN), Card(Suit.CLUB, Value.KING), Card(Suit.CLUB, Value.QUEEN),
        # Trump
        Card(Suit.SPADE, Value.TEN),
        # Player 1
        Card(Suit.HEART, Value.ACE), Card(Suit.HEART, Value.TEN),
        # Player 2
        Card(Suit.DIAMOND, Value.TEN), Card(Suit.SPADE, Value.ACE),
        # Talon (rest of the deck) (9)
        Card(Suit.DIAMOND, Value.QUEEN), Card(Suit.DIAMOND, Value.JACK), Card(Suit.DIAMOND, Value.KING),
        Card(Suit.SPADE, Value.JACK), Card(Suit.CLUB, Value.ACE), Card(Suit.CLUB, Value.JACK),
        Card(Suit.HEART, Value.KING), Card(Suit.HEART, Value.QUEEN), Card(Suit.HEART, Value.JACK),
    ]
    cards.reverse()  # Cards are popped off the end so we reverse this list to behave as intended.
    deck.extend(cards)

    match_controller.reset_round_state(state=state, deck=deck)

    player_1 = state.active_player
    player_2 = state.get_other_player(player_1)
    player_1_state = state.player_states[player_1]
    player_2_state = state.player_states[player_2]
    player_1_hand = player_1_state.hand
    player_2_hand = player_2_state.hand

    # Test the deal
    assert player_1_hand == [
        Card(Suit.DIAMOND, Value.ACE), Card(Suit.SPADE, Value.KING), Card(Suit.SPADE, Value.QUEEN),
        Card(Suit.HEART, Value.ACE), Card(Suit.HEART, Value.TEN)]
    assert player_2_hand == [
        Card(Suit.CLUB, Value.TEN), Card(Suit.CLUB, Value.KING), Card(Suit.CLUB, Value.QUEEN),
        Card(Suit.DIAMOND, Value.TEN), Card(Suit.SPADE, Value.ACE)]
    assert state.trump_card == Card(Suit.SPADE, Value.TEN)
    assert len(state.deck) == 9

    # Now start performing actions
    match_controller.perform_action(state=state, action=Action(card=Card(Suit.DIAMOND, Value.ACE)))
    assert Card(Suit.DIAMOND, Value.ACE) not in player_1_hand
    match_controller.perform_action(state=state, action=Action(card=Card(Suit.SPADE, Value.ACE)))
    # Trump beats non-trump
    assert state.hand_winner == player_2
    # Winner picks up first, so gets the queen of diamods
    assert Card(Suit.DIAMOND, Value.QUEEN) in player_2_hand
    assert Card(Suit.DIAMOND, Value.JACK) in player_1_hand
    assert player_2_state.round_points == 22  # Two aces!

    # What happens if we try and lead the wrong player's action.
    with pytest.raises(ValueError, match="not in hand"):
        match_controller.perform_action(state=state, action=Action(card=Card(Suit.SPADE, Value.KING)))

    # TODO: Now game state is independent of the match controller the following action tests should be simple to break
    # into individual tests
    # Cards of same suit played
    # Cards of different suits played (no trump)
    # Trump Marriage
    # Normal Marriage
    # Swap Trump
    # Close Deck
    # The various match point scenarios
