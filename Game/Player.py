"""Parent player class.
All player implementation should inherit from this and simply implement the
_select_action method to notify the game what it's doing. All other player logic
and game controller interaction handled in this class"""
from Game.Hand import Hand
from Game.Action import Action


class Player:

    def __init__(self, name):
        self.name = name
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
        self._legal_actions = []

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

    def _select_action(self, legal_actions):
        raise Exception('Must be implemented by child')

    def receive_card(self, card):
        self.hand.append(card)

    # Core play action sequence
    def play(self, opponents_card=None):

        card = None
        while card is None:
            # Perform actions until play card
            legal_actions = self.__evaluate_legal_actions(opponents_card is None,
                                                          opponents_card)
            card = self.__do_action(self._select_action(legal_actions))
        return card

    def __swap_trump(self):

        if self.game.deck_closed:
            raise Exception('Player can not swap trump as deck is closed')

        if self.hand.has_card(self._trump.suit, 2):
            jack = self.hand.pop_card(self._trump.suit, 2)
        else:
            raise Exception('Player can not swap trump as requisite card not in hand')

        self.game.swap_trump(self, jack)

    def __close_deck(self):
        self.game.declare_deck_closed(self)

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
            self.game.declare_win(self)

    def _enough_points(self):
        return self.game_points >= 66

    def has_cards_left(self):
        return len(self.hand) != 0

    def __play_marriage(self, marriage, card):
        self.game.declare_marriage(self, marriage)
        return self.__play_card(card)

    def __play_card(self, card):
        for item, iter_card in enumerate(self.hand):
            if iter_card.value == card.value and \
               iter_card.suit == card.suit:
                return self.hand.pop(item)
        raise Exception('Card not in hand')

    # This ugly AF... But it works
    def __evaluate_legal_actions(self, am_leader, opponents_card):

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
        return legal_actions

    def __do_action(self, action):

        return_card = None
        if action.swap_trump is True:
            self.__swap_trump()

        if action.close_deck is True:
            self.__close_deck()

        if action.marriage is not None:
            return_card = self.__play_marriage(action.marriage, action.card)
        elif action.card is not None:
            return_card = self.__play_card(action.card)

        return return_card

    def _print_str_name(self):
        return "SimplerPlayer: " + self.name

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()
