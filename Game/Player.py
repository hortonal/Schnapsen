"""Parent player class.
All player implementation should inherit from this and simply implement the
_select_action method to notify the game what it's doing. All other player logic
and game controller interaction handled in this class"""
from Game.Hand import Hand
from Game.Action import Action


class Player:
    type_AI = 0
    type_human = 1

    def __init__(self, name, automated=True):
        self.name = name
        self.automated = automated
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
        self.type = Player.type_AI  # Must be overridden for humans

    # Child player class must implement this method and return an action
    # The player or some other controller should probably first ask for the
    # legal actions to evaluated (but an illegal action is handled by the game controller)
    def select_action(self):
        raise Exception('Must be implemented by child')

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

    def notify_trump(self, card):
        self._trump = card

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

    # This ugly AF... But it works
    def evaluate_legal_actions(self, am_leader, opponents_card):

        legal_actions = []

        if am_leader:
            if self.hand.has_card(self._trump.suit, 2) and not self.game.deck_closed:
                legal_actions.append(Action(swap_trump=True))

            if not self.game.deck_closed:
                legal_actions.append(Action(close_deck=True))

            have_marriages, marriages = self.hand.available_marriages(self)
            for marriage in marriages:
                legal_actions.append(Action(card=marriage.queen,
                                            marriage=marriage))
                legal_actions.append(Action(card=marriage.king,
                                            marriage=marriage))

            for card in self.hand:
                legal_actions.append(Action(card=card))
        else:
            if not self.game.deck_closed:
                for card in self.hand:
                    legal_actions.append(Action(card=card))
            else:
                more_legal_actions = True
                for card in self.hand.cards_of_same_suit(opponents_card.suit, opponents_card.value):
                    legal_actions.append(Action(card=card))
                    more_legal_actions = False

                if more_legal_actions:
                    for card in self.hand.cards_of_same_suit(opponents_card.suit):
                        legal_actions.append(Action(card=card))
                        more_legal_actions = False

                if more_legal_actions:
                    for card in self.hand.cards_of_same_suit(self._trump.suit):
                        legal_actions.append(Action(card=card))
                        more_legal_actions = False

                if more_legal_actions:
                    for card in self.hand:
                        legal_actions.append(Action(card=card))

        self.legal_actions = legal_actions

    def _print_str_name(self):
        return self.name

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()
