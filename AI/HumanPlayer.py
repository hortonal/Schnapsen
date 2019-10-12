from Game.Player import Player

class HumanPlayer(Player):

    def __init__(self, name='Huuuman'):
        super().__init__(name)
        self.type = Player.type_human

# In this case no implementation of select action is necessary
# all actions are input via UI