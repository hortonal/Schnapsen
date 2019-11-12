"""Parent player class.
All player implementation should inherit from this and simply implement the
_select_action method to notify the game what it's doing. All other player logic
and game controller interaction handled in this class"""
from Game.Hand import Hand
from Game.Action import Action
import random

class SimplePlayer:

    def __init__(self, name, automated=True, requires_model_load=False):
        self.name = name
        self.automated = automated
        self.requires_model_load = requires_model_load
        self.hand = Hand()
        self.cards_won = []
        self.match_points = 0
        self.game_points = 0
        self.opponent_hand = []
        self.opponent_cards_won = []
        self.opponent_match_points = 0
        self.opponent_game_points = 0
        self.game = None  # Assigned by game controller
        self._trump = None
        self.legal_actions = []

    def ready_for_next_match(self):
        self.match_points = 0
        self.opponent_match_points = 0
        self.ready_for_next_game()

    def ready_for_next_game(self):
        self.hand = Hand()
        self.cards_won = []
        self.game_points = 0
        self.opponent_hand = []
        self.opponent_cards_won = []
        self.opponent_game_points = 0
        self._trump = None

    def receive_card(self, card):
        self.hand.append(card)

    def notify_game_points_won(self, player, points, cards=None):
        if player is self:
            self.game_points += points
            self._check_and_declare_win()
            if cards is not None:
                for card in cards:
                    self.cards_won.append(card)
        else:
            self.opponent_game_points += points
            if cards is not None:
                for card in cards:
                    self.opponent_cards_won.append(card)

    def notify_match_points_won(self, player, points):
        if player is self:
            self.match_points += points
        else:
            self.opponent_match_points += points

    def _check_and_declare_win(self):
        if self._enough_points():
            self.game.declare_game_win(self)

    def _enough_points(self):
        return self.game_points >= self.game.game_point_limit

    def has_cards_left(self):
        return len(self.hand) != 0

    # All cards are valid
    def evaluate_legal_actions(self, am_leader, opponents_card):
        legal_actions = []
        for card in self.hand:
            legal_actions.append(Action(card=card))

        self.legal_actions = legal_actions

    def _print_str_name(self):
        return self.name

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()

    def select_action(self):
        return random.choice(self.legal_actions)

    def select_action_better(self):

        selected_action = None

        if self.game.leading_player is self:
            # Play highest card if leader
            highest_card_value = 0
            if selected_action is None:
                for action in self.legal_actions:
                    if action.card is not None:
                        if action.card.value > highest_card_value:
                            highest_card_value = action.card.value
                            selected_action = action
        else:
            # Can I win hand? Why wouldn't I want to?
            # Play lowest card if follower
            lowest_card_value = 100
            if selected_action is None:
                for action in self.legal_actions:
                    if action.card is not None:
                        if action.card.value < lowest_card_value:
                            lowest_card_value = action.card.value
                            selected_action = action

        if selected_action is None:
            raise Exception('Pick an action fuck-wit')

        return selected_action
