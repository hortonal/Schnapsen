"""Card Game Class"""
from Game.Deck import Deck
from Game.Marriage import Marriage
from Game.Marriages import Marriages
import logging
import sys
import random


class Game:

    def __init__(self, player_a, player_b, match_point_limit=7):

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        # Register game instance in players
        player_a.game = self
        player_b.game = self
        # Initialise a bunch of variables and state
        self._player_a = player_a
        self._player_b = player_b
        self._players = [player_a, player_b]
        self._player_with_1st_deal = None
        self._player_with_2nd_deal = None
        self._deck = []
        self._match_point_limit = match_point_limit
        self._init_game_vars()
        self._define_first_deal()

    def _init_game_vars(self):
        self._leading_player = None
        self._following_player = None
        self._hand_winner = None
        self._trump_card = None
        self.deck_closed = False
        self._deck_closed_by_player = False
        self._deck_closer = None
        self._deck_closer_points = 0
        self._deck_non_closer_points = 0
        self._have_game_winner = False
        self._game_winner = None
        self._game_loser = None
        for player in self._players:
            player.ready_for_next_game()
        self._marriages = Marriages()

    def play(self):

        while (self._player_a.match_points < self._match_point_limit and
               self._player_b.match_points < self._match_point_limit):
            self._play_single_game()
            # Prepare for the next game
            self._switch_players()

    def declare_win(self, player):
        # Verify players claim
        # Make independent count of player's points...
        self._have_game_winner = True
        self._game_winner = player
        self._game_loser = self._get_other_player(self._game_winner)

    # Handle a player declaring a marriage
    # Player must be leader and immediate play card
    # Points for marriage only registered once any normal trick is won
    # If player declares 66 at this point, the game terminates immediately
    def declare_marriage(self, player, marriage):

        logging.debug('Marriage declared by {a} {b} {c}'.format(a=player.name, b=marriage.queen, c=marriage.king))
        if player is not self._leading_player:
            raise Exception('Invalid marriage - Only leading player can declare marriage')

        marriage.set_points(self._trump_card.suit)

        self._marriages[marriage.suit] = marriage

        # Award player points immediately if possible
        if player.game_points != 0:
            self._award_game_points(player, marriage.points)
            marriage.points_awarded = True

    # Handle a player closing the deck
    # Said player must be current leader
    # calc points on offer
    def declare_deck_closed(self, player):

        logging.debug('Player closing deck {a}'.format(a=player))
        if self._deck_closed_by_player:
            raise Exception("Deck already closed")

        if player is not self._leading_player:
            raise Exception("non-leading player can't close deck")

        self.deck_closed = True
        self._deck_closed_by_player = True
        self._deck_closer = player
        self._deck_closer_points = self._calc_match_points_on_offer(player=player, closer=True)
        self._deck_non_closer_points = self._calc_match_points_on_offer(player=player, closer=False)

    def swap_trump(self, player, card):
        player.receive_card(self._trump_card)
        self._trump_card = card

    def _play_single_game(self):

        logging.debug('playing game')

        self._init_game_vars()
        self._deck = Deck()
        self._deck.shuffle()
        self._deal()
        self._play_hands()

    def _play_hands(self):

        self._leading_player = self._player_with_1st_deal
        self._following_player = self._player_with_2nd_deal

        # Play hands until someone declares a win or players run out of cards
        while not self._have_game_winner and self._player_a.has_cards_left():
            self._play_hand()
            logging.debug('{c}:{d}, Match points {e}:{f}'.format(
                c=self._player_a.game_points, d=self._player_b.game_points,
                e=self._player_a.match_points, f=self._player_b.match_points))

        # If deck exhausted and no winner, the winner of the last hand gets the points
        if not self._have_game_winner:
            self.declare_win(self._hand_winner)
            logging.debug('win by default')

        self._award_match_points()

        logging.debug('Final Score: {a} vs {b} Game Points {c}:{d}, Match points {e}:{f}'.format(
            a=self._player_a.name, b=self._player_b.name, c=self._player_a.game_points, d=self._player_b.game_points,
            e=self._player_a.match_points, f=self._player_b.match_points))

    def _play_hand(self):

        leading_card = self._leading_player.play()

        # Validate marriage card played if declared
        marriage = self._marriages.unplayed_marriage()
        if marriage is not None:
            marriage.notify_card_played(leading_card)

        # If leader declares victory after marriage, no further actions necessary
        if self._have_game_winner:
            return

        following_card = self._following_player.play(leading_card)

        logging.debug('{a} leads vs. {c}, {b} vs. {d}. Trump: {e}'.format(
            a=self._leading_player.name, b=leading_card, c=self._following_player.name, d=following_card, e=self._trump_card))

        # Decide winning hand. Start with assuming the leader wins and
        # Handle only the other two cases
        self._hand_winner = self._leading_player
        if leading_card.suit == following_card.suit:
            if following_card.value > leading_card.value:
                self._hand_winner = self._following_player
        else:
            if following_card.suit == self._trump_card.suit:
                self._hand_winner = self._following_player

        loser = self._get_other_player(self._hand_winner)

        points = leading_card.value + following_card.value + self._marriages.award_points(self._hand_winner)

        self._award_game_points(self._hand_winner, points, [leading_card, following_card])

        # Deal extra cards, winner first
        if not self.deck_closed:
            self._give_cards(self._hand_winner, 1)
            self._give_cards(loser, 1)

        # Set winner to leading player
        self._leading_player = self._hand_winner
        self._following_player = loser

    def _award_game_points(self, player, points, cards=[]):
        for iter_player in self._players:
            iter_player.notify_game_points_won(player, points, cards)

    def _award_match_points(self):

        if self._deck_closed_by_player:
            if self._deck_closer == self._game_winner:
                match_points = self._deck_closer_points
            else:
                match_points = self._deck_non_closer_points
        else:
            match_points = self._calc_match_points_on_offer(self._game_winner)

        for iter_player in self._players:
            iter_player.notify_match_points_won(self._game_winner, match_points)

    def _notify_players_of_trump(self, card):
        for player in self._players:
            player.notify_trump(card)

    def _calc_match_points_on_offer(self, player, closer=True):
        other_player = self._get_other_player(player)

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

    def _switch_players(self):

        tmp_player = self._player_with_1st_deal
        self._player_with_1st_deal = self._player_with_2nd_deal
        self._player_with_2nd_deal = tmp_player

    def _deal(self):

        self._give_cards(self._player_with_1st_deal, 3)
        self._give_cards(self._player_with_2nd_deal, 3)
        self._trump_card = self._deck.pop()
        self._give_cards(self._player_with_1st_deal, 2)
        self._give_cards(self._player_with_2nd_deal, 2)

        self._notify_players_of_trump(self._trump_card)

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
                player.receive_card(self._trump_card)
            else:
                player.receive_card(self._deck.pop())

    def _get_other_player(self, player):
        return self._player_b if player is self._player_a else self._player_a
