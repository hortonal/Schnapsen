

class Card:

    # Cards
    Ten = 10
    Jack = 2
    Queen = 3
    King = 4
    Ace = 11

    # Suits
    Spades = 0
    Clubs = 1
    Hearts = 2
    Diamonds = 3
    Back = 4  # Special suit for GUI
    Empty = 5  # Special suit for GUI

    Values = {
        Ten: 'Ten',
        Jack: 'Jack',
        Queen: 'Queen',
        King: 'King',
        Ace: 'Ace'}

    Suits = {
        Spades: 'Spades',
        Clubs: 'Clubs',
        Hearts: 'Hearts',
        Diamonds: 'Diamonds'}

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def _print_str_name(self):
        return self.Values[self.value] + ' ' + self.Suits[self.suit]

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Card):
            return self.suit == other.suit and self.value == other.value
        return NotImplemented

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented