"""Card Game Class"""
from Game.Deck import Deck
import logging
import sys
import random


class Game:

    def __init__(self, player_A, player_B, match_point_limit=7):

        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        # Register game instance in players
        player_A.game = self
        player_B.game = self
        # Initialise a bunch of variables and state
        self._player_A = player_A
        self._player_B = player_B
        self._player_with_1st_deal = None
        self._player_with_2nd_deal = None
        self._leading_player = None
        self._following_player = None
        self._game_winner = None
        self._deck = []
        self._match_point_limit = match_point_limit
        self._trump_card = None
        self._define_first_deal()
        self._have_game_winner = False

    def play(self):

        while (self._player_A.match_points < self._match_point_limit and
               self._player_B.match_points < self._match_point_limit):
            self._play_single_game()
            # Prepare for the next game
            self._switch_players()

    def declare_win(self, player):
        # Verify players claim
        # Make independent count of player's points...
        logging.debug('Outright win')
        self._have_game_winner = True
        # ToDo: calculate match points
        player.match_points += 1

    def declare_marriage(self, player):
        # Verify marriage... Process points
        pass

    def _play_single_game(self):

        logging.debug('playing game')

        #Initialise the players
        for player in [self._player_A, self._player_B]:
            player.game_points = 0
            player.hand = []

        self._have_game_winner = False
        self._deck_closed = False
        self._deck = Deck()
        self._deck.shuffle()
        self._deal()

        self._play_hands()

    def _play_hands(self):

        self._leading_player = self._player_with_1st_deal
        self._following_player = self._player_with_2nd_deal

        #Play hands until someone declares a win
        while not self._have_game_winner and self._player_A.has_cards_left():
            self._play_hand()
            logging.debug('{c}:{d}, Match points {e}:{f}'.format(
                c=self._player_A.game_points, d=self._player_B.game_points,
                e=self._player_A.match_points, f=self._player_B.match_points))


        #If deck exhausted and no winner, the winner of the last hand gets the points
        if not self._have_game_winner:
            logging.debug('win by default')
            self._game_winner.match_points += 1

        logging.debug('Final Score: {a} vs {b} Game Points {c}:{d}, Match points {e}:{f}'.format(
            a=self._player_A, b=self._player_B, c=self._player_A.game_points, d=self._player_B.game_points,
            e=self._player_A.match_points, f=self._player_B.match_points))

        if self._player_A.game_points + self._player_B.game_points > 120:
            # Todo: this will change when marriages implemented...
            raise Exception('More than 120 total game points')

    def _play_hand(self):

        leading_card = self._leading_player.play()
        following_card = self._following_player.play(leading_card)

        logging.debug('{a} leads vs. {c}, {b} vs. {d}. Trump: {e}'.format(
            a=self._leading_player.name, b=leading_card, c=self._following_player.name, d=following_card, e=self._trump_card))

        # Leader wins most cases
        self._game_winner = self._leading_player
        loser = self._following_player

        # Handle only cases where follower wins
        if leading_card.suit == following_card.suit:
            if following_card.value > leading_card.value:
                self._game_winner = self._following_player
                loser = self._leading_player
        else:
            if following_card.suit == self._trump_card.suit:
                self._game_winner = self._following_player
                loser = self._leading_player

        self._game_winner.notify_hand_won(leading_card.value + following_card.value)

        #Deal extra cards, winner first
        if not self._deck_closed:
            self._give_cards(self._game_winner, 1)
            self._give_cards(loser, 1)

        # Set winner to leading player
        self._leading_player = self._game_winner
        self._following_player = loser

    def _switch_players(self):

        tmp_player = self._player_with_1st_deal
        self._player_with_1st_deal = self._player_with_2nd_deal
        self._player_with_2nd_deal = tmp_player

    def _deal(self):

        self._give_cards(self._player_with_1st_deal, 3)
        self._give_cards(self._player_with_2nd_deal, 3)
        self._trump_card = self._deck.pop()
        logging.debug('Trump is: {}'.format(self._trump_card))
        self._give_cards(self._player_with_1st_deal, 2)
        self._give_cards(self._player_with_2nd_deal, 2)

    def _define_first_deal(self):
        # Define the 1st leader at random
        self._player_A.is_leader = random.choice([True, False])
        self._player_B.is_leader = not self._player_A.is_leader

        # Todo: make less ugly
        if self._player_A.is_leader:
            self._player_with_1st_deal = self._player_A
            self._player_with_2nd_deal = self._player_B
        else:
            self._player_with_1st_deal = self._player_B
            self._player_with_2nd_deal = self._player_A

    def _give_cards(self, player, number):
        for x in range(number):
            if len(self._deck) == 0 and number == 1:
                self._deck_closed = True
                player.receive_card(self._trump_card)
            else:
                player.receive_card(self._deck.pop())
