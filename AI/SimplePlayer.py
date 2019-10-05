
class SimplerPlayer:

    def __init__(self, name='default'):
        self.name = name
        self.hand = []
        self.is_leader = False
        self.match_points = 0
        self.game_points = 0
        self.game = None
        return

    def receive_card(self, card):
        self.hand.append(card)

    def play(self, opponents_card=None):

        declare_marriage = False
        return_card = self._choose_card()

        return return_card

    def notify_hand_won(self, points):
        self.game_points += points
        self.check_and_declare_win()

    def declare_marriage(self):

        self.game.declare_marriage()
        self.check_and_declare_win()

    def check_and_declare_win(self):
        if self.enough_points():
            self.game.declare_win(self)

    def enough_points(self):
        return self.game_points >= 66

    def has_cards_left(self):
        return len(self.hand) != 0

    # Logic to be implemented
    def _choose_card(self):
        #Play one at random for now...
        return self.hand.pop()

    def _print_str_name(self):
        return "SimplerPlayer: " + self.name

    def __repr__(self):
        return self._print_str_name()

    def __str__(self):
        return self._print_str_name()
