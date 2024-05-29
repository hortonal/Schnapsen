"""Handle conversion of game state to AI ready objects."""
from typing import Dict

import torch

from schnapsen.ai.neural_network.card_input import CardInput
from schnapsen.core.actions import ALL_GAME_ACTIONS
from schnapsen.core.card import Card
from schnapsen.core.card import Suit
from schnapsen.core.card import Value
from schnapsen.core.marriage import Marriage
from schnapsen.core.match_controller import MatchController
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


class IOHelpers:

    deck_closed_key = -1
    my_points_to_victory_key = -2
    my_unearned_points_key = -3
    opponents_points_to_victory_key = -4
    opponents_unearned_points_key = -5
    match_points_on_offer_to_me_key = -6
    match_points_on_offer_to_opponent_key = -7

    # Make a static list of actions for performance.
    # These should be used for reference only and not passed to the game engine
    d_marriage = Marriage(Card(Suit.DIAMOND, Value.QUEEN), Card(Suit.DIAMOND, Value.KING))
    s_marriage = Marriage(Card(Suit.SPADE, Value.QUEEN), Card(Suit.SPADE, Value.KING))
    h_marriage = Marriage(Card(Suit.HEART, Value.QUEEN), Card(Suit.HEART, Value.KING))
    c_marriage = Marriage(Card(Suit.CLUB, Value.QUEEN), Card(Suit.CLUB, Value.KING))

    # Cards
    @staticmethod
    def card_key(suit, value):
        # Build a unique int for quicker indexing (hopefully?)]
        # maybe build these upfront for performance?
        # e.g. 0 * 20 + 11 for Ace of spades
        # 1 * 20 + 2 = 22 for Jack of clubs
        return suit * 20 + value

    @staticmethod
    def create_input_from_game_state(state: MatchState) -> Dict:

        # Make a flat vector of cards each with a state?
        # Make a convolution grd?
        # Make something else
        #
        #   I have:
        #       20 cards
        #           1 trump card
        #           up to 5 in a players hand
        #           up to 18 won by a player
        #           up to 5 that I know are in the opponents hand
        #           Deck closed
        #           Which marriages could be available
        #           Un-beatable cards (?)
        #
        # Option 1:
        #   Vector for each of the 20 cards:
        #       Value           (int) ??
        #       Suit            (int) ??
        #       my hand         (binary)
        #       their hand      (binary)
        #       won by me       (binary)
        #       won by them     (binary)
        #       Is trump        (binary)
        #
        #   Trump suit          (int)
        #   Deck is closed      (binary)
        #   My pts to victory   (int)
        #   My unearned pts     (int)
        #   Opp pts to victory  (int)
        #   Opp unearned pts    (int)
        #
        #                       20 * 6 + 6 = 126 inputs. Not too bad

        inputs = {}
        player_state = state.player_states[state.active_player]
        opponent_state = state.player_states[state.get_other_player(state.active_player)]

        for suit in [Suit.DIAMOND, Suit.CLUB, Suit.SPADE, Suit.HEART]:
            for value in Value:
                inputs[IOHelpers.card_key(suit, value)] = CardInput(suit, value)

        for card in player_state.hand:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.in_my_hand = True

        # # for card in game.get_other_player(player).hand - would be cheating!! Would be an interesting test, though!
        # # As is, this handles cases where we know unequivocally that they have part of a marriage or the last 5 cards
        # # of the deck
        # TODO This was removed with the match state reworking. Would be good to handle this again.
        # for card in player.opponent_hand:
        #     card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
        #     card_input.in_opponent_hand = True

        for card in player_state.cards_won:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.won_by_me = True

        for card in opponent_state.cards_won:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.won_by_opponent = True

        lead_card = state.leading_card
        if lead_card is not None:
            inputs[IOHelpers.card_key(lead_card.suit, lead_card.value)].is_leading_card = True

        inputs[IOHelpers.deck_closed_key] = 1 if state.deck_closed else 0
        inputs[IOHelpers.my_points_to_victory_key] = state.match_point_limit - player_state.round_points
        inputs[IOHelpers.my_unearned_points_key] = 0
        inputs[IOHelpers.opponents_points_to_victory_key] = state.match_point_limit - opponent_state.round_points
        inputs[IOHelpers.opponents_unearned_points_key] = 0
        inputs[IOHelpers.match_points_on_offer_to_me_key] = 0
        inputs[IOHelpers.match_points_on_offer_to_opponent_key] = 0

        # I now have all the data I need. Now to convert it into something useful.
        # Flat vector is simplest. Or do some clever CNN?

        # Simple flat vector to start with...
        return IOHelpers.__create_flat_tensor(inputs, state)

    @staticmethod
    def __create_flat_tensor(inputs: Dict[int, int], state: MatchState):
        # (With performance in mind, it'd be better to create the
        # tensor elements directly instead of using a list but hey...)
        input_vector = []
        for item in inputs.values():
            if isinstance(item, CardInput):
                input_vector.append(item.suit / 3)  # Normalise suit value
                input_vector.append(item.value / state.round_point_limit)  # Normalise card value to fraction of a game
                input_vector.append(item.in_my_hand)
                input_vector.append(item.in_opponent_hand)
                input_vector.append(item.won_by_me)
                input_vector.append(item.won_by_opponent)
                input_vector.append(item.is_leading_card)

        input_vector.append(inputs[IOHelpers.deck_closed_key])
        input_vector.append(inputs[IOHelpers.my_points_to_victory_key] / state.round_point_limit)
        input_vector.append(inputs[IOHelpers.opponents_points_to_victory_key] / state.round_point_limit)

        # input_vector.append(inputs[IOHelpers.my_unearned_points_key] / game.match_state.round_point_limit)
        # input_vector.append(inputs[IOHelpers.opponents_unearned_points_key] / game.match_state.round_point_limit)
        # input_vector.append(inputs[IOHelpers.match_points_on_offer_to_me_key])
        # input_vector.append(inputs[IOHelpers.match_points_on_offer_to_opponent_key])

        return torch.tensor(input_vector, dtype=torch.float)

    @staticmethod
    def check_action_legal(i, legal_actions):
        is_legal = False
        return_action = None

        output_action = ALL_GAME_ACTIONS[i]
        for action in legal_actions:
            if output_action == action:
                is_legal = True
                return_action = action
                break

        return is_legal, return_action

    @staticmethod
    def get_legal_actions(state: MatchState) -> torch.tensor:
        match_controller = MatchController()
        legal_actions = match_controller.get_valid_actions(state=state)
        legal_moves = []
        actions = []
        for i in range(len(ALL_GAME_ACTIONS)):
            is_legal, action = IOHelpers.check_action_legal(i, legal_actions)
            legal_moves.append(is_legal)
            actions.append(action)
        return torch.tensor(legal_moves, dtype=torch.bool), actions

    # Pick an action based on values. Ignore illegal moves
    # convert it into an actual action
    @staticmethod
    def policy(q_values, state: MatchState):
        legal_mask, legal_actions = IOHelpers.get_legal_actions(state)

        # set all illegal moves to a quality value of -100
        # this is more than a little hacky but in reality filters out illegal moves sufficiently
        q_values[~legal_mask] = -100

        _, indices = q_values.max(0)

        selected_action = legal_actions[indices]
        selected_action_id = indices.unsqueeze(0)

        if selected_action is None:
            raise ValueError('No valid action found')

        return selected_action_id, selected_action

    # 3D policy implementation
    @staticmethod
    def policy_batch(q_values, legal_mask):

        # this is hack as hell but works.
        q_values[~legal_mask] = -100
        return q_values.max(1)[0].detach()
