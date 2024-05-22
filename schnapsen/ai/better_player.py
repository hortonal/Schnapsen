"""A slightly better player implementation."""
from schnapsen.core.action import Action
from schnapsen.core.player import Player


class BetterPlayer(Player):
    """A player with rudimentary logic."""

    def select_action(self) -> Action:
        """Select a legal action."""
        selected_action = None

        # Swap trump if we can - rarely is this a bad decision.
        for action in self.legal_actions:
            if action.swap_trump is True:
                selected_action = action
                break

        # Close the deck for shits
        for action in self.legal_actions:
            if action.close_deck is True and self.game_points > 50:
                selected_action = action
                break

        # Declare and play a marriage if we can. It's usually worth doing this whenever possible.
        if selected_action is None:
            for action in self.legal_actions:
                if action.marriage is not None:
                    selected_action = action
                    break

        if selected_action is None and self.game.leading_player:
            selected_action = self._decide_leader_action()
        if selected_action is None and not self.game.leading_player:
            selected_action = self._decide_follower_action()

        assert selected_action is not None, 'No action selected!'

        return selected_action

    def _decide_leader_action(self) -> Action:
        """If we're leading, figure out a sensible play.

        A simple thing to do is try and play the highest card.

        Some considerations:
        - Don't break a marriage (this shouldn't be a problem as marriages are played as a priority)
        - Leading trumps is questionable at best...

        Returns
        -------
        Action
            The selection action.
        """
        # Play highest card if leader
        selected_action = None
        highest_card_value = 0
        for action in self.legal_actions:
            if (action.card is not None) and (action.card.value > highest_card_value):
                highest_card_value = action.card.value
                selected_action = action
        return selected_action

    def _decide_follower_action(self) -> Action:
        selected_action = None
        lowest_card_value = 100
        for action in self.legal_actions:
            # Which legal actions result in win? Pick the cheapest one. I.e. lowest card winner, not a trump etc.

            # Else discard the lowest card that's not in a marriage (unless 10/Ace?)
            if (action.card is not None) and (action.card.value < lowest_card_value):
                lowest_card_value = action.card.value
                selected_action = action
        return selected_action
