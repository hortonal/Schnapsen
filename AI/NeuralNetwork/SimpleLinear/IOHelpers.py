from Game.Card import Card
from Game.Action import Action
from Game.Marriage import Marriage
from AI.NeuralNetwork.CardInput import CardInput
import torch
import random

class IOHelpers:

    deck_closed_key = -1
    my_points_to_victory_key = -2
    my_uneared_points_key = -3
    opponents_points_to_victory_key = -4
    opponents_uneared_points_key = -5
    match_points_on_offer_to_me_key = -6
    match_points_on_offer_to_opponent = -7

    # Make a static list of actions for performance. These should not be used for reference only and not passed to the game engine
    output_actions = {}
    d_marriage = Marriage(None, Card(Card.Diamonds, Card.Queen), Card(Card.Diamonds, Card.King))
    s_marriage = Marriage(None, Card(Card.Spades, Card.Queen), Card(Card.Spades, Card.King))
    h_marriage = Marriage(None, Card(Card.Hearts, Card.Queen), Card(Card.Hearts, Card.King))
    c_marriage = Marriage(None, Card(Card.Clubs, Card.Queen), Card(Card.Clubs, Card.King))
    # Cards
    output_actions[0] = Action(card=Card(Card.Diamonds, Card.Jack), marriage=None, swap_trump=False, close_deck=False)
    output_actions[1] = Action(card=Card(Card.Diamonds, Card.Queen), marriage=None, swap_trump=False, close_deck=False)
    output_actions[2] = Action(card=Card(Card.Diamonds, Card.King), marriage=None, swap_trump=False, close_deck=False)
    output_actions[3] = Action(card=Card(Card.Diamonds, Card.Ten), marriage=None, swap_trump=False, close_deck=False)
    output_actions[4] = Action(card=Card(Card.Diamonds, Card.Ace), marriage=None, swap_trump=False, close_deck=False)
    output_actions[5] = Action(card=Card(Card.Spades, Card.Jack), marriage=None, swap_trump=False, close_deck=False)
    output_actions[6] = Action(card=Card(Card.Spades, Card.Queen), marriage=None, swap_trump=False, close_deck=False)
    output_actions[7] = Action(card=Card(Card.Spades, Card.King), marriage=None, swap_trump=False, close_deck=False)
    output_actions[8] = Action(card=Card(Card.Spades, Card.Ten), marriage=None, swap_trump=False, close_deck=False)
    output_actions[9] = Action(card=Card(Card.Spades, Card.Ace), marriage=None, swap_trump=False, close_deck=False)
    output_actions[10] = Action(card=Card(Card.Hearts, Card.Jack), marriage=None, swap_trump=False, close_deck=False)
    output_actions[11] = Action(card=Card(Card.Hearts, Card.Queen), marriage=None, swap_trump=False, close_deck=False)
    output_actions[12] = Action(card=Card(Card.Hearts, Card.King), marriage=None, swap_trump=False, close_deck=False)
    output_actions[13] = Action(card=Card(Card.Hearts, Card.Ten), marriage=None, swap_trump=False, close_deck=False)
    output_actions[14] = Action(card=Card(Card.Hearts, Card.Ace), marriage=None, swap_trump=False, close_deck=False)
    output_actions[15] = Action(card=Card(Card.Clubs, Card.Jack), marriage=None, swap_trump=False, close_deck=False)
    output_actions[16] = Action(card=Card(Card.Clubs, Card.Queen), marriage=None, swap_trump=False, close_deck=False)
    output_actions[17] = Action(card=Card(Card.Clubs, Card.King), marriage=None, swap_trump=False, close_deck=False)
    output_actions[18] = Action(card=Card(Card.Clubs, Card.Ten), marriage=None, swap_trump=False, close_deck=False)
    output_actions[19] = Action(card=Card(Card.Clubs, Card.Ace), marriage=None, swap_trump=False, close_deck=False)

    # Marriages
    output_actions[20] = Action(card=Card(Card.Diamonds, Card.Queen), marriage=d_marriage, swap_trump=False, close_deck=False)
    output_actions[21] = Action(card=Card(Card.Diamonds, Card.King), marriage=d_marriage, swap_trump=False, close_deck=False)
    output_actions[22] = Action(card=Card(Card.Spades, Card.Queen), marriage=s_marriage, swap_trump=False, close_deck=False)
    output_actions[23] = Action(card=Card(Card.Spades, Card.King), marriage=s_marriage, swap_trump=False, close_deck=False)
    output_actions[24] = Action(card=Card(Card.Hearts, Card.Queen), marriage=h_marriage, swap_trump=False, close_deck=False)
    output_actions[25] = Action(card=Card(Card.Hearts, Card.King), marriage=h_marriage, swap_trump=False, close_deck=False)
    output_actions[26] = Action(card=Card(Card.Clubs, Card.Queen), marriage=c_marriage, swap_trump=False, close_deck=False)
    output_actions[27] = Action(card=Card(Card.Clubs, Card.King), marriage=c_marriage, swap_trump=False, close_deck=False)
    #Special Actions
    output_actions[28] = Action(card=None, marriage=None, swap_trump=True, close_deck=False)
    output_actions[29] = Action(card=None, marriage=None, swap_trump=False, close_deck=True)


    def __init__(self):
        pass

    @staticmethod
    def card_key(suit, value):
        # Build a unique int for quicker indexing (hopefully?)]
        # maybe build these upfront for performance?
        # e.g. 0 * 20 + 11 for Ace of spades
        # 1 * 20 + 2 = 22 for Jack of clubs
        return suit * 20 + value

    @staticmethod
    def create_input_from_game_state(game, player):

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

        for suit in [Card.Diamonds, Card.Clubs, Card.Spades, Card.Hearts]:
            for value in Card.Values.keys():
                inputs[IOHelpers.card_key(suit, value)] = CardInput(suit, value)

        for card in player.hand:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.in_my_hand = True

        # for card in game.get_other_player(player).hand - would be cheating!! Would be an interesting test, though!
        # As is, this handles cases where we know unequivocally that they have part of a marriage or the last 5 cards of the deck
        for card in player.opponent_hand:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.in_opponent_hand = True

        for card in player.cards_won:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.won_by_me = True

        for card in player.opponent_cards_won:
            card_input = inputs[IOHelpers.card_key(card.suit, card.value)]
            card_input.won_by_opponent = True

        lead_card = game.leading_card
        if lead_card is not None:
            inputs[IOHelpers.card_key(lead_card.suit, lead_card.value)].is_leading_card = True

        inputs[IOHelpers.deck_closed_key] = 1 if game.deck_closed else 0
        inputs[IOHelpers.my_points_to_victory_key] = game.match_point_limit - player.game_points
        inputs[IOHelpers.my_uneared_points_key] = 0
        inputs[IOHelpers.opponents_points_to_victory_key] = game.match_point_limit - player.opponent_game_points
        inputs[IOHelpers.opponents_uneared_points_key] = 0
        inputs[IOHelpers.match_points_on_offer_to_me_key] = 0
        inputs[IOHelpers.match_points_on_offer_to_opponent] = 0

        # I now have all the data I need. Now to convert it into something useful.
        # Flat vector is simplest. Or do some clever CNN?

        # Simple flat vector to start with...
        return IOHelpers.__create_flat_tensor(inputs, game)

    @staticmethod
    def __create_flat_tensor(inputs, game):
        # (With performance in mind, it'd be better to create the tensor elements directly instead of using a list but hey...)
        input_vector = []
        for item in inputs.values():
            if type(item) is CardInput:
                input_vector.append(item.suit / 3) #Normalise suit value
                input_vector.append(item.value / game.game_point_limit) #Normalise card value to fraction of a game
                input_vector.append(item.in_my_hand)
                input_vector.append(item.in_opponent_hand)
                input_vector.append(item.won_by_me)
                input_vector.append(item.won_by_opponent)
                input_vector.append(item.is_leading_card)

        input_vector.append(inputs[IOHelpers.deck_closed_key])
        input_vector.append(inputs[IOHelpers.my_points_to_victory_key] / game.game_point_limit)
        input_vector.append(inputs[IOHelpers.opponents_points_to_victory_key] / game.game_point_limit)

        # input_vector.append(inputs[IOHelpers.my_uneared_points_key] / game.game_point_limit)
        # input_vector.append(inputs[IOHelpers.opponents_uneared_points_key] / game.game_point_limit)
        # input_vector.append(inputs[IOHelpers.match_points_on_offer_to_me_key])
        # input_vector.append(inputs[IOHelpers.match_points_on_offer_to_opponent])

        return torch.tensor(input_vector, dtype=torch.float)

    @staticmethod
    def check_action_legal(i, legal_actions):
        is_legal = False
        return_action = None

        output_action = IOHelpers.output_actions[i]
        for action in legal_actions:
            if output_action == action:
                is_legal = True
                return_action = action
                break

        return is_legal, return_action

    @staticmethod
    def get_index_for_action(action):
        for i, output_action in IOHelpers.output_actions.items():
            if action == output_action:
                return i

    @staticmethod
    def get_random_legal_action(game, player):
        player.evaluate_legal_actions(game.leading_card is None, game.leading_card)
        action = random.choice(player.legal_actions)
        i = IOHelpers.get_index_for_action(action)
        return torch.tensor([i], dtype=torch.long), action

    # Pick an action based on values. Ignore illegal moves
    # convert it into an actual action
    @staticmethod
    def policy(q_values, game, player):

        player.evaluate_legal_actions(game.leading_card is None, game.leading_card)
        max_value = -100.0
        selected_action = None
        selected_action_id = None
        for i, item in enumerate(q_values):
            if float(item) > max_value:
                is_legal, action = IOHelpers.check_action_legal(i, player.legal_actions)
                if is_legal:
                    max_value = float(item)
                    selected_action = action
                    selected_action_id = torch.tensor([i], dtype=torch.long)
        if selected_action is None:
            raise Exception('No valid action found')

        return selected_action_id, selected_action
