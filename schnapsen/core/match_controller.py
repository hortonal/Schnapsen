"""Card Game Class."""
import logging
import random
from typing import List

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Value
from schnapsen.core.deck import Deck
from schnapsen.core.marriage import Marriage
from schnapsen.core.player import Player


class MatchController:
    """Core game controller object."""

    def __init__(self, player_a: Player, player_b: Player,
                 match_point_limit: int = 7, game_point_limit: int = 66) -> None:
        """Create a GameController instance.

        Parameters
        ----------
        player_a : Player
            The first Player.
        player_b : Player
            The opponent.
        match_point_limit : int, optional
            The number of game points required to win a match, by default 7
        game_point_limit : int, optional
            The number of points required to win a game, by default 66
        """
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
        self._reset_state_for_new_match()
        self._reset_state_for_new_game()
        self.on_event_callback_card_played = None  # Func set externally for event handling, e.g. in a GUI.

    def _reset_state_for_new_match(self) -> None:
        self._player_with_1st_deal = None
        self._player_with_2nd_deal = None
        for player in self._players:
            player.reset_for_new_match()
        self._define_first_deal()
        self.match_winner = None
        self.have_match_winner = False

    def _reset_state_for_new_game(self) -> None:
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
            player.reset_for_new_game()
        self._marriages_info = {}

    def new_match(self) -> None:
        """Start a new match."""
        self._reset_state_for_new_match()

    def new_game(self) -> None:
        """Start a new game within match."""
        self._reset_state_for_new_game()
        self._deck = Deck()
        self._deck.shuffle()
        self._deal()
        self.leading_player = self._player_with_1st_deal
        self._following_player = self._player_with_2nd_deal
        self.active_player = self.leading_player

    def play_automated_match(self) -> None:
        """Progress match/game state automatically."""
        self.new_match()
        while not self.have_match_winner:
            self.new_game()
            while not self.have_game_winner:
                self.progress_automated_actions()  # If AI vs. AI, whole game plays

    def progress_automated_actions(self) -> None:
        """Progress automated actions until no more automated actions exist or the game finishes."""
        while self.active_player.automated and not self.have_game_winner:
            self._logger.log(logging.DEBUG, 'performing next AI action')
            self.evaluate_active_player_actions()
            if len(self.active_player.legal_actions) > 0:
                self.do_next_action(self.active_player, self.active_player.select_action())

    def evaluate_active_player_actions(self) -> None:
        """Determine list of available actions for the active player."""
        self.active_player.evaluate_legal_actions(self.leading_card)

    def do_next_action(self, player: Player, action: Action) -> None:
        """Perform the action of the player."""
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.log(logging.DEBUG, 'Action %s, card %s, marriage %s, close deck: %s, swap_trump: %s',
                             player.name, str(action.card is not None), str(action.marriage is not None),
                             str(action.close_deck), str(action.swap_trump))

        play_card = None
        if action.swap_trump is True:
            self._swap_trump(player)

        if action.close_deck is True:
            self._close_deck(player)

        if action.marriage is not None:
            self._declare_marriage(player, action.marriage)

        if action.card is not None:
            play_card = self._play_card(player, action.card)

        if not self.have_game_winner and play_card is not None:
            if player is self.leading_player:
                self.leading_card = play_card
                self._call_back_hand_played()
                self.active_player = self.get_other_player(self.active_player)
            else:
                self.following_card = play_card
                self._call_back_hand_played()
                self._end_of_hand()

    def _call_back_hand_played(self) -> None:
        if self.on_event_callback_card_played is not None:
            self.on_event_callback_card_played()

    def _end_of_hand(self) -> None:
        self._hand_winner = self.leading_player
        if self.leading_card.suit == self.following_card.suit:
            if self.following_card.value > self.leading_card.value:
                self._hand_winner = self._following_player
        else:
            if self.following_card.suit == self.trump_card.suit:
                self._hand_winner = self._following_player

        loser = self.get_other_player(self._hand_winner)

        points = self.leading_card.value + self.following_card.value + self._award_marriage_points(self._hand_winner)

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

        if len(self._player_a.hand) == 0 and not self.have_game_winner:
            self._logger.debug('win by default')
            self.declare_game_win(self._hand_winner)

    def declare_game_win(self, player: Player) -> None:
        """Declare the game as over.

        This is typically called by a player who thinks they've won.

        Parameters
        ----------
        player : Player
            The Player declaring victory.
        """
        self.have_game_winner = True
        self.game_winner = player
        self._game_loser = self.get_other_player(self.game_winner)
        self._award_match_points()
        self._switch_deals_between_games()
        self._check_and_handle_match_win()

    def _check_and_handle_match_win(self) -> None:
        if self._player_a.match_points >= self.match_point_limit:
            self.match_winner = self._player_a
            self.have_match_winner = True
        if self._player_b.match_points >= self.match_point_limit:
            self.match_winner = self._player_b
            self.have_match_winner = True

    def _award_marriage_points(self, player: Player) -> int:
        """Award points for marriage as/if appropriate.

        Parameters
        ----------
        player : Player
            The Player in consideration.

        Returns
        -------
        int
            The number of points for the Marriage.
        """
        return_points = 0
        for marriage_info in self._marriages_info.values():
            marriage_player = marriage_info["player"]
            marriage = marriage_info["marriage"]
            if not marriage.points_awarded and player is marriage_player:
                marriage.points_awarded = True
                return_points += marriage.points
        return return_points   # Can be 0!

    def _declare_marriage(self, player: Player, marriage: Marriage) -> None:
        """Handle a player declaring a marriage.

        Player must be leader and immediate play a card form the marriage.
        Points for marriage only registered once any normal trick is won.
        If player declares 66 at this point, the game terminates immediately

        Parameters
        ----------
        player : Player
            The Player declaring the Marriage.
        marriage : Marriage
            The Marriage being declared.

        Raises
        ------
        ValueError
            If marriage is invalid.
        """
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Marriage declared by %s %s %s', player.name, marriage.queen, marriage.king)
        if player is not self.leading_player:
            raise ValueError('Invalid marriage - Only leading player can declare marriage')

        marriage.set_points(self.trump_card.suit)

        self._marriages_info[marriage.suit] = {
            "marriage": marriage,
            "player": player
        }

        # Award player points immediately if possible
        if player.game_points != 0:
            self._award_game_points(player, marriage.points)
            marriage.points_awarded = True

    def _play_card(self, player: Player, card: Card) -> None:
        for item, iter_card in enumerate(player.hand):
            if iter_card.value == card.value and \
                    iter_card.suit == card.suit:
                return player.hand.pop(item)
        raise Exception('Card not in hand')

    # Handle a player closing the deck
    # Said player must be current leader
    # calc points on offer
    def _close_deck(self, player: Player) -> None:
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Player closing deck %s', player)
        if self._deck_closed_by_player:
            raise Exception("Deck already closed")

        if player is not self.leading_player:
            raise Exception("non-leading player can't close deck")

        self.deck_closed = True
        self._deck_closed_by_player = True
        self._deck_closer = player
        self._deck_closer_points = self._calc_match_points_on_offer(player=player, closer=True)
        self._deck_non_closer_points = self._calc_match_points_on_offer(player=player, closer=False)

    def _swap_trump(self, player: Player) -> None:

        if self.deck_closed:
            raise Exception('Player can not swap trump as deck is closed')

        jack_of_trumps = Card(suit=self.trump_card.suit, value=Value.JACK)
        if player.hand.has_card(jack_of_trumps):
            jack_of_trumps = player.hand.pop_card(jack_of_trumps)
        else:
            raise Exception('Player can not swap trump as requisite card not in hand')

        player.receive_card(self.trump_card)
        self.trump_card = jack_of_trumps

    def _award_game_points(self, player: Player, points: int, cards: List[Card] = None) -> None:
        if cards is None:
            cards = []
        for iter_player in self._players:
            iter_player.notify_game_points_won(player, points, cards)

    def _award_match_points(self) -> None:

        if self._deck_closed_by_player:
            if self._deck_closer == self.game_winner:
                match_points = self._deck_closer_points
            else:
                match_points = self._deck_non_closer_points
        else:
            match_points = self._calc_match_points_on_offer(self.game_winner)

        for iter_player in self._players:
            iter_player.notify_match_points_won(self.game_winner, match_points)

    def _notify_players_of_trump(self, card: Card) -> None:
        for player in self._players:
            player.notify_trump(card)

    def _calc_match_points_on_offer(self, player: Player, closer: bool = True) -> None:
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

    def _switch_deals_between_games(self) -> None:

        tmp_player = self._player_with_1st_deal
        self._player_with_1st_deal = self._player_with_2nd_deal
        self._player_with_2nd_deal = tmp_player

    def _deal(self) -> None:

        self._give_cards(self._player_with_1st_deal, 3)
        self._give_cards(self._player_with_2nd_deal, 3)
        self.trump_card = self._deck.pop()
        self._give_cards(self._player_with_1st_deal, 2)
        self._give_cards(self._player_with_2nd_deal, 2)

        self._notify_players_of_trump(self.trump_card)

    # Assign leader at random
    # This could be prettier but it works..
    def _define_first_deal(self) -> None:
        self._player_with_1st_deal = self._player_a
        self._player_with_2nd_deal = self._player_a

        if random.choice([True, False]):
            self._player_with_1st_deal = self._player_b
        else:
            self._player_with_2nd_deal = self._player_b

    def _give_cards(self, player: Player, number: int) -> None:
        for _ in range(number):
            if len(self._deck) == 0 and number == 1:
                self.deck_closed = True
                player.receive_card(self.trump_card)
            else:
                player.receive_card(self._deck.pop())

    def get_other_player(self, player: Player) -> Player:
        """Returns the second Player instance.

        Parameters
        ----------
        player : Player
            The first Player instance.

        Returns
        -------
        Player
            The second Player instance.
        """
        return self._player_b if player is self._player_a else self._player_a
