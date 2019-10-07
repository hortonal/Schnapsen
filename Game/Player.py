"""Parent player class.
All player implementation should inherit from this for hand validation
and other helpers"""
from Game.HandHelpers import HandHelpers


class Player:

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.cards_won = []
        self.match_points = 0
        self.game_points = 0
        self.opponent_hand = []
        self.opponent_cards_won = []
        self.opponent_match_points = 0
        self.opponent_game_points = 0
        self.game = None  # Assigned by game controller
        self._trump = None

    def ready_for_next_match(self):
        self.match_points = 0
        self.opponent_match_points = 0
        self.ready_for_next_game()

    def ready_for_next_game(self):
        self.hand = []
        self.cards_won = []
        self.game_points = 0
        self.opponent_hand = []
        self.opponent_cards_won = []
        self.opponent_game_points = 0
        self._trump = None

    def receive_card(self, card):
        self.hand.append(card)

    def play(self, opponents_card=None):
        raise Exception('play method not implemented by child player class')

    def notify_trump(self, card):
        self._trump = card

    def notify_game_points_won(self, player, points, cards=[]):
        if player is self:
            self.game_points += points
            self.check_and_declare_win()
            for card in cards:
                self.cards_won.append(card)

    def notify_match_points_won(self, player, points):
        if player is self:
            self.match_points += points

    def check_and_declare_win(self):
        if self.enough_points():
            self.game.declare_win(self)

    def enough_points(self):
        return self.game_points >= 66

    def has_cards_left(self):
        return len(self.hand) != 0

    def evaluate_legal_actions(self):
        pass

    def _print_str_name(self):
        return "SimplerPlayer: " + self.name

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()
