from Game.Card import Card
from AI.NeuralNetwork.CardInput import CardInput
import torch


class IOHelpers:

    deck_closed_key = -1
    my_points_to_victory_key = -2
    my_uneared_points_key = -3
    opponents_points_to_victory_key = -4
    opponents_uneared_points_key = -5
    match_points_on_offer_to_me_key = -6
    match_points_on_offer_to_opponent = -7

    def __init__(self):
        pass

    @staticmethod
    def generate_input_card_key(suit, value):
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
                inputs[IOHelpers.generate_input_card_key(suit, value)] = CardInput(suit, value)


        for card in player.hand:
            card_input = inputs[IOHelpers.generate_input_card_key(card.suit, card.value)]
            card_input.in_my_hand = True

        # for card in game.get_other_player(player).hand - would be cheating!! Would be an interesting test, though!
        # As is, this handles cases where we know unequivocally that they have part of a marriage or the last 5 cards of the deck
        for card in player.opponent_hand:
            card_input = inputs[IOHelpers.generate_input_card_key(card.suit, card.value)]
            card_input.in_opponent_hand = True

        for card in player.cards_won:
            card_input = inputs[IOHelpers.generate_input_card_key(card.suit, card.value)]
            card_input.won_by_me = True

        for card in player.opponent_cards_won:
            card_input = inputs[IOHelpers.generate_input_card_key(card.suit, card.value)]
            card_input.won_by_opponent = True

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
        return IOHelpers.__create_flat_tensor(inputs)

    @staticmethod
    def __create_flat_tensor(inputs):
        # (With performance in mind, it'd be better to create the tensor elements directly instead of using a list but hey...)
        input_vector = []
        for item in inputs.values():
            if type(item) is CardInput:
                input_vector.append(item.suit)
                input_vector.append(item.value)
                input_vector.append(item.in_my_hand)
                input_vector.append(item.in_opponent_hand)
                input_vector.append(item.won_by_me)
                input_vector.append(item.won_by_opponent)

        for input_key in [
            IOHelpers.deck_closed_key,
            IOHelpers.my_points_to_victory_key,
            IOHelpers.my_uneared_points_key,
            IOHelpers.opponents_points_to_victory_key,
            IOHelpers.opponents_uneared_points_key,
            IOHelpers.match_points_on_offer_to_me_key,
            IOHelpers.match_points_on_offer_to_opponent]:
            input_vector.append(inputs[input_key])

        return torch.tensor(input_vector)
