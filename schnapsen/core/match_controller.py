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
from schnapsen.core.state import PublicMatchState
from schnapsen.core.state import PublicRoundState


class MatchController:
    """Core game controller object."""

    def __init__(self, player_a: Player, player_b: Player,
                 match_point_limit: int = 7, round_point_limit: int = 66) -> None:
        """Create a GameController instance.

        Parameters
        ----------
        player_a : Player
            The first Player.
        player_b : Player
            The opponent.
        match_point_limit : int, optional
            The number of game points required to win a match, by default 7
        round_point_limit : int, optional
            The number of points required to win a game, by default 66
        """
        self._logger = logging.getLogger()
        self._round_point_limit = round_point_limit
        self._match_point_limit = match_point_limit
        self._player_a = player_a
        self._player_b = player_b
        self._players = [player_a, player_b]
        self._deck = None   # will be defined when game starts.
        self.on_event_callback_card_played = None  # Func set externally for event handling, e.g. in a GUI.

    def new_match(self) -> None:
        """Start a new match."""
        self.match_state = PublicMatchState(
            round_point_limit=self._round_point_limit,
            match_point_limit=self._match_point_limit
        )
        for player in self._players:
            player.match_points = 0
            player.match_state = self.match_state
            player.declare_win_callback = self.declare_game_win

        self._define_first_deal()
        self.match_state.match_winner = None
        self.match_state.have_match_winner = False

    def new_round(self, deck: Deck = None) -> None:
        """Start a new game within match.

        Parameters
        ----------
        deck : Deck, optional
            Provide the game with a deck. This is mostly for testing, by default None
        """
        self.round_state = PublicRoundState()
        for player in self._players:
            player.round_state = self.round_state
            player.new_round()
        self._marriages_info = {}

        if deck is None:
            self._deck = Deck()
            self._deck.shuffle()
        else:
            self._deck = deck
        self._deal()
        self.round_state.leading_player = self.match_state.player_with_1st_deal
        self.round_state.following_player = self.get_other_player(self.round_state.leading_player)
        self.round_state.active_player = self.round_state.leading_player

    def play_automated_match(self) -> None:
        """Progress match/game state automatically."""
        self.new_match()
        while not self.match_state.have_match_winner:
            self.new_round()
            while not self.round_state.have_round_winner:
                self.progress_automated_actions()  # If AI vs. AI, whole game plays

    def progress_automated_actions(self) -> None:
        """Progress automated actions until no more automated actions exist or the game finishes."""
        active_player = self.round_state.active_player
        while active_player.automated and not self.round_state.have_round_winner:
            self._logger.log(logging.DEBUG, 'performing next AI action')
            self.evaluate_active_player_actions()
            if len(active_player.legal_actions) > 0:
                self.do_next_action(active_player.select_action())
            # Active player can be updated after each action!
            active_player = self.round_state.active_player

    def evaluate_active_player_actions(self) -> None:
        """Determine list of available actions for the active player."""
        self.round_state.active_player.evaluate_legal_actions(self.round_state.leading_card)

    def do_next_action(self, action: Action) -> None:
        """Perform the action of the player."""
        player = self.round_state.active_player
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

        if not self.round_state.have_round_winner and play_card is not None:
            if player is self.round_state.leading_player:
                self.round_state.leading_card = play_card
                self._call_back_hand_played()
                self.round_state.active_player = self.get_other_player(self.round_state.active_player)
            else:
                self.round_state.following_card = play_card
                self._call_back_hand_played()
                self._end_of_hand()

    def _call_back_hand_played(self) -> None:
        if self.on_event_callback_card_played is not None:
            self.on_event_callback_card_played()

    def _end_of_hand(self) -> None:
        self.round_state.hand_winner = self.round_state.leading_player
        if self.round_state.leading_card.suit == self.round_state.following_card.suit:
            if self.round_state.following_card.value > self.round_state.leading_card.value:
                self.round_state.hand_winner = self.round_state.following_player
        else:
            if self.round_state.following_card.suit == self.round_state.trump_card.suit:
                self.round_state.hand_winner = self.round_state.following_player

        loser = self.get_other_player(self.round_state.hand_winner)

        points = self.round_state.leading_card.value + self.round_state.following_card.value \
            + self._award_marriage_points(self.round_state.hand_winner)

        self._award_game_points(self.round_state.hand_winner, points,
                                [self.round_state.leading_card, self.round_state.following_card])

        self._logger.debug(self.round_state.hand_winner.name + ' wins')

        # Deal extra cards, winner first
        if not self.round_state.deck_closed:
            self._give_cards(self.round_state.hand_winner, 1)
            self._give_cards(loser, 1)

        # Set winner to leading player
        self.round_state.leading_card = None
        self.round_state.following_card = None
        self.round_state.leading_player = self.round_state.hand_winner
        self.round_state.active_player = self.round_state.leading_player
        self.round_state.following_player = loser

        if len(self._player_a.hand) == 0 and not self.round_state.have_round_winner:
            self._logger.debug('win by default')
            self.declare_game_win(self.round_state.hand_winner)

    def declare_game_win(self, player: Player) -> None:
        """Declare the game as over.

        This is typically called by a player who thinks they've won.

        Parameters
        ----------
        player : Player
            The Player declaring victory.
        """
        self.round_state.have_round_winner = True
        self.round_state.round_winner = player
        self.round_state.round_loser = self.get_other_player(player)
        self._award_match_points()
        self._switch_deals_between_games()
        self._check_and_handle_match_win()

    def _check_and_handle_match_win(self) -> None:
        if self.match_state.player_a_match_points >= self.match_state.match_point_limit:
            self.match_state.match_winner = self._player_a
            self.match_state.have_match_winner = True
        if self.match_state.player_b_match_points >= self.match_state.match_point_limit:
            self.match_state.match_winner = self._player_b
            self.match_state.have_match_winner = True

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
        if player is not self.round_state.leading_player:
            raise ValueError('Invalid marriage - Only leading player can declare marriage')

        marriage.set_points(self.round_state.trump_card.suit)

        self._marriages_info[marriage.suit] = {
            "marriage": marriage,
            "player": player
        }

        # Award player points immediately if possible
        if player.round_points != 0:
            self._award_game_points(player, marriage.points)
            marriage.points_awarded = True

    def _play_card(self, player: Player, card: Card) -> None:
        for idx, card_in_hand in enumerate(player.hand):
            if card_in_hand == card:
                return player.hand.pop(idx)
        raise ValueError('Card not in hand')

    # Handle a player closing the deck
    # Said player must be current leader
    # calc points on offer
    def _close_deck(self, player: Player) -> None:
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug('Player closing deck %s', player)
        if self.round_state.deck_closed_by_player:
            raise Exception("Deck already closed")

        if player is not self.round_state.leading_player:
            raise Exception("non-leading player can't close deck")

        self.round_state.deck_closed = True
        self.round_state.deck_closed_by_player = True
        self.round_state.deck_closer = player
        self.round_state.deck_closer_points = self._calc_match_points_on_offer(player=player, closer=True)
        self.round_state.deck_non_closer_points = self._calc_match_points_on_offer(player=player, closer=False)

    def _swap_trump(self, player: Player) -> None:

        if self.round_state.deck_closed:
            raise ValueError('Player can not swap trump as deck is closed')

        jack_of_trumps = Card(suit=self.round_state.trump_card.suit, value=Value.JACK)
        if player.hand.has_card(jack_of_trumps):
            player.hand.pop_card(jack_of_trumps)
        else:
            raise ValueError('Player can not swap trump as requisite card not in hand')

        player.receive_card(self.round_state.trump_card)
        self.round_state.trump_card = jack_of_trumps

    def _award_game_points(self, player: Player, points: int, cards: List[Card] = None) -> None:
        if cards is None:
            cards = []
        for iter_player in self._players:
            iter_player.notify_game_points_won(player, points, cards)

    def _award_match_points(self) -> None:
        """Notify players of their points, and keep track of them in the game controller, too."""
        if self.round_state.deck_closed_by_player:
            if self.round_state.deck_closer == self.round_state.round_winner:
                match_points = self.round_state.deck_closer_points
            else:
                match_points = self.round_state.deck_non_closer_points
        else:
            match_points = self._calc_match_points_on_offer(self.round_state.round_winner)

        # Update our own records
        if self.round_state.round_winner is self._player_a:
            self.match_state.player_a_match_points += match_points
        else:
            self.match_state.player_b_match_points += match_points

        # Notify Player objects
        for iter_player in self._players:
            iter_player.notify_match_points_won(self.round_state.round_winner, match_points)

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
        if other_player.round_points == 0:
            match_points = 3
        elif other_player.round_points < 33:
            match_points = 2

        return match_points

    def _switch_deals_between_games(self) -> None:
        self.match_state.player_with_1st_deal = self.match_state.player_with_2nd_deal
        self.match_state.player_with_2nd_deal = self.get_other_player(self.match_state.player_with_1st_deal)

    def _deal(self) -> None:
        player_a = self.match_state.player_with_1st_deal
        player_b = self.match_state.player_with_2nd_deal
        self._give_cards(player_a, 3)
        self._give_cards(player_b, 3)
        self.round_state.trump_card = self._deck.pop()
        self._give_cards(player_a, 2)
        self._give_cards(player_b, 2)

        self._notify_players_of_trump(self.round_state.trump_card)

    # Assign leader at random
    # This could be prettier but it works..
    def _define_first_deal(self) -> None:
        random_player = random.choice(self._players)
        self.match_state.player_with_1st_deal = random_player
        self.match_state.player_with_2nd_deal = self.get_other_player(random_player)

    def _give_cards(self, player: Player, number: int) -> None:
        for _ in range(number):
            # Giving out the trump card is a special case when the face down deck is finished
            if len(self._deck) == 0 and number == 1:
                self.round_state.deck_closed = True
                player.receive_card(self.round_state.trump_card)
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
