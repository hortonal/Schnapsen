from Game.Player import Player


class BetterPlayer(Player):

    def __init__(self, name='Betty'):
        super().__init__(name)

    def select_action(self):

        selected_action = None

        # Swap trump if we can
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
                    if action.card is not None:
                        if action.card.value > highest_card_value:
                            highest_card_value = action.card.value
                            selected_action = action
        else:
            # Can I win hand? Why wouldn't I want to?
            # Play lowest card if follower
            lowest_card_value = 100
            if selected_action is None:
                for action in self.legal_actions:
                    if action.card is not None:
                        if action.card.value < lowest_card_value:
                            lowest_card_value = action.card.value
                            selected_action = action

        if selected_action is None:
            raise Exception('Pick an action fuck-wit')

        return selected_action
