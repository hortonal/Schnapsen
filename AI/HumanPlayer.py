from Game.Player import Player


class HumanPlayer(Player):

    def __init__(self, name='Huuuman'):
        super().__init__(name=name, automated=False)
        self.type = Player.type_human
