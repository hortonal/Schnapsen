from SimpleGame.SimplePlayer import SimplePlayer


class SimpleHumanPlayer(SimplePlayer):

    def __init__(self, name='Huuuman'):
        super().__init__(name=name, automated=False)
