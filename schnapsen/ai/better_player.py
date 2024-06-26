"""A slightly better player implementation."""
from typing import List

from schnapsen.core.action import Action
from schnapsen.core.player import Player
from schnapsen.core.state import MatchState


class BetterPlayer(Player):
    """A player with rudimentary logic."""

    def select_action(self, state: MatchState, legal_actions: List[Action]) -> Action:
        """Select legal action.

        Args:
            state (MatchState): Current game state.
            legal_actions (List[Action]): Current legal actions.

        Returns:
            Action: A selected action.
        """
        selected_action = None

        # Swap trump if we can - rarely is this a bad decision.
        for action in legal_actions:
            if action.swap_trump is True:
                selected_action = action
                break

        # Declare and play a marriage if we can. It's usually worth doing this whenever possible.
        # Whether we play the king or queen should depend on if we think we'll win the hand or not.
        if selected_action is None:
            for action in legal_actions:
                if action.declare_marriage:
                    selected_action = action
                    break

        if selected_action is None and (state.leading_player is self):
            selected_action = self._decide_leader_action(legal_actions=legal_actions)
        if selected_action is None and not (state.leading_player is self):
            selected_action = self._decide_follower_action(state=state, legal_actions=legal_actions)

        assert selected_action is not None, 'Player must select an action.'

        return selected_action

    def _decide_leader_action(self, legal_actions: List[Action]) -> Action:
        """If we're leading, figure out a sensible play.

        A simple thing to do is try and play the highest card.

        Some considerations:
        - Don't break a marriage (this shouldn't be a problem as marriages are played as a priority)
        - Leading trumps is questionable at best...

        Args:
            legal_actions (List[Action]): Current legal actions.

        Returns:
            Action: The selected action.
        """
        # Play highest card if leader
        selected_action = None
        highest_card_value = 0
        for action in legal_actions:
            if (action.card is not None) and (action.card.value > highest_card_value):
                highest_card_value = action.card.value
                selected_action = action
        return selected_action

    def _decide_follower_action(self, state: MatchState, legal_actions: List[Action]) -> Action:
        # Following actions are all card plays which simplifies things. Try and win the hand if we can.
        selected_action = None
        lowest_action_value = 1000
        leading_card = state.leading_card
        trump_suit = state.trump_card.suit
        winning_actions = []

        for action in legal_actions:
            # Can I win this hand?
            if action.card.suit == leading_card.suit and action.card.value > leading_card.value:
                winning_actions.append(action)

            # Else trumps could we play.
            if action.card.suit == trump_suit and action.card.suit == leading_card.suit:
                winning_actions.append(action)

        # If we can win, let's play the "cheapest" winning action
        if len(winning_actions) > 0:
            for action in winning_actions:
                action_value = 10 * action.card.value if action.card.suit == trump_suit else action.card.value
                if action_value < lowest_action_value:
                    lowest_action_value = action_value
                    selected_action = action
        # We can't win, so discard the cheapest action (avoiding trumps!)
        else:
            for action in legal_actions:
                action_value = 10 * action.card.value if action.card.suit == trump_suit else action.card.value
                if action_value < lowest_action_value:
                    lowest_action_value = action_value
                    selected_action = action

        return selected_action
