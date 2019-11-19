"""Card Game Class"""
from Game.Deck import Deck
from Game.Marriages import Marriages
import logging
import random
from Game.Player import Player


class Game:

    def __init__(self, player_a, player_b, match_point_limit=7, game_point_limit=66):

        self._logger = logging.getLogger()
        # Register game instance in players
        player_a.game = self
        player_b.game = self
        # Initialise a bunch of variables and state
        self._player_a = player_a
        self._player_b = player_b
        self._players = [player_a, player_b]
        self.game_point_limit = game_point_limit
        self.match_point_limit = match_point_limit
        self._deck = []
        self.__init_match_vars()
        self.__init_game_vars()
        self.on_event_callback_card_played = None  # Func set externally for event handling

    def __init_match_vars(self):
        self._player_with_1st_deal = None
        self._player_with_2nd_deal = None
        for player in self._players:
            player.ready_for_next_match()
        self._define_first_deal()
        self.match_winner = None
        self.have_match_winner = False

    def __init_game_vars(self):
        self.active_player = None
        self.leading_card = None
        self.following_card = None
        self.leading_player = None
        self._following_player = None
        self._hand_winner = None
        self.trump_card = None
        self.deck_closed = False
        self._deck_closed_by_player = False
        self._deck_closer = None
        self._deck_closer_points = 0
        self._deck_non_closer_points = 0
        self.have_game_winner = False
        self.game_winner = None
        self._game_loser = None
        for player in self._players:
            player.ready_for_next_game()
        self._marriages = Marriages()

    def new_match(self):
        self.__init_match_vars()

    def new_game(self):
        self.__init_game_vars()
        self._deck = Deck()
        self._deck.shuffle()
        self._deal()
        self.leading_player = self._player_with_1st_deal
        self._following_player = self._player_with_2nd_deal
        self.active_player = self.leading_player

    def play_automated(self):
        self.new_match()
        while not self.have_match_winner:
            self.new_game()
            while not self.have_game_winner:
                self.progress_automated_actions()  # If AI vs. AI, whole game plays

    # Exits if action results in game winner
    def progress_automated_actions(self):
        while self.active_player.automated and not self.have_game_winner:
            self._logger.log(logging.DEBUG, 'performing next AI action')
            self.evaluate_active_player_actions()
            if len(self.active_player.legal_actions) > 0:
                self.do_next_action(self.active_player, self.active_player.select_action())

    def evaluate_active_player_actions(self):
        self.active_player.evaluate_legal_actions(self.leading_card)

    def do_next_action(self, player, action):

        # Check logging level first to avoid making the string unnecessarily
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.log(logging.DEBUG, 'Action ' + player.name + ', card: ' + str(action.card is not None) + ', marriage ' + str(action.marriage is not None) + ', close deck: ' + str(action.close_deck) + ', swap_trump: ' + str(action.swap_trump))

        play_card = None
        if action.swap_trump is True:
            self.__swap_trump(player)

        if action.close_deck is True:
            self.__close_deck(player)

        if action.marriage is not None:
            self.__declare_marriage(player, action.marriage)

        if action.card is not None:
            play_card = self.__play_card(player, action.card)

        if not self.have_game_winner:
            if play_card is not None:
                if player is self.leading_player:
                    self.leading_card = play_card
                    self.__call_back_hand_played()
                    self.active_player = self.get_other_player(self.active_player)
                else:
                    self.following_card = play_card
                    self.__call_back_hand_played()
                    self.__end_of_hand()

    def __call_back_hand_played(self):
        if self.on_event_callback_card_played is not None:
            self.on_event_callback_card_played()

    def __end_of_hand(self):
        self._hand_winner = self.leading_player
        if self.leading_card.suit == self.following_card.suit:
            if self.following_card.value > self.leading_card.value:
                self._hand_winner = self._following_player
        else:
            if self.following_card.suit == self.trump_card.suit:
                self._hand_winner = self._following_player

        loser = self.get_other_player(self._hand_winner)

        points = self.leading_card.value + self.following_card.value + self._marriages.award_points(self._hand_winner)

        self._award_game_points(self._hand_winner, points, [self.leading_card, self.following_card])

        self._logger.debug(self._hand_winner.name + ' wins')

        # Deal extra cards, winner first
        if not self.deck_closed:
            self._give_cards(self._hand_winner, 1)
            self._give_cards(loser, 1)



        # Set winner to leading player
        self.leading_card = None
        self.following_card = None
        self.leading_player = self._hand_winner
        self.active_player = self.leading_player
        self._following_player = loser

        if len(self._player_a.hand) == 0:
            if not self.have_game_winner:
                self._logger.debug('win by default')
                self.declare_game_win(self._hand_winner)

    # called by player to notify game of its alleged victory
    def declare_game_win(self, player):
        # Verify players claim
        # Make independent count of player's points...
        self.have_game_winner = True
        self.game_winner = player
        self._game_loser = self.get_other_player(self.game_winner)
        self._award_match_points()
        self._switch_deals_between_games()
        self.__check_and_handle_match_win()

    def __check_and_handle_match_win(self):
        if self._player_a.match_points >= self.match_point_limit:
            self.match_winner = self._player_a
            self.have_match_winner = True
        if self._player_b.match_points >= self.match_point_limit:
            self.match_winner = self._player_b
            self.have_match_winner = True

    # Handle a player declaring a marriage
    # Player must be leader and immediate play card
    # Points for marriage only registered once any normal trick is won
    # If player declares 66 at this point, the game terminates immediately
    def __declare_marriage(self, player, marriage):

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Marriage declared by {a} {b} {c}'.format(a=player.name, b=marriage.queen, c=marriage.king))
        if player is not self.leading_player:
            raise Exception('Invalid marriage - Only leading player can declare marriage')

        marriage.set_points(self.trump_card.suit)

        self._marriages[marriage.suit] = marriage

        # Award player points immediately if possible
        if player.game_points != 0:
            self._award_game_points(player, marriage.points)
            marriage.points_awarded = True

    def __play_card(self, player, card):
        for item, iter_card in enumerate(player.hand):
            if iter_card.value == card.value and \
                            iter_card.suit == card.suit:
                return player.hand.pop(item)
        raise Exception('Card not in hand')

    # Handle a player closing the deck
    # Said player must be current leader
    # calc points on offer
    def __close_deck(self, player):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Player closing deck {a}'.format(a=player))
        if self._deck_closed_by_player:
            raise Exception("Deck already closed")

        if player is not self.leading_player:
            raise Exception("non-leading player can't close deck")

        self.deck_closed = True
        self._deck_closed_by_player = True
        self._deck_closer = player
        self._deck_closer_points = self._calc_match_points_on_offer(player=player, closer=True)
        self._deck_non_closer_points = self._calc_match_points_on_offer(player=player, closer=False)

    def __swap_trump(self, player):

        if self.deck_closed:
            raise Exception('Player can not swap trump as deck is closed')

        if player.hand.has_card(self.trump_card.suit, 2):
            jack = player.hand.pop_card(self.trump_card.suit, 2)
        else:
            raise Exception('Player can not swap trump as requisite card not in hand')

        player.receive_card(self.trump_card)
        self.trump_card = jack

    def _award_game_points(self, player, points, cards=[]):
        for iter_player in self._players:
            iter_player.notify_game_points_won(player, points, cards)

    def _award_match_points(self):

        if self._deck_closed_by_player:
            if self._deck_closer == self.game_winner:
                match_points = self._deck_closer_points
            else:
                match_points = self._deck_non_closer_points
        else:
            match_points = self._calc_match_points_on_offer(self.game_winner)

        for iter_player in self._players:
            iter_player.notify_match_points_won(self.game_winner, match_points)

    def _notify_players_of_trump(self, card):
        for player in self._players:
            player.notify_trump(card)

    def _calc_match_points_on_offer(self, player, closer=True):
        other_player = self.get_other_player(player)

        # Default award for a single game
        match_points = 1

        # The non-closer gets at least 2 points if he wins
        if not closer:
            match_points = 2

        # Any winner gets 3 points in the opposition has 0 trick points
        if other_player.game_points == 0:
            match_points = 3
        elif other_player.game_points < 33:
            match_points = 2

        return match_points

    def _switch_deals_between_games(self):

        tmp_player = self._player_with_1st_deal
        self._player_with_1st_deal = self._player_with_2nd_deal
        self._player_with_2nd_deal = tmp_player

    def _deal(self):

        self._give_cards(self._player_with_1st_deal, 3)
        self._give_cards(self._player_with_2nd_deal, 3)
        self.trump_card = self._deck.pop()
        self._give_cards(self._player_with_1st_deal, 2)
        self._give_cards(self._player_with_2nd_deal, 2)

        self._notify_players_of_trump(self.trump_card)

    # Assign leader at random
    # This could be prettier but it works..
    def _define_first_deal(self):
        self._player_with_1st_deal = self._player_a
        self._player_with_2nd_deal = self._player_a

        if random.choice([True, False]):
            self._player_with_1st_deal = self._player_b
        else:
            self._player_with_2nd_deal = self._player_b

    def _give_cards(self, player, number):
        for x in range(number):
            if len(self._deck) == 0 and number == 1:
                self.deck_closed = True
                player.receive_card(self.trump_card)
            else:
                player.receive_card(self._deck.pop())

    def get_other_player(self, player):
        return self._player_b if player is self._player_a else self._player_a
