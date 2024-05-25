"""Parent player class.

All player implementation should inherit from this and simply implement the
_select_action method to notify the game what it's doing. All other player logic
and game controller interaction handled in this class.
"""
from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

from schnapsen.core.action import Action
from schnapsen.core.card import Card
from schnapsen.core.card import Value
from schnapsen.core.hand import Hand

if TYPE_CHECKING:
    from schnapsen.core.state import PublicMatchState
    from schnapsen.core.state import PublicRoundState


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
        # Not critical but useful for logging/UI.
        self.name = name
        # Used for AI players to progress actions automatically when possible.
        self.automated = automated
        # Used for model based players alongside a load_model method on the player.
        # TODO: make ModelPlayer child of the Player object and replace this bool with a simple isinstance check.
        self.requires_model_load = requires_model_load
        # Track the player's current hand. This could/should also be tracked by the match controller but it's cleaner
        # for a player to own his hand.
        self.hand = Hand()
        # Allow a player to access public game state.
        self.round_state: PublicRoundState = None  # Assigned by game controller, contains public round state
        self.match_state: PublicMatchState = None  # Assigned by game controller, contains public match state
        self.declare_win_callback: Callable = None  # Assigned by game controller. This is used but isn't necessary
        # Track the current set of legal actions.
        self.legal_actions: List[Action] = []
        # Track game state independently of the match controller.
        # TODO: If we're assuming bots have good memory of previous match state, we should remove these in favour of
        # using the public state objects above.
        self.cards_won = []
        self.match_points = 0
        self.round_points = 0
        self.opponent_hand = []  # This is for keeping track of cards we know the opponent definitely has
        self.opponent_cards_won = []
        self.opponent_match_points = 0
        self.opponent_round_points = 0
        self._trump = None

    def select_action(self) -> Action:
        """Method for selecting Player Action.

        A child player class must implement this method and return an action. The player or some other controller
        should probably first ask for the legal actions to evaluated (but an illegal action is handled by the
        game controller).

        Returns
        -------
        Action
            The selected game Action.

        Raises
        ------
        NotImplementedError
            If a child object fails to implement this necessary method.
        """
        raise NotImplementedError('Must be implemented by child')

    def new_round(self) -> None:
        """Prepare a player for next round."""
        self.hand = Hand()
        self.cards_won = []
        self.round_points = 0
        self.opponent_hand = []
        self.opponent_cards_won = []
        self.opponent_round_points = 0
        self._trump = None

    def receive_card(self, card: Card) -> None:
        """Receive a card into a hand. Typically while dealing."""
        self.hand.append(card)

    def notify_trump(self, card: Card) -> None:
        """Notify the player which card is Trump.

        TODO: This should be deduced from game state.
        """
        self._trump = card

    def notify_round_points_won(self, winning_player: Player, points: int, cards: List[Card] = None) -> None:
        """Notify player that a single hand has been won.

        Parameters
        ----------
        winning_player : Player
            The player that won the single hand.
        points : int
            The points won by the hand.
        cards : List[Card], optional
            The cards won by the player, by default None
        """
        if winning_player is self:
            self.round_points += points
            # After we get awarded points, immediately see if we can terminate the round.
            self._check_and_declare_win()
            self.cards_won.extend(cards)

        else:
            self.opponent_round_points += points
            self.opponent_cards_won.extend(cards)

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
            self.declare_win_callback(self)

    def _enough_points(self) -> None:
        return self.round_points >= self.match_state.round_point_limit

    def evaluate_legal_actions(self, leading_card: Card) -> List[Action]:
        """Determine the set of legal actions.

        TODO: Reduce complexity.

        Parameters
        ----------
        leading_card : Card
            The Card played by the opponent, or None if it's the current player's lead.
        """
        legal_actions = []

        if leading_card is None:
            legal_actions.extend(self._legal_leading_actions())
        else:
            legal_actions.extend(self._legal_follower_actions(leading_card=leading_card))

        self.legal_actions = legal_actions

    def _legal_leading_actions(self) -> List[Action]:
        legal_actions = []

        if self.hand.has_card(Card(self._trump.suit, Value.JACK)) and not self.round_state.deck_closed:
            legal_actions.append(Action(swap_trump=True))

        if not self.round_state.deck_closed:
            legal_actions.append(Action(close_deck=True))

        marriages = self.hand.available_marriages()
        for marriage in marriages:
            legal_actions.append(Action(card=marriage.queen,
                                        marriage=marriage))
            legal_actions.append(Action(card=marriage.king,
                                        marriage=marriage))
        for card in self.hand:
            legal_actions.append(Action(card=card))
        return legal_actions

    def _legal_follower_actions(self, leading_card: Card) -> List[Action]:
        legal_actions = []
        furhter_legal_actions_exist = True
        # Handle special rules around a closed deck first.
        if self.round_state.deck_closed:
            # If deck closed, player must follow suit and win if possible
            for card in self.hand.cards_of_same_suit(suit=leading_card.suit, greater_than=leading_card.value):
                legal_actions.append(Action(card=card))
                furhter_legal_actions_exist = False

            # Player must follow suit if they can't win
            if furhter_legal_actions_exist:
                for card in self.hand.cards_of_same_suit(suit=leading_card.suit):
                    legal_actions.append(Action(card=card))
                    furhter_legal_actions_exist = False

            # Player must trump if they can't follow suit
            if furhter_legal_actions_exist:
                for card in self.hand.cards_of_same_suit(suit=self._trump.suit):
                    legal_actions.append(Action(card=card))
                    furhter_legal_actions_exist = False

        # Failing the above, player can play any card.
        if furhter_legal_actions_exist:
            [legal_actions.append(Action(card=card)) for card in self.hand]

        return legal_actions

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
