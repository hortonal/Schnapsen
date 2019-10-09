"""Simple object to hold possible actions"""

class Action:

    def __init__(self, card=None, marriage=None, swap_trump=False, close_deck=False):
        self.card = card
        self.marriage = marriage
        self.swap_trump = swap_trump
        self.close_deck = close_deck

    def _print_str_name(self):
        return_string = ''
        if self.swap_trump:
            return_string = 'Swap trump '

        if self.close_deck:
            return_string += 'Close Deck '

        if self.marriage is not None:
            return_string += 'Play marriage '

        if self.card is not None:
            return_string += 'Play card ' + str(self.card)

        return return_string

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()
