import random

import pytest

from schnapsen.ai.random_player import RandomPlayer
from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.deck import Deck
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player


def test_play_automated():
    # Play some games at random. 10 games seems to cover almost all game actions and finds glaring syntax bugs.
    random.seed(0)

    match_controller = MatchController(player_a=RandomPlayer("Randy1"), player_b=RandomPlayer("Randy2"))
    for _ in range(10):
        match_controller.play_automated_match()
    assert isinstance(match_controller.round_state.round_winner, Player)


def test_regression():
    """Play through a fixed game checking key abilities."""
    random.seed(0)

    match_controller = MatchController(player_a=Player(name="player_a", automated=False),
                                       player_b=Player(name="player_b", automated=False))

    match_controller.new_match()
    assert match_controller.match_state.player_a_match_points == 0
    assert match_controller.match_state.player_b_match_points == 0

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

    match_controller.new_round(deck)
    player_1 = match_controller.round_state.active_player
    player_2 = match_controller.get_other_player(player_1)
    # Test the deal
    assert player_1.hand == [
        Card(Suit.DIAMOND, Value.ACE), Card(Suit.SPADE, Value.KING), Card(Suit.SPADE, Value.QUEEN),
        Card(Suit.HEART, Value.ACE), Card(Suit.HEART, Value.TEN)]
    assert player_2.hand == [
        Card(Suit.CLUB, Value.TEN), Card(Suit.CLUB, Value.KING), Card(Suit.CLUB, Value.QUEEN),
        Card(Suit.DIAMOND, Value.TEN), Card(Suit.SPADE, Value.ACE)]
    assert match_controller.round_state.trump_card == Card(Suit.SPADE, Value.TEN)
    assert len(match_controller._deck) == 9

    # Now start performing actions
    match_controller.do_next_action(Action(card=Card(Suit.DIAMOND, Value.ACE)))
    assert Card(Suit.DIAMOND, Value.ACE) not in player_1.hand
    match_controller.do_next_action(Action(card=Card(Suit.SPADE, Value.ACE)))
    # Trump beats non-trump
    assert match_controller.round_state.hand_winner == player_2
    # Winner picks up first, so gets the queen of diamods
    assert Card(Suit.DIAMOND, Value.QUEEN) in player_2.hand
    assert Card(Suit.DIAMOND, Value.JACK) in player_1.hand
    assert player_2.round_points == 22  # Two aces!

    # What happens if we try and lead the wrong player's action.
    with pytest.raises(ValueError, match="not in hand"):
        match_controller.do_next_action(Action(card=Card(Suit.SPADE, Value.KING)))

    # TODO: Trump Marriage
    # TODO: Normal Marriage
    # TODO: Swap Trump
    # TODO: Close Deck
    # TODO: Various match point scenarios
