"""Parent player class.

All player implementation should inherit from this and simply implement the
_select_action method to notify the game what it's doing. All other player logic
and game controller interaction handled in this class.
"""
from __future__ import annotations

from typing import List

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Value
from schnapsen.core.hand import Hand


class Player:
    """Parent player class.

    This should generally be inherited from.
    """

    def __init__(self, name: str, automated: bool = True, requires_model_load: bool = False) -> None:
        """Initialise Player.

        Parameters
        ----------
        name : str
            Print friendly name.
        automated : bool, optional
            True if AI/Bot, False otherwise, by default True
        requires_model_load : bool, optional
            If True attempt to load model before using (e.g. for AI models), by default False
        """
        self.name = name
        self.automated = automated
        self.requires_model_load = requires_model_load
        self.hand = Hand()
        self.cards_won = []
        self.match_points = 0
        self.game_points = 0
        self.opponent_hand = []  # This is for keeping track of cards we know the opponent definitely has
        self.opponent_cards_won = []
        self.opponent_match_points = 0
        self.opponent_game_points = 0
        self.game = None  # Assigned by game controller
        self._trump = None
        self.legal_actions = []

    def select_action(self) -> Action:
        """Method for selecting Player Action.

        A child player class must implement this method and return an action. The player or some other controller
        should probably first ask for the legal actions to evaluated (but an illegal action is handled by the
        game controller).

        Returns
        -------
        Action
            The selected game Action.
        """
        raise Exception('Must be implemented by child')

    def reset_for_new_match(self) -> None:
        """Prepare a player for next match."""
        self.match_points = 0
        self.opponent_match_points = 0
        self.reset_for_new_game()

    def reset_for_new_game(self) -> None:
        """Prepare a player for next game."""
        self.hand = Hand()
        self.cards_won = []
        self.game_points = 0
        self.opponent_hand = []
        self.opponent_cards_won = []
        self.opponent_game_points = 0
        self._trump = None

    def receive_card(self, card: Card) -> None:
        """Receive a card into a hand. Typically while dealing."""
        self.hand.append(card)

    def notify_trump(self, card: Card) -> None:
        """Notify the player which card is Trump.

        TODO: This should be deduced from game state.
        """
        self._trump = card

    def notify_game_points_won(self, player: Player, points: int, cards: List[Card] = None) -> None:
        """Notify player that a single hand has been won.

        Parameters
        ----------
        player : Player
            The player that won the single hand.
        points : int
            The points won by the hand.
        cards : List[Card], optional
            The cards won by the player, by default None
        """
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

    def notify_match_points_won(self, player: Player, points: int) -> None:
        """Notify Player of match points won.

        Parameters
        ----------
        player : Player
            The winning Player.
        points : int
            The number of points won.
        """
        if player is self:
            self.match_points += points
        else:
            self.opponent_match_points += points

    def _check_and_declare_win(self) -> None:
        # Check to see if we have enough points to declare a victory.
        if self._enough_points():
            self.game.declare_game_win(self)

    def _enough_points(self) -> None:
        return self.game_points >= self.game.game_point_limit

    def has_cards_left(self) -> None:
        """Check if hand is empty."""
        return len(self.hand) != 0

    def evaluate_legal_actions(self, opponents_card: Card) -> List[Action]:  # noqa: C901 (it's complex still...)
        """Check what legal actions are available.

        TODO: Make this less ugly...

        Parameters
        ----------
        opponents_card : Card
            The Card played by the opponent, or None if our move.
        """
        legal_actions = []

        if opponents_card is None:
            if self.hand.has_card(Card(self._trump.suit, Value.JACK)) and not self.game.deck_closed:
                legal_actions.append(Action(swap_trump=True))

            if not self.game.deck_closed:
                legal_actions.append(Action(close_deck=True))

            marriages = self.hand.available_marriages()
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

    def _print_str_name(self) -> str:
        return self.name

    def __repr__(self) -> str:
        """String format.

        Returns
        -------
        str
            Object as str.
        """
        return self._print_str_name()

    def __str__(self) -> str:
        """String format.

        Returns
        -------
        str
            Object as str.
        """
        return self._print_str_name()
