class CardInput:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.in_my_hand = False
        self.in_opponent_hand = False
        self.won_by_me = False
        self.won_by_opponent = False
        self.is_leading_card = False

