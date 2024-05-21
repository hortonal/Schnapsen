"""A slightly better player implementation."""
from schnapsen.core.action import Action
from schnapsen.core.player import Player


class BetterPlayer(Player):
    """A player with rudimentary logic."""

    def select_action(self) -> Action:   # noqa: C901
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

        # Declare marriage and play queen if we can
        if selected_action is None:
            for action in self.legal_actions:
                if action.marriage is not None:
                    selected_action = action
                    break

        if self.game.leading_player is self:
            # Play highest card if leader
            highest_card_value = 0
            if selected_action is None:
                for action in self.legal_actions:
                    if (action.card is not None) and (action.card.value > highest_card_value):
                        highest_card_value = action.card.value
                        selected_action = action
        else:
            # Can I win hand? Why wouldn't I want to?
            # Play lowest card if follower
            lowest_card_value = 100
            if selected_action is None:
                for action in self.legal_actions:
                    if (action.card is not None) and (action.card.value < lowest_card_value):
                        lowest_card_value = action.card.value
                        selected_action = action

        if selected_action is None:
            raise ValueError('No action selected!')

        return selected_action
