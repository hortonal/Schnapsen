"""Main file (test for now)"""
import logging
import sys
import Game.GameHelpers as GameHelpers
from Game.Game import Game
from AI.RandomPlayer import RandomPlayer
from AI.BetterPlayer import BetterPlayer
from AI.HumanPlayer import HumanPlayer
#from AI.NNSimple import NNSimple
from GUI.GUI import GUI

if __name__ == "__main__":

    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.debug('Starting main')

    betty = BetterPlayer
    randy = RandomPlayer
    human = HumanPlayer
#    nanny = NeuralNetwork

    player1 = human()
    # player1 = nanny()
    # player1 = randy()
    player2 = betty()
    player1_wins = 0
    player2_wins = 0

    game = Game(player1, player2)

    human = None
    if type(player2) is HumanPlayer:
        human = player2
    if type(player1) is HumanPlayer:
        human = player1
    if human is not None:
        human.UI = GUI(game, human)
        human.UI.mainloop()

    else:
        GameHelpers.play_automated_games(game, 1000)
