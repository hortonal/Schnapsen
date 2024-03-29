"""Main file (test for now)"""
import logging
import sys
import Game.GameHelpers as GameHelpers
from Game.Game import Game
from AI.RandomPlayer import RandomPlayer
from AI.BetterPlayer import BetterPlayer
from AI.HumanPlayer import HumanPlayer
from AI.NeuralNetwork.SimpleLinear.NNSimpleLinearPlayer import NNSimpleLinearPlayer
from GUI.GUI import GUI

if __name__ == "__main__":

    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.debug('Starting main')

    betty = BetterPlayer
    randy = RandomPlayer
    human = HumanPlayer
    nanny = NNSimpleLinearPlayer
#    nanny = NeuralNetwork

    player1 = human()
    # player1 = nanny()
    # player1 = randy()
    player2 = nanny()

    human = None
    for player in [player1, player2]:
        if type(player) is HumanPlayer:
            human = player
        if player.requires_model_load:
            player.load_model()

    player1_wins = 0
    player2_wins = 0

    game = Game(player1, player2)

    if human is not None:
        human.UI = GUI(game, human)
        human.UI.mainloop()

    else:
        GameHelpers.play_automated_games(game, 1000)
