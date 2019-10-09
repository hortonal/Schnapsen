from Game.Player import Player

class SimplerPlayer(Player):

    def __init__(self, name='default'):
        super().__init__(name)

    def _select_action(self, legal_actions):

        selected_action = None

        # Swap trump if we can
        for action in legal_actions:
            if action.swap_trump is True:
                selected_action = action
                break

        # Close the deck for shits
        for action in legal_actions:
            if action.close_deck is True and self.game_points > 50:
                selected_action = action
                break

        # Declare marriage and play queen if we can
        if selected_action is None:
            for action in legal_actions:
                if action.marriage is not None:
                    selected_action = action
                    break

        # Else play highest card
        highest_card_value = 0
        if selected_action is None:
            for action in legal_actions:
                if action.card is not None:
                    if action.card.value > highest_card_value:
                        highest_card_value = action.card.value
                        selected_action = action

        if selected_action is None:
            raise Exception('Pick an action fuck-wit')

        return selected_action
